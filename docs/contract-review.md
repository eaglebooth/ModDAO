# ModDAO Contract Review

Review date: 2026-07-12

## Critical findings

- `strict_eq` compares a JSON result containing free-form `comment`, so validators can
  agree on performance but fail consensus because their wording differs.
- `initialize` can be called repeatedly and accepts any admin address.
- Treasury funding, moderator registration, and deactivation have no admin check.
- Any caller can request an evaluation for any moderator.
- Evaluation deducts treasury immediately, leaving no review or appeal stage.
- Unreadable web evidence throws instead of producing a safe `NEEDS_EVIDENCE` state.
- The contract records a payout ledger but does not transfer a stablecoin; product copy
  must not claim that a token transfer happened.
- The frontend, README, env files, and client fallback contain different contract
  addresses, making deployment verification unreliable.
- Production UI includes local scenario files and prefilled wallets instead of an
  honest empty state.

## Required V2 lifecycle

`initialize` -> `add_funds` -> `register_moderator` -> `request_evaluation` ->
`evaluate` -> optional `submit_appeal` -> optional `evaluate_appeal` ->
`finalize_evaluation`.

Every write has an authorization guard and explicit status transition. Subjective
reviews use `prompt_comparative`, and finalization mutates the treasury exactly once.
