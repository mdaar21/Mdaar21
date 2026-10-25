# Workflow and routing

1. Requirement Analysis: record task, acceptance criteria, authorized assets and constraints.
2. Independent Planning: spawn fresh expert contexts with no other opinions; save independent plans.
3. Department Review: collect plans and objections; choose implementation councils without altering votes.
4. Implementation: assign owners; serialize shared-file writes or isolate worktrees. Freeze deliverables afterward.
5. Automated Testing: execute relevant checks; preserve commands, exit codes and output as evidence.
6. Devil's Advocate Review: use $elite50-devils-advocate; record supported counterexamples.
7. Red Team Review: use $elite50-red-team within authorized scope.
8. Evidence Verification: use $elite50-evidence-gate; distinguish content truth from hash integrity.
9. Independent Reassessment: repair supported problems, create new snapshot, reassess independently.
10. Performance Comparison: use $elite50-auto-improvement with reproducible baseline/candidate measurements, or evidence-backed reason no measurable performance dimension applies.
11. Final Audit: use $elite50-final-audit; verify completeness, current evidence and runtime participation.
12. Unanimous Voting: collect fifty actual final responses on the same version; import faithfully with reasons and evidence. A fresh context can reassess its own prior vote but must not impersonate a different expert runtime. Preserve original response artifacts.
13. Final Delivery: emit THE ELITE 50 — FINAL REPORT with Task, Participating Councils, Solution Version, Experts Approved X/50, Experts Rejected, Experts Requiring Evidence, Changed Votes, Reasons for Vote Changes, Tests Executed, Remaining Risks, Consensus Status and Final Decision.

## Routing

All councils share all six systems. Route by the council slug in experts.json to installed skill named elite50-<slug>, resolved through the host skill registry. Scope implementation to relevant councils; full consensus always requires all fifty assessors.

## Bounded correction

Default to three correction rounds. Resolve objections with new evidence, not majority voting. New reliable evidence, evaluation errors, changed solution, newly passed tests and new risks can justify a decision change; group pressure cannot. After the budget, return PENDING/BLOCKED with unresolved items and useful artifacts.

## Host bridge

No provider-specific subprocess or API key is assumed. In a host with collaboration tools, spawn one expert with fork_turns=none where possible, supply its task packet and definition and no prior votes, record the returned ID via register, then collect its structured response. With seven slots including coordinator, use at most six workers. A project engine is a ledger and dispatcher packet generator; it does not itself run models. Runtime IDs are operator attestations, not authenticated credentials. Do not describe a registered string alone as verified model execution.
