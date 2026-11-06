# sciaro

**Knowledge written formally, checked by machine** – mathematics and law in [verkodo](https://github.com/verkodo/verkodo).
*Sciaro* is Esperanto for a body of knowledge: what a person, a group or a society knows about a subject.

It is at its beginning. What is here is meant to be right, not to show the language – small samples of that are in
[verkodo's examples](https://github.com/verkodo/verkodo/tree/main/examples).

| Folder | What |
|---|---|
| [math/](math/) | mathematics, one folder per field |
| [de/](de/) | German law, one folder per act |

European law follows in `eu/`.

## Rules

- **Sources.** Law is written from the official text, named in the file's header with its address and the day it was
  retrieved; mathematics names the textbook or paper where it is not standard. What is not checked against a source
  is marked **OPEN**.
- **Not legal or tax advice.** A formalisation says how a provision was read; where a reading is a choice, the file
  says so.
- **Lean decides.** Definitions, bridges and proofs are checked by Lean 4 with Mathlib (`verkodo prove`); a proof that
  is missing stays open, never silently assumed.
- English in comments and commits, labels and texts in the languages of the content; commits signed off
  (`git commit -s`, [DCO](https://developercertificate.org/)).

## Check

```sh
cargo install verkodo --git https://github.com/verkodo/verkodo   # Rust 1.99 or later; 0.2 on crates.io does not know every form used here
verkodo check .           # parse, resolve and check every file
```

Lean's check needs verkodo's Lean project (`lean/` in verkodo/verkodo, with Mathlib): `verkodo prove .` there.
CI runs `verkodo check` with the commit of verkodo it names; Lean is not run in CI yet (**OPEN**).

## Licence

The knowledge here is under [CC BY 4.0](LICENSES/CC-BY-4.0.txt), the CI workflow under [MIT](LICENSES/MIT.txt).
Published by [falkOSS](https://falkoss.org).
