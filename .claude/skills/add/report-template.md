# Chat reports — the decision-point template (for the AI, not for add.py)

The engine renders artifacts (`report`, `report --decide`, `status`); this file
governs the CHAT MESSAGE you wrap around them. The digest is the artifact BEHIND
your presentation, never a replacement for it — and your prose is never a
replacement for the digest.

Use it every time you report at or near a decision point: an intake proposal, a
bundle approval, a verify gate, a task completion, a milestone close.

## The five blocks, in order

```
SUMMARY   one line: intent + target + where we are
DECISION  what you need from the human (or "none — FYI")
⚠ FLAGS   lowest-confidence first, why + cost-if-wrong
EVIDENCE  small table: tests · gates · parity · check — engine-sourced
NEXT      the single next action + what it unlocks
```

1. **SUMMARY** — one line carrying intent + target + position, e.g.
   "v13 task 2/3 — tests-declared-fallback is green, gate PASS." The reader
   knows where they are before they read anything else.
2. **DECISION** — the question the human must answer, stated plainly; exactly
   one decision per report, or an explicit "none — FYI". If a decision exists,
   ask it AFTER everything below has been shown (show-before-ask).
3. **⚠ FLAGS** — lowest-confidence first, each with *why* confidence is lowest and the
   *cost if wrong*. Where TASK.md markers exist (`⚠` / `- [~]` / `- [ ]`),
   quote them verbatim and keep their document order — extraction ≠ judgment.
4. **EVIDENCE** — engine-sourced facts pasted from `add.py` output, never
   re-typed from memory. If your prose and the engine disagree, the engine
   wins: fix the engine or the data, not the sentence.
5. **NEXT** — one action and what it unlocks. Mirror the rollup's DECIDE NEXT
   line when it is right; overrule it only with a stated reason (e.g. planned
   tasks the state file cannot see yet).

**The ask itself** — when block 2's decision becomes a literal question component
(option picker, numbered menu), compose it as a summary: the detail stays in the
report above, the question carries intent + what "yes" means + the flag count.

## Hard rules

<constraints>
- **Summary-first.** Never bury the decision under a task list or a diff.
- **Show before ask.** Render the artifact (digest · diff · report) before any
  approval question; the human decides on what they can see.
- **Never pre-stamp a human decision point.** Freeze / gate / lock fields stay DRAFT or
  blank until the answer returns: show → ask → stamp → advance. An artifact
  must never claim an approval that has not happened.
- **One report per decision point.** After an approval, point at the frozen artifact —
  do not re-render the whole bundle.
- **Honest scope.** "Done" means the request, not the last task: report
  "task 2/3", never "done" while approved scope remains.
- **The question is a summary, never the artifact.** Every approval ask carries
  two layers: a compact SUMMARY · DECISION · ⚠ FLAGS block sits in chat
  immediately before the ask (positional), and the question text itself is a
  summary of two lines at most — intent + what "yes" means + the flag count —
  pointing at the report above (compositional). The full bundle, diff, or
  artifact lives only in the chat report; a question that re-carries it buries
  the decision.
</constraints>
