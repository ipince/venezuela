

## Directory Structure

Looks like result pages are of the form:

`resultado_municipal_2013/[r|pp|lvg]/<index>/reg_<code>.html`

* Hierarchy is Country -> State -> Municipality -> Parish -> Center -> Table.
* `r` contains the country, state, and municipality, and parish-level summaries.
* `pp` contains the center-level summaries.
* `lvg` contains the table-level summaries.
* Each subdirectory (`r`, `pp`, and `lvg`) contains many files, sometimes in the thousands. This is where `index` comes in. It's a directory whose name is a number between 1 and n and is used to distribute files across subdirectories.
  * The `r` directory contains subdirs `1` and `2`. `1` contains country level summary, as well as state, municipality, and parish summaries for the first 10 states. The `2` subdir contains the state, municipality, and parish summaries for the remaining 14 states.
  * The `pp` directory contains subdirs from `1` to `15`. The subdirs `1` thru `14` all contain 1000 files each, while the `15` subdir contains 272 files. That is, there are 14,272 tables. The files are dropped into the directories sorted by their `code` (e.g. the first 1000 files when sorted by `code` end up in subdir `1`).
  * The `lvg` directory contains 
* The `code` is a prefix-based identifier for each summary level. It can be 6, 9, or 12 characters long and is of the form `<state><muni><parish>[<center><table>]`. The state, muni, and parish codes are all 2 digits long, while the center and table codes are 3 digits long. Codes for summaries of parish level or higher only have 6 digits, codes for centers have 9, and codes for specific tables have the full 12. Lastly, the code is prefix-based, so to identify the aggregated summary for some state, the code could be `122300`, identifying the summary of parish 23 at state 12. As such, code `000000` corresponds to the country level summary.
