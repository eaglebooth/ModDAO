# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import typing
import json

class ModDAO(gl.Contract):
    admin_wallet: TreeMap[u256, str]
    treasury_balance: TreeMap[u256, u256]

    mod_count: u256
    mod_wallets: TreeMap[u256, str]
    mod_names: TreeMap[u256, str]
    mod_base_pays: TreeMap[u256, u256]
    mod_active: TreeMap[u256, u256]

    eval_count: u256
    eval_mod_ids: TreeMap[u256, u256]
    eval_log_urls: TreeMap[u256, str]
    eval_scores: TreeMap[u256, u256]
    eval_payouts: TreeMap[u256, u256]
    eval_statuses: TreeMap[u256, str]
    eval_comments: TreeMap[u256, str]

    def __init__(self):
        self.mod_count = u256(0)
        self.eval_count = u256(0)

    @gl.public.write
    def initialize(self, admin: str) -> typing.Any:
        if len(admin) == 0:
            return "EMPTY_ADMIN"
        self.admin_wallet[u256(0)] = admin
        self.treasury_balance[u256(0)] = u256(0)
        return "INITIALIZED"

    @gl.public.write
    def add_funds(self, amount: u256) -> typing.Any:
        if amount == u256(0):
            return "ZERO_AMOUNT"
        current = self.treasury_balance[u256(0)]
        self.treasury_balance[u256(0)] = current + amount
        return "FUNDS_ADDED"

    @gl.public.write
    def register_moderator(self, wallet: str, name: str, base_pay: u256) -> typing.Any:
        if len(wallet) == 0:
            return "EMPTY_WALLET"
        if len(name) == 0:
            return "EMPTY_NAME"
        if base_pay == u256(0):
            return "ZERO_BASE_PAY"

        mod_id = self.mod_count
        self.mod_wallets[mod_id] = wallet
        self.mod_names[mod_id] = name
        self.mod_base_pays[mod_id] = base_pay
        self.mod_active[mod_id] = u256(1)
        self.mod_count = mod_id + u256(1)
        return "REGISTERED"

    @gl.public.write
    def deactivate_moderator(self, mod_id: u256) -> typing.Any:
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        self.mod_active[mod_id] = u256(0)
        return "DEACTIVATED"

    @gl.public.write
    def request_evaluation(self, mod_id: u256, log_url: str) -> typing.Any:
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        if self.mod_active[mod_id] == u256(0):
            return "MOD_INACTIVE"
        if len(log_url) == 0:
            return "EMPTY_LOG_URL"

        eval_id = self.eval_count
        self.eval_mod_ids[eval_id] = mod_id
        self.eval_log_urls[eval_id] = log_url
        self.eval_scores[eval_id] = u256(0)
        self.eval_payouts[eval_id] = u256(0)
        self.eval_statuses[eval_id] = "PENDING"
        self.eval_comments[eval_id] = ""
        self.eval_count = eval_id + u256(1)
        return "REQUESTED"

    @gl.public.write
    def evaluate(self, eval_id: u256) -> typing.Any:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        if self.eval_statuses[eval_id] != "PENDING":
            return "ALREADY_EVALUATED"

        mod_id = self.eval_mod_ids[eval_id]
        log_url = self.eval_log_urls[eval_id]
        mod_name = self.mod_names[mod_id]
        base_pay = self.mod_base_pays[mod_id]

        def run() -> str:
            # 1. Fetch moderator support logs
            content = ""
            if len(log_url) > 0:
                resp = gl.nondet.web.get(log_url)
                content = resp.body.decode("utf-8")
                # Truncate content to avoid token overflow
                if len(content) > 3000:
                    content = content[:3000]

            # 2. Ask AI Jury to score based on quality of responses
            prompt = (
                f"You are a member of the ModDAO AI Jury evaluating community support quality.\n"
                f"Moderator Name: {mod_name}\n"
                f"Chat Log/Evidence:\n{content}\n\n"
                f"Evaluate the moderator's performance on the following criteria:\n"
                f"- Polite and helpful attitude (0-30 points)\n"
                f"- Problem-solving efficacy and accurate information (0-50 points)\n"
                f"- Proper compliance with community rules and moderation standards (0-20 points)\n\n"
                f"Calculate the total score (sum of all criteria, 0 to 100).\n"
                f"Provide a brief comment justifying the score.\n\n"
                f"Respond with ONLY a JSON object formatted exactly as:\n"
                f"{{{{\n"
                f"  \"score\": <integer 0 to 100>,\n"
                f"  \"comment\": \"<brief justification string>\"\n"
                f"}}}}\n"
                f"Do not include any other markdown wrapper, note, or text."
            )
            return gl.nondet.exec_prompt(prompt)

        # 3. Consensus step comparing independent LLM nodes
        result = gl.eq_principle.strict_eq(run)

        # 4. Parse output and handle state transition
        data = json.loads(result)
        score_val = int(data["score"])
        if score_val < 0:
            score_val = 0
        if score_val > 100:
            score_val = 100
        score = u256(score_val)
        comment = str(data["comment"])

        payout = (base_pay * score) // u256(100)
        current_treasury = self.treasury_balance[u256(0)]

        if payout > current_treasury:
            # Budget check failed: reject the payment but log the reason
            self.eval_statuses[eval_id] = "REJECTED"
            self.eval_comments[eval_id] = "Insufficient treasury funds for payout of " + str(payout)
            return "INSUFFICIENT_TREASURY"

        # Apply state changes safely
        self.treasury_balance[u256(0)] = current_treasury - payout
        self.eval_scores[eval_id] = score
        self.eval_payouts[eval_id] = payout
        self.eval_comments[eval_id] = comment
        self.eval_statuses[eval_id] = "APPROVED"
        return "EVALUATED"

    @gl.public.view
    def get_contract_state(self) -> str:
        # Serializes general state metadata
        admin_addr = ""
        treasury_val = 0
        # Accessing self.admin_wallet[u256(0)] safely
        try:
            admin_addr = self.admin_wallet[u256(0)]
        except Exception:
            pass

        # Accessing self.treasury_balance[u256(0)] safely
        try:
            treasury_val = int(self.treasury_balance[u256(0)])
        except Exception:
            pass

        return json.dumps(
            {
                "admin": admin_addr,
                "treasury": treasury_val,
                "mod_count": int(self.mod_count),
                "eval_count": int(self.eval_count),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_moderator(self, mod_id: u256) -> str:
        if mod_id >= self.mod_count:
            return "MOD_NOT_FOUND"
        return json.dumps(
            {
                "id": int(mod_id),
                "wallet": self.mod_wallets[mod_id],
                "name": self.mod_names[mod_id],
                "base_pay": int(self.mod_base_pays[mod_id]),
                "active": int(self.mod_active[mod_id]),
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_evaluation(self, eval_id: u256) -> str:
        if eval_id >= self.eval_count:
            return "EVAL_NOT_FOUND"
        return json.dumps(
            {
                "id": int(eval_id),
                "mod_id": int(self.eval_mod_ids[eval_id]),
                "log_url": self.eval_log_urls[eval_id],
                "score": int(self.eval_scores[eval_id]),
                "payout": int(self.eval_payouts[eval_id]),
                "status": self.eval_statuses[eval_id],
                "comment": self.eval_comments[eval_id],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
