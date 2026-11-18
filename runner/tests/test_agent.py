import unittest

from runner.agent import build_prompt, parse_outcome


class AgentProtocolTests(unittest.TestCase):
    def test_parses_done_result(self):
        outcome = parse_outcome('log\nFACTORY_RESULT: {"status":"done","message":"Tests passed"}\n')
        self.assertEqual((outcome.status, outcome.message), ("done", "Tests passed"))

    def test_rejects_missing_result(self):
        self.assertEqual(parse_outcome("finished").status, "stuck")

    def test_prompt_has_issue_and_protocol(self):
        prompt = build_prompt(12, "Add greeting", "## Goal\nAdd it", None)
        self.assertIn("#12", prompt)
        self.assertIn("FACTORY_RESULT:", prompt)


if __name__ == "__main__":
    unittest.main()
