# Workflow: Debug Issue

1. **Reproduce & Isolate**: Reproduce the issue with the smallest failing test, command, or narrow probe.
2. **Review Refuted Hypotheses**: Check `memory-bank/activeContext.md` and `memory-bank/risks.md` to ensure you do not retry already-disproven theories.
3. **Formulate Falsifiable Hypothesis**: State the suspected root cause, the expected baseline failure, and what observable output will change once fixed.
4. **Apply Escalation Ladder**:
   - **Tier 1 (Surgical Fix)**: Direct inline fix when root cause is clear.
   - **Tier 2 (Scratch Reproduction Script)**: Standalone script in `tmp/` to isolate external dependencies or ambiguous library quirks.
   - **Tier 3 (Diagnostic Test Harness)**: Targeted unit/mock test suite for concurrency, state machines, or edge cases.
   - **Tier 4 (Model & Architecture Redesign)**: Deep state or interface overhaul if lower tiers fail to stabilize.
5. **Verify & Learn from Misses**: Run verification. If the fix fails, treat the miss as a high-value signal: record the dead hypothesis and killing evidence under `Refuted Hypotheses` in `memory-bank/activeContext.md` before attempting another angle.
6. **Add Regression Coverage**: Add or update automated regression tests to permanently lock in the fix.
7. **Commit & Document**: Commit atomically (`fix(...)`) and record newly discovered patterns in `memory-bank/risks.md`.