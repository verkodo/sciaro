# de

German law, one folder per act, named by its official abbreviation in lower case (`estg/`, `ustg/`), one file per
section or article (`p32a.vk` for § 32a, `a3.vk` for Art. 3); modules are named after the path: `de.estg.p32a`.
The law of a Land lives below the Land's ISO 3166-2 code (`bb/ftg/` for Brandenburg's Feiertagsgesetz); the Länder
themselves are the enumeration in `states.vk`.
Each file names the official text it was written from (https://www.gesetze-im-internet.de for federal law), the day
it was retrieved and the version it covers; earlier versions are kept with `replaces`.

| File | What | Lean |
|---|---|---|
| [ustg/p19.vk](ustg/p19.vk) | § 19 UStG, small business scheme – the version from 2025-01-01, paragraphs 1 to 6, with the deadlines of paragraphs 3 and 5 | 68 checked, 0 open |
| [bgb/p193.vk](bgb/p193.vk) | § 193 BGB – a day to act that falls on a Sunday, public holiday or Saturday moves to the next working day | checked |
| [ao/p108.vk](ao/p108.vk) | § 108 (3) AO – the same for the end of a period in tax law | checked |
| [einigvtr/a2.vk](einigvtr/a2.vk) | Art. 2 (2) Einigungsvertrag – the Day of German Unity | checked |
| [bb/ftg/p2.vk](bb/ftg/p2.vk) | § 2 (1) Feiertagsgesetz Brandenburg – the public holidays in Brandenburg | checked |
| [states.vk](states.vk) | the 16 Länder | – |
| [bmf/pap_lst_2026.vk](bmf/pap_lst_2026.vk) | the wage tax 2026 by the BMF's programme flowchart (annual computation): provident lump sum, allowances, tax classes I to VI, splitting – all 516 values of its two test tables agree (`tests/lst_2026.py`) | checked |

Public holidays of the other Länder: OPEN, one module per Land as its act is written; until then § 193 BGB takes
them as an input.

Not legal or tax advice.
