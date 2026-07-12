# ModDAO V2 Rebuild Plan

## Visual direction

ModDAO will use a moderation operations-room identity: crisp white and cool gray,
electric cobalt for trusted actions, signal yellow for review, and restrained red for
policy risk. The layout uses transcript columns, score rails, audit stamps, and dense
editorial typography. It must not reuse the green civic style, hero composition, form
shell, or timeline treatment of NeighborPeace.

## Routes

| Route | Purpose |
| --- | --- |
| `/` | Product overview and live contract status |
| `/how-it-works` | Full scoring, consensus, appeal, and ledger guide |
| `/setup` | `initialize` |
| `/treasury` | `add_funds` and treasury read state |
| `/moderators` | Real on-chain moderator directory |
| `/moderators/new` | `register_moderator` |
| `/moderators/[id]/deactivate` | `deactivate_moderator` |
| `/evaluations` | Real evaluation queue |
| `/evaluations/new` | `request_evaluation` |
| `/evaluations/[id]` | Evaluation audit detail |
| `/evaluations/[id]/review` | `evaluate` |
| `/evaluations/[id]/appeal` | `submit_appeal` |
| `/evaluations/[id]/appeal/review` | `evaluate_appeal` |
| `/evaluations/[id]/finalize` | `finalize_evaluation` |
| `/activity` | Contract sync and Explorer evidence |

## Delivery order

1. Replace the contract with V2 and add static/lifecycle rule tests.
2. Clear the old address until V2 is redeployed.
3. Build the multi-page shell and typed contract actions without mock data.
4. Add scroll-triggered reveal motion and reduced-motion handling.
5. Run tests, lint, build, and visual checks on desktop/mobile.
6. After the user deploys V2, add the new address and test every write on Studio.
