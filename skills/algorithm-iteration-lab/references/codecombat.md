# CodeCombat adapter notes

These notes come from the 2026 Chaotic Crossing workflow. They describe pitfalls and how to check them, not a guarantee that a current arena has the same rules or limits.

## Runtime boundary

CodeCombat Python is executed by the game's interpreter. `hero`, `params`, player views, callbacks and movement methods are injected by the game. Ordinary CPython syntax validation cannot prove a complete match runs; forward function references or `global` placement can also differ between game and CPython semantics.

Use the arena's actual parser/transpiler when available. Do not reorder callbacks or rewrite the submission merely to make desktop Python execution work. Preserve originals and record any intentional compatibility edit.

## Establish current truth

Identify the arena, rule/engine bundle version, captured input, code for both teams, language and seed. Inspect only the supplied or in-scope material. Keep captured sessions, credentials, account identifiers and other players' private data out of a public package.

Historical debugging found frame-blocking behavior different from the player documentation, per-thread interpreter limits, and lazy loading of the Python parser. Verify these behaviors in the current runtime before designing around them. Do not hard-code “3 million ops”, a frame rate or release radius into a general-purpose acceptance rule without current evidence.

An empty AST or missing language bundle is a broken harness, not a weak bot. A worker that exits without a complete engine result is an error, not a scored game.

## Minimum replay evidence

For each baseline/candidate comparison, retain:

- Exact source snapshots and runtime identity; reuse one identity checksum only when needed for replay integrity.
- Team side, seed, timeout and command; start each match in its own process when using the historical harness with state contamination.
- Parsed score, the current tie-break fields, frame/end status, stderr and relevant interpreter errors.
- Whether the observation came from the official engine, an approximation, a fixture or a live match.

Use an existing local runner rather than downloading a new engine by default. Read its CLI and environment handling first: paths, language selection and verdict logic vary. If it requires a payload or bundle not supplied, list the exact missing artifact and mark the official replay `NOT_RUN`.

## Analyze losses before changing strategy

1. Is the failed match using the same submission and opponent versions? A current snapshot cannot automatically reconstruct a historical match.
2. Did a coach or player thread hit a limit or stop acting? Distinguish this from losing tactically.
3. Are coordinates mirrored differently for actions and views? Test each side, do not assume symmetry.
4. Are possession, immunity, capture and clearance rules represented correctly in the observation?
5. Is a tied score decided by fans/activity or another rule? Read the current verdict code, not just a printed score.

Static index defects can be real even if a match still happens to be won. Fixing such a defect is a correctness result; promoting that fix as a stronger competitive version requires the paired match gates.

## Acceptance discipline

Use the target loss plus a small set of wins that must not be lost. Add self-mirror and previous deployed versions only where they answer a real question. After gates pass, test the wider arena-relevant distribution and both team sides. Seeds should cover actual randomness; do not assume seed 0 is universal or add redundant seeds without reason.

Refresh opponents only if requested and in scope, then freeze that evaluation snapshot. Do not let baseline and candidate see different live versions during one comparison. Report stale data honestly rather than fetching unrelated accounts.

Publishing and tournament submission are separate actions. A user's prize statement does not prove that every archived variant was their final winning submission; retain that distinction in public documentation.
