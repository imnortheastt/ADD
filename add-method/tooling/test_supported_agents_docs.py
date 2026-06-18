#!/usr/bin/env python3
"""The onboarding docs name the expanded supported-agent set (multi-agent-installer · onboarding-docs-refresh).

After the installer learned six more agents, README + GETTING-STARTED must tell users ADD works
beyond Claude Code. Keep the "any agent" phrasing (test_agent_portability depends on it).

Run: python3 -m unittest test_supported_agents_docs -v
"""
import unittest
from pathlib import Path

_ADD_METHOD = Path(__file__).resolve().parent.parent
README = (_ADD_METHOD / "README.md").read_text(encoding="utf-8")
GETTING = (_ADD_METHOD / "GETTING-STARTED.md").read_text(encoding="utf-8")

NEW_AGENTS = ["Cursor", "Windsurf", "Trae", "Gemini", "Copilot", "Cline", "Aider"]


class SupportedAgentsDocsTest(unittest.TestCase):
    def test_readme_names_new_agents(self):
        for name in NEW_AGENTS:
            self.assertIn(name, README, f"README should name {name}")

    def test_getting_started_lists_agents_and_keeps_any_agent(self):
        for name in NEW_AGENTS:
            self.assertIn(name, GETTING, f"GETTING-STARTED should name {name}")
        self.assertIn("any agent", GETTING, "the 'any agent' phrasing must be preserved")


if __name__ == "__main__":
    unittest.main(verbosity=2)
