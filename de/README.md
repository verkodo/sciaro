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
| [bmf/pap_lst_2026.vk](bmf/pap_lst_2026.vk) | the wage tax 2026 by the BMF's programme flowchart (Anlage 1), complete: every pay period, pensions and the relief for old age, allowances and additions, the factor method, other emoluments, solidarity surcharge and church tax base – its two test tables (516 values), five cases of the BMF's calculator and 600 cases computed by the BMF's machine-readable flowchart agree (`tests/lst_2026.py`) | checked |
| [bmf/pap_lst_tab_2026.vk](bmf/pap_lst_tab_2026.vk) | the wage tax tables 2026 (Anlage 2): one entry per step of 36 euros, general and special tables – its two test tables (516 values) and both worked examples agree | checked |
| [bmf/pap_lst_dba_2026.vk](bmf/pap_lst_dba_2026.vk) | the wage tax on pensions limited by the treaties with Türkiye, Norway and Spain (Anlage 3) – its test table (258 values) agrees; other payments and allowances checked only by reading (OPEN) | checked |

Public holidays of the other Länder: OPEN, one module per Land as its act is written; until then § 193 BGB takes
them as an input.

Not legal or tax advice.
