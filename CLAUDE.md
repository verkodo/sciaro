# CLAUDE.md – sciaro

Rules for working in this repository. This file is public: nothing personal goes here.

## What this is

sciaro – the body of knowledge written in verkodo: mathematics (`math/`) and German law (`de/`), later European law
(`eu/`). Content only – the language and its tools are verkodo/verkodo, small samples of the language are its
`examples/`, never here. Everything here is meant to be right: sourced, checked, open points marked.

## Rules

- Modules named after their path (`math/analysis/sequences.vk` → `math.analysis.sequences`, `de/estg/p32a.vk` →
  `de.estg.p32a`); one section or article of law per file; the law of a Land below its ISO code (`de/bb/ftg/p2.vk`).
- What depends on a place – public holidays – is computed per Land from its own act; Länder not written yet are
  inputs, never guessed.
- Law from the official text (gesetze-im-internet.de for federal law): address and retrieval date in the header, the
  version covered, earlier versions kept with `replaces`. Not legal or tax advice – say where a reading is a choice.
- Claims need a source; unverified statements are marked **OPEN**. Missing proofs stay visible (Lean: open), never
  assumed.
- Every `.vk` file starts with an SPDX header for CC BY 4.0 (the identifier `CC-BY-4.0`); REUSE is checked in CI.
- English in comments, docs and commits; labels and texts in the content's languages. Commits signed off
  (`git commit -s`).

## Checks

```sh
verkodo check .                      # CI does this with the verkodo version named in .github/workflows/ci.yml
(cd lean && lake exe cache get)      # once: Mathlib's build
verkodo prove . --lean lean          # Lean – CI does this too
```
