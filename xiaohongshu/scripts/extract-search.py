import argparse
import sys


def main():
    sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=20, help='max items in this slice')
    parser.add_argument('--offset', type=int, default=0, help='offset in the currently loaded cumulative feeds')
    args = parser.parse_args()
    if args.limit <= 0 or args.offset < 0:
        parser.error('--limit must be positive and --offset must be nonnegative')

    js = f"""
(function() {{
  try {{
    const unwrap = v => v?.value !== undefined ? v.value : v?._value !== undefined ? v._value : v;
    const feeds = unwrap(window.__INITIAL_STATE__?.search?.feeds);
    if (!feeds || !feeds.length) {{
      return JSON.stringify({{ error: true, message: 'feeds not loaded or empty — verify page is a search result page and wait stable has completed' }});
    }}
    const s = window.__INITIAL_STATE__?.search;
    const items = feeds.slice({args.offset}, {args.offset + args.limit}).map(item => {{
      const nc = unwrap(item?.noteCard);
      const user = unwrap(nc?.user);
      const interact = unwrap(nc?.interactInfo);
      const cover = unwrap(nc?.cover);
      return {{
        id: unwrap(item?.id),
        xsecToken: unwrap(item?.xsecToken),
        type: unwrap(nc?.type),
        title: unwrap(nc?.displayTitle),
        userId: user?.userId,
        nickname: user?.nickname,
        likedCount: interact?.likedCount,
        collectedCount: interact?.collectedCount,
        commentCount: interact?.commentCount,
        coverUrl: cover?.url_default
      }};
    }});
    return JSON.stringify({{
      total: feeds.length,
      offset: {args.offset},
      returned: items.length,
      nextOffset: Math.min({args.offset} + items.length, feeds.length),
      hasMore: unwrap(s?.hasMore),
      page: unwrap(s?.searchContext)?.page,
      items
    }});
  }} catch(e) {{
    return JSON.stringify({{ error: true, message: e.message }});
  }}
}})()
"""
    print(js)


if __name__ == '__main__':
    main()
