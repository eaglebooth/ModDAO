# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class ModDAO(gl.Contract):
    initialized: u256
    admin_wallet: TreeMap[u256, str]
    treasury_balance: TreeMap[u256, u256]
    treasury_reserved: TreeMap[u256, u256]
    total_funded: TreeMap[u256, u256]
    total_paid: TreeMap[u256, u256]
    total_withdrawn: TreeMap[u256, u256]

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
    eval_appeal_deadlines: TreeMap[u256, u256]
    eval_evidence_revisions: TreeMap[u256, u256]
    eval_reserves: TreeMap[u256, u256]

    settlement_count: u256
    settlement_eval_ids: TreeMap[u256, u256]
    settlement_recipients: TreeMap[u256, str]
    settlement_amounts: TreeMap[u256, u256]
    settlement_kinds: TreeMap[u256, str]

    def __init__(self):
        self.initialized = u256(1)
        self.admin_wallet[u256(0)] = gl.message.sender_address.as_hex
        self.treasury_balance[u256(0)] = u256(0)
        self.treasury_reserved[u256(0)] = u256(0)
        self.total_funded[u256(0)] = u256(0)
        self.total_paid[u256(0)] = u256(0)
        self.total_withdrawn[u256(0)] = u256(0)
        self.mod_count = u256(0)
        self.eval_count = u256(0)
        self.settlement_count = u256(0)

    def _is_admin(self) -> typing.Any:
        return self.admin_wallet[u256(0)] == gl.message.sender_address.as_hex

    def _valid_url(self, url: str) -> typing.Any:
        return len(url) >= 12 and len(url) <= 500 and url.startswith("https://")

    @gl.public.write.payable
    def fund_treasury(self) -> typing.Any:
        if not self._is_admin():
            return "ADMIN_ONLY"
        amount = gl.message.value
        if amount == u256(0):
            return "ZERO_AMOUNT"
        self.treasury_balance[u256(0)] = self.treasury_balance[u256(0)] + amount
        self.total_funded[u256(0)] = self.total_funded[u256(0)] + amount
        return "TREASURY_FUNDED"

    @gl.public.write
    def withdraw_unallocated(self, amount: u256) -> typing.Any:
        if not self._is_admin():
            return "ADMIN_ONLY"
        if amount == u256(0):
            return "ZERO_AMOUNT"
        current = self.treasury_balance[u256(0)]
        if amount > current:
            return "INSUFFICIENT_TREASURY"
        self.treasury_balance[u256(0)] = current - amount
        self.total_withdrawn[u256(0)] = self.total_withdrawn[u256(0)] + amount
        _Recipient(gl.message.sender_address).emit_transfer(value=amount)
        return "TREASURY_WITHDRAWN"

    @gl.public.write
    def register_moderator(
        self,
        wallet: str,
        name: str,
        standard_pay: u256,
        excellent_pay: u256,
    ) -> typing.Any:
        if not self._is_admin():
            return "ADMIN_ONLY"
        if len(name) == 0 or len(name) > 100:
            return "INVALID_NAME"
        if standard_pay == u256(0) or excellent_pay < standard_pay:
            return "INVALID_PAY_TIERS"
        try:
            normalized_wallet = Address(wallet).as_hex
        except Exception:
            return "INVALID_WALLET"

        i = u256(0)
        while i < self.mod_count:
            if self.mod_wallets[i] == normalized_wallet:
                return "WALLET_ALREADY_REGISTERED"
            i = i + u256(1)

        mod_id = self.mod_count
        self.mod_wallets[mod_id] = normalized_wallet
        self.mod_names[mod_id] = name
        self.mod_standard_pays[mod_id] = standard_pay
        self.mod_excellent_pays[mod_id] = excellent_pay
        self.mod_active[mod_id] = u256(1)
        self.mod_count = mod_id + u256(1)
        return str(mod_id)

    @gl.public.write
    def deactivate_moderator(self, mod_id: u256) -> typing.Any:
        if not self._is_admin():
            return "ADMIN_ONLY"
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        if self.mod_active[mod_id] == u256(0):
            return "ALREADY_INACTIVE"
        self.mod_active[mod_id] = u256(0)
        return "DEACTIVATED"

    @gl.public.write
    def request_evaluation(self, mod_id: u256, log_url: str, cycle_ref: str) -> typing.Any:
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        sender = gl.message.sender_address.as_hex
        if self.mod_wallets[mod_id] != sender and self.admin_wallet[u256(0)] != sender:
            return "NOT_AUTHORIZED"
        if self.mod_active[mod_id] == u256(0):
            return "MOD_INACTIVE"
        if not self._valid_url(log_url):
            return "INVALID_LOG_URL"
        if len(cycle_ref) == 0 or len(cycle_ref) > 120:
            return "INVALID_CYCLE_REF"

        reserve = self.mod_excellent_pays[mod_id]
        available = self.treasury_balance[u256(0)]
        if reserve > available:
            return "INSUFFICIENT_TREASURY"

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
        self.eval_appeal_deadlines[eval_id] = u256(0)
        self.eval_evidence_revisions[eval_id] = u256(0)
        self.eval_reserves[eval_id] = reserve
        self.treasury_balance[u256(0)] = available - reserve
        self.treasury_reserved[u256(0)] = self.treasury_reserved[u256(0)] + reserve
        self.eval_count = eval_id + u256(1)
        return str(eval_id)

    @gl.public.write
    def replace_evidence(self, eval_id: u256, new_log_url: str) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        if self.eval_statuses[eval_id] != "NEEDS_EVIDENCE":
            return "EVIDENCE_NOT_REQUESTED"
        mod_id = self.eval_mod_ids[eval_id]
        sender = gl.message.sender_address.as_hex
        if self.mod_wallets[mod_id] != sender and self.admin_wallet[u256(0)] != sender:
            return "NOT_AUTHORIZED"
        if self.eval_evidence_revisions[eval_id] >= u256(2):
            return "EVIDENCE_REVISION_LIMIT"
        if not self._valid_url(new_log_url):
            return "INVALID_LOG_URL"
        self.eval_log_urls[eval_id] = new_log_url
        self.eval_evidence_revisions[eval_id] = self.eval_evidence_revisions[eval_id] + u256(1)
        self.eval_statuses[eval_id] = "PENDING"
        self.eval_comments[eval_id] = "Updated evidence is ready for review."
        return "EVIDENCE_REPLACED"

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
                content = str(gl.nondet.web.render(log_url, mode="html"))[:5000]
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
        if gl.get_block_timestamp() > self.eval_appeal_deadlines[eval_id]:
            return "APPEAL_WINDOW_CLOSED"
        mod_id = self.eval_mod_ids[eval_id]
        if self.mod_wallets[mod_id] != gl.message.sender_address.as_hex:
            return "MODERATOR_ONLY"
        if not self._valid_url(appeal_url):
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
        original_url = self.eval_log_urls[eval_id]
        appeal_url = self.eval_appeal_urls[eval_id]
        original_score = self.eval_scores[eval_id]
        original_comment = self.eval_comments[eval_id]

        def run_appeal() -> str:
            try:
                original = str(gl.nondet.web.render(original_url, mode="html"))[:2600]
                appeal = str(gl.nondet.web.render(appeal_url, mode="html"))[:3400]
            except Exception:
                return json.dumps(
                    {"decision": "NEEDS_EVIDENCE", "helpfulness": 0, "accuracy": 0, "compliance": 0, "score": 0, "comment": "The appeal evidence could not be read."},
                    sort_keys=True,
                    separators=(",", ":"),
                )

            prompt = f"""You are the ModDAO appeal jury. Reconsider the moderator audit using both records.
Original score: {original_score}
Original reason: {original_comment}
ORIGINAL LOG:
{original}
NEW APPEAL EVIDENCE:
{appeal}

Use the same helpfulness 0-30, accuracy 0-50, compliance 0-20 rubric and payout thresholds.
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
            decision = str(data.get("decision", "NEEDS_EVIDENCE")).upper()
            helpfulness = int(data.get("helpfulness", 0))
            accuracy = int(data.get("accuracy", 0))
            compliance = int(data.get("compliance", 0))
            score = int(data.get("score", 0))
        except Exception:
            return "INVALID_AI_RESPONSE"
        if helpfulness < 0 or helpfulness > 30 or accuracy < 0 or accuracy > 50 or compliance < 0 or compliance > 20:
            return "INVALID_AI_RESPONSE"
        if score != helpfulness + accuracy + compliance or score < 0 or score > 100:
            return "INVALID_AI_RESPONSE"
        if decision not in ("EXCELLENT", "STANDARD", "NO_PAYOUT", "NEEDS_EVIDENCE"):
            return "INVALID_AI_RESPONSE"

        payout = u256(0)
        if decision == "EXCELLENT" and score >= 90:
            payout = self.mod_excellent_pays[mod_id]
        elif decision == "STANDARD" and score >= 75 and score < 90:
            payout = self.mod_standard_pays[mod_id]
        elif decision not in ("NO_PAYOUT", "NEEDS_EVIDENCE"):
            return "INVALID_AI_RESPONSE"

        self.eval_helpfulness[eval_id] = u256(helpfulness)
        self.eval_accuracy[eval_id] = u256(accuracy)
        self.eval_compliance[eval_id] = u256(compliance)
        self.eval_scores[eval_id] = u256(score)
        self.eval_payouts[eval_id] = payout
        self.eval_comments[eval_id] = str(data.get("comment", "No reason supplied."))[:900]
        if decision == "NEEDS_EVIDENCE":
            self.eval_appeal_deadlines[eval_id] = u256(0)
            if self.eval_evidence_revisions[eval_id] >= u256(2):
                self.eval_statuses[eval_id] = "CANCELLED_EVIDENCE"
                self.eval_finalized[eval_id] = u256(1)
                self._release_reserve(eval_id)
                self._record_settlement(eval_id, self.mod_wallets[mod_id], u256(0), "EVIDENCE_CANCELLED")
            else:
                self.eval_statuses[eval_id] = "NEEDS_EVIDENCE"
        else:
            self.eval_statuses[eval_id] = final_status
            if final_status == "RULING_PROPOSED":
                self.eval_appeal_deadlines[eval_id] = gl.get_block_timestamp() + u256(86400)
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
        if status == "RULING_PROPOSED" and gl.get_block_timestamp() <= self.eval_appeal_deadlines[eval_id]:
            return "APPEAL_WINDOW_OPEN"

        payout = self.eval_payouts[eval_id]
        recipient = self.mod_wallets[self.eval_mod_ids[eval_id]]
        reserved = self.eval_reserves[eval_id]
        if payout > reserved:
            return "PAYOUT_EXCEEDS_RESERVE"
        if payout == u256(0):
            self.eval_finalized[eval_id] = u256(1)
            self.eval_statuses[eval_id] = "FINALIZED_NO_PAYOUT"
            self._release_reserve(eval_id)
            self._record_settlement(eval_id, recipient, payout, "NO_PAYOUT")
            return self.get_evaluation(eval_id)

        self._release_reserve(eval_id)
        self.treasury_balance[u256(0)] = self.treasury_balance[u256(0)] - payout
        self.total_paid[u256(0)] = self.total_paid[u256(0)] + payout
        self.eval_finalized[eval_id] = u256(1)
        self.eval_statuses[eval_id] = "PAID"
        self._record_settlement(eval_id, recipient, payout, "MODERATOR_PAYOUT")
        _Recipient(Address(recipient)).emit_transfer(value=payout)
        return self.get_evaluation(eval_id)

    def _release_reserve(self, eval_id: u256) -> typing.Any:
        reserved = self.eval_reserves[eval_id]
        if reserved == u256(0):
            return u256(0)
        self.eval_reserves[eval_id] = u256(0)
        self.treasury_reserved[u256(0)] = self.treasury_reserved[u256(0)] - reserved
        self.treasury_balance[u256(0)] = self.treasury_balance[u256(0)] + reserved
        return reserved

    def _record_settlement(self, eval_id: u256, recipient: str, amount: u256, kind: str) -> typing.Any:
        settlement_id = self.settlement_count
        self.settlement_eval_ids[settlement_id] = eval_id
        self.settlement_recipients[settlement_id] = recipient
        self.settlement_amounts[settlement_id] = amount
        self.settlement_kinds[settlement_id] = kind
        self.settlement_count = settlement_id + u256(1)
        return settlement_id

    @gl.public.view
    def get_contract_state(self) -> str:
        return json.dumps({"initialized": str(self.initialized), "admin": self.admin_wallet[u256(0)], "treasury_available": str(self.treasury_balance[u256(0)]), "treasury_reserved": str(self.treasury_reserved[u256(0)]), "total_funded": str(self.total_funded[u256(0)]), "total_paid": str(self.total_paid[u256(0)]), "total_withdrawn": str(self.total_withdrawn[u256(0)]), "mod_count": str(self.mod_count), "eval_count": str(self.eval_count), "settlement_count": str(self.settlement_count)}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_moderator(self, mod_id: u256) -> str:
        if mod_id >= self.mod_count:
            return json.dumps({"error": "MOD_NOT_FOUND"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"id": str(mod_id), "wallet": self.mod_wallets[mod_id], "name": self.mod_names[mod_id], "standard_pay": str(self.mod_standard_pays[mod_id]), "excellent_pay": str(self.mod_excellent_pays[mod_id]), "active": str(self.mod_active[mod_id])}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_evaluation(self, eval_id: u256) -> str:
        if eval_id >= self.eval_count:
            return json.dumps({"error": "EVAL_NOT_FOUND"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"id": str(eval_id), "mod_id": str(self.eval_mod_ids[eval_id]), "cycle_ref": self.eval_cycle_refs[eval_id], "log_url": self.eval_log_urls[eval_id], "appeal_url": self.eval_appeal_urls[eval_id], "helpfulness": str(self.eval_helpfulness[eval_id]), "accuracy": str(self.eval_accuracy[eval_id]), "compliance": str(self.eval_compliance[eval_id]), "score": str(self.eval_scores[eval_id]), "payout": str(self.eval_payouts[eval_id]), "reserve": str(self.eval_reserves[eval_id]), "status": self.eval_statuses[eval_id], "comment": self.eval_comments[eval_id], "appealed": str(self.eval_appealed[eval_id]), "finalized": str(self.eval_finalized[eval_id]), "appeal_deadline": str(self.eval_appeal_deadlines[eval_id]), "evidence_revisions": str(self.eval_evidence_revisions[eval_id])}, sort_keys=True, separators=(",", ":"))

    @gl.public.view
    def get_settlement(self, settlement_id: u256) -> str:
        if settlement_id >= self.settlement_count:
            return json.dumps({"error": "SETTLEMENT_NOT_FOUND"}, sort_keys=True, separators=(",", ":"))
        return json.dumps({"id": str(settlement_id), "eval_id": str(self.settlement_eval_ids[settlement_id]), "recipient": self.settlement_recipients[settlement_id], "amount": str(self.settlement_amounts[settlement_id]), "kind": self.settlement_kinds[settlement_id]}, sort_keys=True, separators=(",", ":"))
