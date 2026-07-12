# ModDAO V2

ModDAO is a GenLayer-native moderation quality and payout-ledger protocol. It reads
public support logs, asks independent validators to evaluate helpfulness, accuracy,
and policy compliance, allows one moderator appeal, and finalizes a declared payout
tier exactly once.

## Why GenLayer

Moderator quality is subjective: message count cannot determine whether an answer was
patient, correct, effective, and policy-compliant. ModDAO uses GenLayer web evidence,
LLM reasoning, and comparative semantic consensus for the decision that selects a
transparent payout tier.

## Contract lifecycle

1. `initialize` records the calling wallet as admin once.
2. `add_funds` adds admin-controlled treasury ledger units.
3. `register_moderator` records a wallet and fixed STANDARD/EXCELLENT tiers.
4. `request_evaluation` stores one public log per unique payroll cycle.
5. `evaluate` proposes a decision using `prompt_comparative` consensus.
6. `submit_appeal` lets the moderator add new evidence once.
7. `evaluate_appeal` produces the final proposed tier.
8. `finalize_evaluation` applies the treasury ledger update exactly once.

The current implementation is an accounting ledger and does not claim to transfer a
stablecoin.

## Frontend routes

The Next.js application separates Setup, Treasury, Moderator Registry, Deactivation,
Evaluation Request, Review, Appeal, Appeal Review, Finalization, lists, detail,
How It Works, and Explorer proof into focused pages.

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

## Deployment

ModDAO V2 is deployed on GenLayer Studio (Studionet):

`0x2F8C22569060Ae6102a8e8F4920D7F65B67b9179`

Frontend configuration:

```bash
NEXT_PUBLIC_CONTRACT_ADDRESS=0x2F8C22569060Ae6102a8e8F4920D7F65B67b9179
NEXT_PUBLIC_NETWORK=studionet
NEXT_PUBLIC_CONTRACT_VERSION=2
```
