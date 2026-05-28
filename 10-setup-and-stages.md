# 10 · Project setup and stages

[← 09 The loop](./09-the-loop.md) · [Contents](./README.md) · Next: [11 Governance →](./11-governance.md)

This chapter covers two operational matters: what you set up once per project, and how the same flow runs at different depths as a product matures.

---

## One-time setup

Before the first feature, establish the foundation the whole project depends on. Done once, it makes every later checkpoint enforceable automatically.

| Item | File | Purpose |
|------|------|---------|
| Repository + pipeline | — | runs the gates on every change |
| Conventions | `CONVENTIONS.md` | naming, layout, language, formatter — the survivor layer |
| Model record | `MODEL_REGISTRY.md` | which AI model and version the project uses, for reproducibility and audit |
| Dependency allow-list | `dependencies.allowlist` | the packages the AI may use; the pipeline rejects others |
| Prompt playbook | `playbook/` | the six prompts from [Appendix B](./appendix-b-prompts.md) |

**Setup exit check**

- [ ] The pipeline runs and is green on the empty skeleton.
- [ ] The model is pinned.
- [ ] The allow-list exists and the pipeline fails on any package outside it.
- [ ] The playbook is present.

Do not start a feature until the pipeline is green. It is the thing that will enforce every later exit check without anyone having to remember to.

---

## Stages: the same flow at increasing depth

A *stage* is one pass through the flow at a chosen depth. The steps never change between stages; what changes is how deeply you run each one. The instinct to skip steps for an early prototype is right in spirit but wrong in form — you do not skip steps, you run them lightly.

### The depth matrix

Depth: **Deep** (full rigor) · **Core** (real but scoped) · **Light** (just enough) · **—** (skipped or stubbed).

| Step | Prototype | Proof of Concept | MVP | Production-Ready |
|------|:---------:|:----------------:|:---:|:----------------:|
| 1 Specify | Light | Deep (risky slice) | Deep | Deep |
| (design, if UI) | **Deep** | Light | Core | Deep |
| 2 Scenarios | Light | Core | Deep | Deep |
| 3 Contract | — | Core | Deep | Deep |
| 4 Tests | — | Core | Core | Deep |
| 5 Build | Light (throwaway) | Core | Core | Deep |
| 6 Verify | Light | Core | Core | Deep |
| Loop / operate | — | — | Light | Deep |
| **Typical time\*** | ~2–5 days | ~1–3 weeks | ~4–8 weeks | ~4–8+ weeks |
| **Code is** | disposable | disposable | kept | hardened |

\* *Ranges assume a small team on a single product slice. Scale by scope and by the number of parallel streams. The pace is set by judgment and review capacity, not by how fast the AI can type — adding more AI does not compress the human-led steps.*

### Stage by stage

**Prototype — prove the experience.** Run the design deeply and everything else lightly; the code is throwaway. The achievement is that a stakeholder reacts to something tangible and a go/no-go on the concept becomes possible. Do not expect real data, tests, or anything that survives.

**Proof of Concept — retire the biggest technical risk.** Run the contract, tests, and build *deeply but only on the single riskiest slice*. The achievement is evidence that the hardest unknown is solvable, which turns an MVP estimate from hopeful into credible. Do not expect breadth or polish.

**MVP — deliver value to real users.** Run the full flow at a narrow scope — the first complete loop, including light observation. The achievement is real users getting value while you learn from them. Do not expect scale or full operational rigor.

**Production-Ready — run safely at scale.** Run every step at full rigor and deepen the operate-and-learn loop: service objectives, incident response, tested rollback, gradual delivery. The achievement is a system that is tested, secure, observable, and supportable. Do not expect "zero defects"; expect managed risk with a working feedback loop.

### What carries forward

The durable thing is never the code:

| Transition | Discard | Keep |
|------------|---------|------|
| Prototype → POC | the prototype code | the validated experience (design, flows) |
| POC → MVP | the spike code | the validated approach + the risky-interface contract |
| MVP → Production | nothing | everything; the code is real and is hardened |

The survivor layer thickens as you move right: a prototype leaves you a validated design; a proof of concept adds a proven approach and a contract; the MVP adds real, kept code. By production, you are hardening, not rebuilding.
