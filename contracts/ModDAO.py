# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


class ModDAO(gl.Contract):
    initialized: u256
    admin_wallet: TreeMap[u256, str]
    treasury_balance: TreeMap[u256, u256]

    mod_count: u256
    mod_wallets: TreeMap[u256, str]
    mod_names: TreeMap[u256, str]
    mod_standard_pays: TreeMap[u256, u256]
    mod_excellent_pays: TreeMap[u256, u256]
    mod_active: TreeMap[u256, u256]

    eval_count: u256
    eval_mod_ids: TreeMap[u256, u256]
    eval_cycle_refs: TreeMap[u256, str]
    eval_log_urls: TreeMap[u256, str]
    eval_appeal_urls: TreeMap[u256, str]
    eval_scores: TreeMap[u256, u256]
    eval_helpfulness: TreeMap[u256, u256]
    eval_accuracy: TreeMap[u256, u256]
    eval_compliance: TreeMap[u256, u256]
    eval_payouts: TreeMap[u256, u256]
    eval_statuses: TreeMap[u256, str]
    eval_comments: TreeMap[u256, str]
    eval_appealed: TreeMap[u256, u256]
    eval_finalized: TreeMap[u256, u256]

    def __init__(self):
        self.initialized = u256(0)
        self.mod_count = u256(0)
        self.eval_count = u256(0)

    @gl.public.write
    def initialize(self) -> typing.Any:
        if self.initialized != u256(0):
            return "ALREADY_INITIALIZED"
        self.admin_wallet[u256(0)] = gl.message.sender_address
        self.treasury_balance[u256(0)] = u256(0)
        self.initialized = u256(1)
        return "INITIALIZED"

    @gl.public.write
    def add_funds(self, amount: u256) -> typing.Any:
        if self.initialized == u256(0):
            return "NOT_INITIALIZED"
        if self.admin_wallet[u256(0)] != gl.message.sender_address:
            return "ADMIN_ONLY"
        if amount == u256(0):
            return "ZERO_AMOUNT"
        self.treasury_balance[u256(0)] = self.treasury_balance[u256(0)] + amount
        return "FUNDS_ADDED"

    @gl.public.write
    def register_moderator(
        self,
        wallet: str,
        name: str,
        standard_pay: u256,
        excellent_pay: u256,
    ) -> typing.Any:
        if self.initialized == u256(0):
            return "NOT_INITIALIZED"
        if self.admin_wallet[u256(0)] != gl.message.sender_address:
            return "ADMIN_ONLY"
        if len(wallet) == 0:
            return "EMPTY_WALLET"
        if len(name) == 0 or len(name) > 100:
            return "INVALID_NAME"
        if standard_pay == u256(0) or excellent_pay < standard_pay:
            return "INVALID_PAY_TIERS"

        i = u256(0)
        while i < self.mod_count:
            if self.mod_wallets[i] == wallet:
                return "WALLET_ALREADY_REGISTERED"
            i = i + u256(1)

        mod_id = self.mod_count
        self.mod_wallets[mod_id] = wallet
        self.mod_names[mod_id] = name
        self.mod_standard_pays[mod_id] = standard_pay
        self.mod_excellent_pays[mod_id] = excellent_pay
        self.mod_active[mod_id] = u256(1)
        self.mod_count = mod_id + u256(1)
        return str(mod_id)

    @gl.public.write
    def deactivate_moderator(self, mod_id: u256) -> typing.Any:
        if self.initialized == u256(0):
            return "NOT_INITIALIZED"
        if self.admin_wallet[u256(0)] != gl.message.sender_address:
            return "ADMIN_ONLY"
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        if self.mod_active[mod_id] == u256(0):
            return "ALREADY_INACTIVE"
        self.mod_active[mod_id] = u256(0)
        return "DEACTIVATED"

    @gl.public.write
    def request_evaluation(self, mod_id: u256, log_url: str, cycle_ref: str) -> typing.Any:
        if self.initialized == u256(0):
            return "NOT_INITIALIZED"
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        sender = gl.message.sender_address
        if self.mod_wallets[mod_id] != sender and self.admin_wallet[u256(0)] != sender:
            return "NOT_AUTHORIZED"
        if self.mod_active[mod_id] == u256(0):
            return "MOD_INACTIVE"
        if len(log_url) == 0 or len(log_url) > 500:
            return "INVALID_LOG_URL"
        if len(cycle_ref) == 0 or len(cycle_ref) > 120:
            return "INVALID_CYCLE_REF"

        i = u256(0)
        while i < self.eval_count:
            if self.eval_cycle_refs[i] == cycle_ref:
                return "CYCLE_ALREADY_EVALUATED"
            i = i + u256(1)

        eval_id = self.eval_count
        self.eval_mod_ids[eval_id] = mod_id
        self.eval_cycle_refs[eval_id] = cycle_ref
        self.eval_log_urls[eval_id] = log_url
        self.eval_appeal_urls[eval_id] = ""
        self.eval_scores[eval_id] = u256(0)
        self.eval_helpfulness[eval_id] = u256(0)
        self.eval_accuracy[eval_id] = u256(0)
        self.eval_compliance[eval_id] = u256(0)
        self.eval_payouts[eval_id] = u256(0)
        self.eval_statuses[eval_id] = "PENDING"
        self.eval_comments[eval_id] = "Awaiting comparative AI review."
        self.eval_appealed[eval_id] = u256(0)
        self.eval_finalized[eval_id] = u256(0)
        self.eval_count = eval_id + u256(1)
        return str(eval_id)

    @gl.public.write
    def evaluate(self, eval_id: u256) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        if self.eval_statuses[eval_id] != "PENDING":
            return "EVAL_NOT_PENDING"

        mod_id = self.eval_mod_ids[eval_id]
        log_url = self.eval_log_urls[eval_id]
        mod_name = self.mod_names[mod_id]

        def run_review() -> str:
            try:
                response = gl.nondet.web.get(log_url)
                content = response.body.decode("utf-8")[:5000]
            except Exception:
                return json.dumps(
                    {"decision": "NEEDS_EVIDENCE", "helpfulness": 0, "accuracy": 0, "compliance": 0, "score": 0, "comment": "The moderation log URL could not be read."},
                    sort_keys=True,
                    separators=(",", ":"),
                )

            prompt = f"""You are an impartial GenLayer jury auditing a community moderator.
Moderator: {mod_name}
MODERATION LOG:
{content}

Score exactly:
- helpfulness 0-30: respectful tone, patience, and useful guidance.
- accuracy 0-50: correct answers, effective problem solving, no harmful invention.
- compliance 0-20: consistent enforcement of community rules without abuse.
- score must equal the sum, from 0 to 100.

Decision rules:
- EXCELLENT for score 90-100 with no serious accuracy/compliance issue.
- STANDARD for score 75-89 with no serious policy violation.
- NO_PAYOUT for score below 75 or evidence of abuse, fabrication, or serious policy failure.
- NEEDS_EVIDENCE when logs are incomplete, unreadable, contradictory, or too weak to judge.

Respond with ONLY this JSON, no markdown:
{{"decision":"EXCELLENT|STANDARD|NO_PAYOUT|NEEDS_EVIDENCE","helpfulness":0,"accuracy":0,"compliance":0,"score":0,"comment":"one concise evidence-based sentence"}}"""
            return gl.nondet.exec_prompt(prompt)

        principle = """Two ModDAO reviews are equivalent when they agree on the substantive payout decision,
the same score band (90-100, 75-89, or below 75), and whether serious accuracy or compliance failures occurred.
The three criterion scores should be close enough to preserve the same total band. Ignore wording, punctuation,
JSON key order, and harmless comment differences. Reject equivalence if one result pays and the other does not,
or if EXCELLENT and STANDARD would select different payout tiers."""

        result = gl.eq_principle.prompt_comparative(run_review, principle)
        return self._store_review_result(eval_id, mod_id, result, "RULING_PROPOSED")

    @gl.public.write
    def submit_appeal(self, eval_id: u256, appeal_url: str) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        if self.eval_statuses[eval_id] != "RULING_PROPOSED":
            return "RULING_NOT_APPEALABLE"
        if self.eval_appealed[eval_id] != u256(0):
            return "APPEAL_ALREADY_USED"
        mod_id = self.eval_mod_ids[eval_id]
        if self.mod_wallets[mod_id] != gl.message.sender_address:
            return "MODERATOR_ONLY"
        if len(appeal_url) == 0 or len(appeal_url) > 500:
            return "INVALID_APPEAL_URL"
        self.eval_appeal_urls[eval_id] = appeal_url
        self.eval_appealed[eval_id] = u256(1)
        self.eval_statuses[eval_id] = "APPEAL_PENDING"
        return "APPEAL_OPENED"

    @gl.public.write
    def evaluate_appeal(self, eval_id: u256) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        if self.eval_statuses[eval_id] != "APPEAL_PENDING":
            return "APPEAL_NOT_PENDING"

        mod_id = self.eval_mod_ids[eval_id]
        appeal_url = self.eval_appeal_urls[eval_id]
        original_score = self.eval_scores[eval_id]
        original_comment = self.eval_comments[eval_id]

        def run_appeal() -> str:
            try:
                response = gl.nondet.web.get(appeal_url)
                content = response.body.decode("utf-8")[:5000]
            except Exception:
                return json.dumps(
                    {"decision": "NEEDS_EVIDENCE", "helpfulness": 0, "accuracy": 0, "compliance": 0, "score": 0, "comment": "The appeal evidence URL could not be read."},
                    sort_keys=True,
                    separators=(",", ":"),
                )

            prompt = f"""You are the ModDAO appeal jury. Reconsider the moderator audit using new evidence.
Original score: {original_score}
Original reason: {original_comment}
NEW APPEAL EVIDENCE:
{content}

Use the same helpfulness 0-30, accuracy 0-50, compliance 0-20 rubric and the same payout thresholds.
Respond with ONLY this JSON:
{{"decision":"EXCELLENT|STANDARD|NO_PAYOUT|NEEDS_EVIDENCE","helpfulness":0,"accuracy":0,"compliance":0,"score":0,"comment":"one concise sentence explaining whether the new evidence changes the result"}}"""
            return gl.nondet.exec_prompt(prompt)

        principle = """Two ModDAO appeal reviews are equivalent when they agree on whether new evidence changes
the payout tier, the final decision, the same score band, and whether serious accuracy or compliance issues remain.
Ignore wording and JSON formatting differences. Reject equivalence whenever the selected payout tier differs."""
        result = gl.eq_principle.prompt_comparative(run_appeal, principle)
        return self._store_review_result(eval_id, mod_id, result, "APPEAL_RULING")

    def _store_review_result(self, eval_id: u256, mod_id: u256, result: str, final_status: str) -> typing.Any:
        try:
            data = json.loads(result)
        except Exception:
            return "INVALID_AI_RESPONSE"

        decision = str(data.get("decision", "NEEDS_EVIDENCE")).upper()
        try:
            helpfulness = int(data.get("helpfulness", 0))
            accuracy = int(data.get("accuracy", 0))
            compliance = int(data.get("compliance", 0))
            score = int(data.get("score", 0))
        except Exception:
            return "INVALID_AI_RESPONSE"
        if helpfulness < 0 or helpfulness > 30 or accuracy < 0 or accuracy > 50 or compliance < 0 or compliance > 20:
            return "INVALID_AI_RESPONSE"
        calculated = helpfulness + accuracy + compliance
        if score != calculated or score < 0 or score > 100:
            return "INVALID_AI_RESPONSE"
        if decision != "EXCELLENT" and decision != "STANDARD" and decision != "NO_PAYOUT" and decision != "NEEDS_EVIDENCE":
            return "INVALID_AI_RESPONSE"

        payout = u256(0)
        if decision == "EXCELLENT" and score >= 90:
            payout = self.mod_excellent_pays[mod_id]
        elif decision == "STANDARD" and score >= 75:
            payout = self.mod_standard_pays[mod_id]
        elif decision != "NO_PAYOUT" and decision != "NEEDS_EVIDENCE":
            return "INVALID_AI_RESPONSE"

        self.eval_helpfulness[eval_id] = u256(helpfulness)
        self.eval_accuracy[eval_id] = u256(accuracy)
        self.eval_compliance[eval_id] = u256(compliance)
        self.eval_scores[eval_id] = u256(score)
        self.eval_payouts[eval_id] = payout
        self.eval_comments[eval_id] = str(data.get("comment", "No reason supplied."))[:900]
        if decision == "NEEDS_EVIDENCE":
            self.eval_statuses[eval_id] = "NEEDS_EVIDENCE"
        else:
            self.eval_statuses[eval_id] = final_status
        return self.get_evaluation(eval_id)

    @gl.public.write
    def finalize_evaluation(self, eval_id: u256) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        status = self.eval_statuses[eval_id]
        if status != "RULING_PROPOSED" and status != "APPEAL_RULING":
            return "RULING_NOT_FINAL"
        if self.eval_finalized[eval_id] != u256(0):
            return "ALREADY_FINALIZED"

        payout = self.eval_payouts[eval_id]
        current = self.treasury_balance[u256(0)]
        if payout > current:
            return "INSUFFICIENT_TREASURY"
        self.treasury_balance[u256(0)] = current - payout
        self.eval_finalized[eval_id] = u256(1)
        self.eval_statuses[eval_id] = "FINALIZED"
        return self.get_evaluation(eval_id)

    @gl.public.view
    def get_contract_state(self) -> str:
        admin = ""
        treasury = u256(0)
        if self.initialized != u256(0):
            admin = self.admin_wallet[u256(0)]
            treasury = self.treasury_balance[u256(0)]
        return json.dumps({"initialized": str(self.initialized), "admin": admin, "treasury": str(treasury), "mod_count": str(self.mod_count), "eval_count": str(self.eval_count)}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_moderator(self, mod_id: u256) -> str:
        if mod_id >= self.mod_count:
            return json.dumps({"error": "MOD_NOT_FOUND"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"id": str(mod_id), "wallet": self.mod_wallets[mod_id], "name": self.mod_names[mod_id], "standard_pay": str(self.mod_standard_pays[mod_id]), "excellent_pay": str(self.mod_excellent_pays[mod_id]), "active": str(self.mod_active[mod_id])}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_evaluation(self, eval_id: u256) -> str:
        if eval_id >= self.eval_count:
            return json.dumps({"error": "EVAL_NOT_FOUND"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"id": str(eval_id), "mod_id": str(self.eval_mod_ids[eval_id]), "cycle_ref": self.eval_cycle_refs[eval_id], "log_url": self.eval_log_urls[eval_id], "appeal_url": self.eval_appeal_urls[eval_id], "helpfulness": str(self.eval_helpfulness[eval_id]), "accuracy": str(self.eval_accuracy[eval_id]), "compliance": str(self.eval_compliance[eval_id]), "score": str(self.eval_scores[eval_id]), "payout": str(self.eval_payouts[eval_id]), "status": self.eval_statuses[eval_id], "comment": self.eval_comments[eval_id], "appealed": str(self.eval_appealed[eval_id]), "finalized": str(self.eval_finalized[eval_id])}, sort_keys=True, separators=(",", ":"))
