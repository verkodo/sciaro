# sciaro

**Knowledge written formally, checked by machine** – mathematics and law in [verkodo](https://github.com/verkodo/verkodo).
*Sciaro* is Esperanto for a body of knowledge: what a person, a group or a society knows about a subject.

It is at its beginning. What is here is meant to be right, not to show the language – small samples of that are in
[verkodo's examples](https://github.com/verkodo/verkodo/tree/main/examples).

| Folder | What |
|---|---|
| [math/](math/) | mathematics, one folder per field |
| [de/](de/) | German law, one folder per act; the law of a Land below its code (`de/bb/` for Brandenburg) |
| [calendar/](calendar/) | what bodies of law count with: Easter Sunday |
| [tests/](tests/) | results against official tables, through `verkodo eval` |

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
cargo install verkodo     # 0.3 or later; Rust 1.99 or later
verkodo check .           # parse, resolve and check every file
```

Lean checks with the Lean project in `lean/` (Mathlib, pinned like verkodo's): `lake exe cache get` there once, then
`verkodo prove . --lean lean`. CI does both on every change, with the version of verkodo it names.

## Licence

The knowledge here is under [CC BY 4.0](LICENSES/CC-BY-4.0.txt), the CI workflow under [MIT](LICENSES/MIT.txt).
Published by [falkOSS](https://falkoss.org).
