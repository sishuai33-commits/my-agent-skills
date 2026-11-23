"""Offline schema/year/valuation regressions; all network paths are stubs."""
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import pandas as pd
import urllib.request
from test_markdown_functions import load_function


class ValuationContractTests(unittest.TestCase):
    def table(self, current=1, following=1):
        return pd.DataFrame({'年度': ['2031年', '2030年'], '预测机构数': [4, 3],
                             '最小值': [0.1, 0.2], '均值': [following, current], '最大值': [9, 9]})

    def valuation(self, table):
        fields = [''] * 53
        fields[1], fields[3], fields[44] = 'fixture', '60', '100'
        raw = ('v_sh600000="' + '~'.join(fields) + '";').encode('gbk')
        ns = {'math': math, 'pd': pd, 'ths_eps_forecast': lambda code: table,
              'urllib': SimpleNamespace(request=SimpleNamespace(Request=urllib.request.Request,
                    urlopen=lambda *a, **k: SimpleNamespace(read=lambda: raw)))}
        for name in ['forward_pe', 'pe_digestion', 'calc_peg', 'full_valuation']:
            load_function(name, ns)
        return ns['full_valuation']('600000', forecast_year=2030)

    def test_mean_and_explicit_year_not_minimum_or_row_order(self):
        result = self.valuation(self.table(3, 6))
        self.assertEqual((result['eps_cur'], result['eps_next'], result['analyst_count']), (3, 6, 3))
        self.assertEqual(result['pe_fwd'], 20)
        self.assertEqual(result['digest_years'], 0)

    def test_high_pe_without_growth_is_not_zero_years(self):
        result = self.valuation(self.table(1, 1))
        self.assertEqual(result['cagr_pct'], 0)
        self.assertIsNone(result['digest_years'])
        self.assertEqual(result['digest_status'], '不可消化')

    def test_invalid_eps_or_missing_year_remains_unknown(self):
        tables = [self.table(0, 1), self.table(float('nan'), 1), self.table(1, 1).iloc[:1]]
        for table in tables:
            with self.subTest(table=table.to_dict()):
                result = self.valuation(table)
                self.assertIsNotNone(result['forecast_error'])
                self.assertIsNone(result['digest_years'])
                self.assertEqual(result['digest_status'], '未计算')

    def forecast(self, tables):
        ns = {'pd': pd, 'requests': SimpleNamespace(get=lambda *a, **k: SimpleNamespace(
            text='<html/>', encoding=None, raise_for_status=lambda: None))}
        fn = load_function('ths_eps_forecast', ns)
        with patch.object(pd, 'read_html', return_value=tables):
            return fn('600000')

    def test_unrelated_first_table_never_becomes_eps(self):
        with self.assertRaises(ValueError):
            self.forecast([self.table()])  # no explicit EPS identity

    def test_explicit_eps_headers_are_normalized(self):
        df = self.table()
        df.columns = pd.MultiIndex.from_tuples([('每股收益预测', c) for c in df.columns])
        result = self.forecast([pd.DataFrame({'other': [1]}), df])
        self.assertEqual(list(result.columns), ['年度', '预测机构数', '均值'])
        self.assertEqual(result.iloc[1]['均值'], 1)

    def test_ambiguous_mean_columns_fail_closed(self):
        df = self.table()
        df['平均值'] = 2
        df.columns = pd.MultiIndex.from_tuples([('每股收益预测', c) for c in df.columns])
        with self.assertRaises(ValueError):
            self.forecast([df])


if __name__ == '__main__':
    unittest.main()
