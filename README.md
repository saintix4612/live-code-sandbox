# Sherlock: search-save crash investigation

**Contribution type:** Bug investigation and reproducible evidence.

**Method:** Live code review with local sandbox testing.

Here, "live code review" means inspecting the current upstream source and running its actual search/save code. Synthetic profiles were served by a local HTTP server; no real people or external profile websites were searched. This was a controlled local harness, not an operating-system security sandbox.

**Status:** Investigated and reproduced locally. No fix submitted or accepted upstream.

**Finding:** Unhandled filesystem errors during TXT, CSV, and XLSX export stop the program and skip remaining usernames.

**Validation:** Five normal runs passed; seven save-failure cases reproduced. Saved report contents and HTTP request logs were checked.

**Source reviewed:** [Sherlock commit e40a45e](https://github.com/sherlock-project/sherlock/tree/e40a45ec2a074b90703b3b4b842c8a3adbd6ada3).

## Evidence

- [Full report](REPORT.md)
- [Results table](results-table.md)
- [Structured results](summary.json)
- [Environment and versions](environment.json)
- [Reproduction script](run_sandbox.py)
- [Successful TXT example](evidence/save_txt/saved-files/saved_demo.txt)
- [Successful CSV example](evidence/save_csv/saved-files/saved_demo.csv)
- [Successful Excel example](evidence/save_xlsx/saved-files/saved_demo.xlsx)
- [Example crash log](evidence/slash_txt_batch/stderr.log)

The local profile links are synthetic evidence and are not permanent public URLs. Local workspace paths in published logs are replaced with <workspace>.

## Reproducing from this contribution folder

Use Python 3.14 with the dependencies in requirements.txt. Exact versions used in the investigation are listed in environment.json. Clone the pinned upstream source into an isolated working directory and run the harness with its source path:

```sh
git clone https://github.com/sherlock-project/sherlock.git sherlock-source
git -C sherlock-source checkout e40a45ec2a074b90703b3b4b842c8a3adbd6ada3
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
SHERLOCK_SOURCE="$PWD/sherlock-source" python run_sandbox.py
```

The harness uses existing evidence directories on rerun; use a fresh copy for a clean reproduction.

## Credit

Sherlock is maintained by the Sherlock Project and was originally created by Siddharth Dushantha. This record documents an investigation for saintix4612, carried out with assistance from OpenAI Codex. The upstream behavior was already reported in [issue #3119](https://github.com/sherlock-project/sherlock/issues/3119); this is independent reproduction, not a claim of original discovery.
