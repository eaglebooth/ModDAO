# ModDAO V3

ModDAO is a GenLayer-native moderator quality and payout protocol. It reads public
support logs, asks independent validators to assess helpfulness, accuracy, and policy
compliance, protects a timed appeal, and transfers native GEN from contract custody to
the registered moderator wallet.

## Why GenLayer

Message count cannot determine whether a moderator was patient, correct, effective,
and fair. ModDAO uses web evidence, LLM reasoning, and comparative semantic consensus
for the subjective decision that selects a financially meaningful payout tier.

## Contract lifecycle

1. The constructor binds the deployer wallet as administrator.
2. `fund_treasury` accepts a payable native GEN deposit from that administrator.
3. `register_moderator` records a normalized wallet and fixed STANDARD/EXCELLENT GEN tiers.
4. `request_evaluation` stores one public HTTPS log per unique payroll cycle and reserves the moderator's maximum payout.
5. `evaluate` proposes a decision using `prompt_comparative` semantic consensus.
6. `replace_evidence` recovers a `NEEDS_EVIDENCE` case, with two revisions maximum.
7. `submit_appeal` lets the moderator submit new evidence within 24 hours.
8. `evaluate_appeal` compares the original and appeal evidence.
9. `finalize_evaluation` transfers native GEN exactly once, returns unused reserve, or records a no-payout settlement.
10. `withdraw_unallocated` lets only the administrator recover available treasury.

## Frontend routes

The Next.js application separates contract verification, payable treasury funding,
treasury withdrawal, moderator registration/deactivation, evaluation request, evidence
replacement, AI review, appeal, appeal review, payout settlement, registries, and the
product guide into focused pages. All records shown in registries come from GenLayer
contract reads through `genlayer-js`.

## Local verification

```bash
python -m unittest discover -s tests -v
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

Open `http://localhost:3043`.

## Deployment status

ModDAO V3 is deployed on GenLayer Studio (Studionet):

`0x783bb09AfBA0D070E09601e6A10a1D54796e9F43`

Frontend configuration:

```bash
NEXT_PUBLIC_CONTRACT_ADDRESS=0x783bb09AfBA0D070E09601e6A10a1D54796e9F43
NEXT_PUBLIC_NETWORK=studionet
NEXT_PUBLIC_CONTRACT_VERSION=3
```
