import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "contracts" / "ModDAO.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class ModDAOContractTests(unittest.TestCase):
    def test_exact_runtime_header(self):
        lines = SOURCE.splitlines()
        self.assertEqual(lines[0], "# v0.2.16")
        self.assertEqual(lines[1], '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }')
        self.assertEqual(lines[2], "from genlayer import *")

    def test_semantic_consensus_for_subjective_reviews(self):
        self.assertNotIn("gl.eq_principle.strict_eq", SOURCE)
        self.assertIn("prompt_comparative(run_review, principle)", SOURCE)
        self.assertIn("prompt_comparative(run_appeal, principle)", SOURCE)

    def test_real_payable_treasury_and_transfers(self):
        self.assertIn("@gl.public.write.payable\n    def fund_treasury", SOURCE)
        self.assertIn("amount = gl.message.value", SOURCE)
        self.assertIn("emit_transfer(value=payout)", SOURCE)
        self.assertIn("emit_transfer(value=amount)", SOURCE)

    def test_deployer_owned_and_normalized_authorization(self):
        self.assertIn("self.admin_wallet[u256(0)] = gl.message.sender_address.as_hex", SOURCE)
        self.assertNotIn("def initialize", SOURCE)
        self.assertGreaterEqual(SOURCE.count("gl.message.sender_address.as_hex"), 5)
        self.assertIn("normalized_wallet = Address(wallet).as_hex", SOURCE)

    def test_web_render_and_bounded_evidence_recovery(self):
        self.assertNotIn("gl.nondet.web.get", SOURCE)
        self.assertGreaterEqual(SOURCE.count("gl.nondet.web.render"), 3)
        self.assertIn("def replace_evidence", SOURCE)
        self.assertIn('return "EVIDENCE_REVISION_LIMIT"', SOURCE)

    def test_timed_appeal_and_single_settlement(self):
        self.assertIn("gl.get_block_timestamp() + u256(86400)", SOURCE)
        self.assertIn('return "APPEAL_WINDOW_OPEN"', SOURCE)
        self.assertIn('return "APPEAL_WINDOW_CLOSED"', SOURCE)
        self.assertIn('return "ALREADY_FINALIZED"', SOURCE)
        self.assertIn("settlement_count", SOURCE)

    def test_evaluation_reserves_maximum_payout(self):
        self.assertIn("reserve = self.mod_excellent_pays[mod_id]", SOURCE)
        self.assertIn("self.eval_reserves[eval_id] = reserve", SOURCE)
        self.assertIn("def _release_reserve", SOURCE)
        self.assertIn('return "PAYOUT_EXCEEDS_RESERVE"', SOURCE)

    def test_lifecycle_methods(self):
        methods = {node.name for node in ast.walk(TREE) if isinstance(node, ast.FunctionDef)}
        expected = {"fund_treasury", "withdraw_unallocated", "register_moderator", "deactivate_moderator", "request_evaluation", "replace_evidence", "evaluate", "submit_appeal", "evaluate_appeal", "finalize_evaluation", "get_settlement"}
        self.assertTrue(expected.issubset(methods))


if __name__ == "__main__":
    unittest.main()
