# ModDAO V3 contract review

## Resolved security and product gaps

- The constructor binds administration to the deployer; no first-caller takeover exists.
- Every sender comparison uses normalized hexadecimal addresses.
- Treasury funding is payable native GEN custody, not a user-entered ledger mutation.
- Successful finalization transfers native GEN to the registered moderator wallet.
- Each evaluation reserves its maximum payout before review, so admin withdrawal cannot make an active ruling insolvent.
- Subjective reviews use comparative semantic consensus rather than byte equality.
- Evidence is fetched with `gl.nondet.web.render` and truncated before prompting.
- A 24-hour appeal window prevents immediate payout from bypassing the moderator.
- `NEEDS_EVIDENCE` has a bounded replacement path instead of becoming a dead state.
- Settlement records and aggregate funded/paid/withdrawn values are queryable on-chain.

## Lifecycle

`fund_treasury` -> `register_moderator` -> `request_evaluation` -> `evaluate` ->
optional `replace_evidence` or `submit_appeal` -> optional `evaluate_appeal` ->
`finalize_evaluation`.

ModDAO V3 must be deployed as a new contract because its storage and payment behavior
are not compatible with the previous V2 address.
