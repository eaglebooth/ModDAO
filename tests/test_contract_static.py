import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "contracts" / "ModDAO.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class ModDAOContractTests(unittest.TestCase):
    def test_header(self):
        lines = SOURCE.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertIn('"Depends": "py-genlayer:', lines[1])

    def test_comparative_consensus(self):
        self.assertNotIn("gl.eq_principle.strict_eq", SOURCE)
        self.assertIn("prompt_comparative(run_review, principle)", SOURCE)
        self.assertIn("prompt_comparative(run_appeal, principle)", SOURCE)

    def test_authorization(self):
        self.assertIn("gl.message.sender_address", SOURCE)
        self.assertGreaterEqual(SOURCE.count('return "ADMIN_ONLY"'), 3)
        self.assertIn('return "MODERATOR_ONLY"', SOURCE)
        self.assertIn('return "NOT_AUTHORIZED"', SOURCE)

    def test_lifecycle_methods(self):
        methods = {node.name for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef)}
        expected = {"initialize", "add_funds", "register_moderator", "deactivate_moderator", "request_evaluation", "evaluate", "submit_appeal", "evaluate_appeal", "finalize_evaluation"}
        self.assertTrue(expected.issubset(methods))

    def test_safety_guards(self):
        for code in ["ALREADY_INITIALIZED", "CYCLE_ALREADY_EVALUATED", "INVALID_AI_RESPONSE", "ALREADY_FINALIZED", "INSUFFICIENT_TREASURY"]:
            self.assertIn(code, SOURCE)

    def test_no_score_division(self):
        self.assertNotIn("// u256", SOURCE)
        self.assertIn("mod_standard_pays", SOURCE)
        self.assertIn("mod_excellent_pays", SOURCE)


if __name__ == "__main__":
    unittest.main()
