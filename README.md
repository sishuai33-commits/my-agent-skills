# Antigravity Skills System: The Self-Evolving Agent

Welcome to the **Antigravity Skills System**, an "Antifragile" skill management framework for AI coding agents.

This repository contains a set of meta-skills that allow your AI assistant (Claude, etc.) to **manage, test, and evolve its own capabilities** based on your feedback.

## 🚀 Key Components

### 1. The Manager: `skills-management`
**Role**: Administrator & DevOps
- **Responsibilities**: 
  - Validates new skills for security risks (P0-P3 permissions).
  - Handles updates from official sources while preserving your custom patches ("Smart Rebase").
  - Executes "Hot-Fixes" on broken skills during live sessions.

### 2. The Engine: `self-improving-agent`
**Role**: Evolution & Optimization
- **Responsibilities**:
  - Listens for your corrections ("No, do it this way...").
  - Listens for your praise ("This code is perfect!").
  - **Automatically updates skill definitions** based on this feedback.
  - **Creates regression tests** in `tests/` to prevent future regressions.

### 3. The Vault: `tests/`
**Role**: Persistence & Quality Assurance
- Stores test cases generated from your real-world usage.
- Ensures that once you fix a bug in a skill, it stays fixed.

---

## 🛠 Installation

1. **Clone this repository** to your local machine:
   ```bash
   git clone https://github.com/yourusername/antigravity-skills.git ~/My_Skills_Library/antigravity-skills
   ```

2. **Configure your AI Agent** (Cursor, VSCode, OpenCode, etc.):
   - Add `~/My_Skills_Library/antigravity-skills` as a **Context Directory**.
   - Or explicitly load `skills-management/SKILL.md` when you need to perform maintenance.

---

## 💡 How to Use (The "Evolution Loop")

You don't need to run scripts manually. Just talk to your agent.

### Scenario A: Correcting a Mistake
> **You**: "The `frontend-design` skill keeps using `var` instead of `const`. Stop that."
>
> **Agent (The Engine)**: "Understood. I have updated the `frontend-design` rules to strictly forbid `var`. I've also added a test case to `tests/frontend-design.test.md` to ensure this doesn't happen again."

### Scenario B: Saving a Best Practice
> **You**: "This React component pattern is exactly what I want. Save it as the standard."
>
> **Agent (The Engine)**: "Done. I've extracted this code as a 'Gold Standard' example and added it to the `frontend-design` skill definition."

### Scenario C: Updating from Upstream
> **You**: "Check for updates to the official skills."
>
> **Agent (The Manager)**: "Found updates. I'm applying them now, but I'll keep your custom 'No `var`' rule intact using the Smart Rebase strategy."

---

## 📂 Directory Structure

```
.
├── skills-management/       # The "Manager" skill (Admin, Security, Updates)
├── self-improving-agent/    # The "Engine" skill (Feedback loop, Evolution)
├── tests/                   # Your personal "Test Vault" (Auto-generated)
├── antigravity-model-sync/  # (Optional) Model synchronization tools
└── antigravity-proxy-manager/ # (Optional) Proxy management tools
```

## 🤝 Contributing

This system is designed to evolve. Feel free to fork, improve the `skills-management` logic, and submit Pull Requests!
