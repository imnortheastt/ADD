# Diagram pipeline (reusable)

The book's four hand-drawn infographics are **generated**, not hand-edited, so they
stay regenerable as the method evolves. The source of truth is the book chapters; these
prompts render a faithful picture of them, and `CHECKLIST.md` is the acceptance gate.

| Diagram | Prompt | Renders to (all three doc trees) | Chapter |
|---------|--------|----------------------------------|---------|
| 7-phase flow | `prompt-flow.txt` | `add-flow.png` | ch02 |
| Five competencies | `prompt-competencies.txt` | `add-competencies.png` | ch00 / ch14 |
| Engine on the foundation | `prompt-foundation.txt` | `add-foundation.png` | ch14 |
| Three tiers | `prompt-hierarchy.txt` | `add-hierarchy.png` | ch14 / appendix F |

## Render

Uses the `nanobanana-rest` skill (Google Gemini image API; key in `~/.nanobanana.env`):

```bash
SKILL=~/.claude/skills/nanobanana-rest/scripts/nanobanana_rest.py
python3 "$SKILL" \
  --prompt "$(cat add-method/diagrams/prompt-flow.txt)" \
  --model gemini-3-pro-image-preview \
  --aspect-ratio 16:9 --image-size 2K \
  --output add-flow.png
```

`gemini-3-pro-image-preview` for the final (highest label fidelity); a flash model is
fine while iterating. The four diagrams are 16:9 landscape.

## Accept (the gate is text accuracy)

Image models garble small text — **this is the failure mode to watch.** After every
render, check **every glyph** against `CHECKLIST.md` (phase names, the acronyms
DDD/SDD/UDD/TDD/ADD, the dashed-arrow labels). A misspelled, dropped, or duplicated
label = reject and re-render. Expect to render a few times before one passes.

## Propagate

A passing PNG is copied byte-identical into all three doc trees:

```bash
for d in . add-method/docs .add/docs; do cp add-flow.png "$d/add-flow.png"; done
```

The machine-checkable half of the flow diagram (mermaid labels match the engine phases;
the loopback rule is both written and drawn; the three trees agree) is pinned by
`add-method/tooling/test_flow_diagram.py`. The raster itself is a human visual gate.
