# Sherlock search-save investigation

Confirmed: ordinary saves work, but a filesystem error while saving terminates Sherlock and prevents later usernames from being searched.

## What was tested

The unmodified upstream search/save code ran against a local HTTP server with invented profiles. Five normal runs succeeded: TXT, CSV, XLSX, a nonexistent profile, and a two-username batch. Seven failure cases reproduced. Sample TXT, CSV, and XLSX contents were checked. The nonexistent-profile CSV contains only the header because default output filters out profiles not found.

Source commit: e40a45ec2a074b90703b3b4b842c8a3adbd6ada3. Versions and source status are recorded in [environment.json](environment.json). The installed Sherlock engine and desktop app were not modified.

This is a controlled local test, not an OS security sandbox. Each CLI process used a separate working directory. The harness restricts socket connections to loopback and stubs the automatic update check. It uses a local site manifest with remote exclusions disabled. No real people or external profile websites were searched.

## Results

Five normal runs exited successfully. Seven runs exited with code 1:

- Slash-containing username: TXT, CSV, and XLSX all failed because `a/b` becomes a pathname under a nonexistent `a` directory.
- Missing output parent: FileNotFoundError.
- Directory selected as the output filename: IsADirectoryError.
- Read-only output directory: PermissionError.
- Output folder name already occupied by a file: FileExistsError.

The full [results table](results-table.md) and [machine-readable summary](summary.json) record each case.

## Why it crashes

Sherlock queries each username and immediately writes reports within the same loop. TXT calls `open()` at sherlock.py:836, CSV calls `open()` at :853, and XLSX calls `to_excel()` at :927. Directory creation at :830 and :850 is also unprotected. These operations have no filesystem-error handler around them.

When saving fails, the exception escapes main() and Python exits with a traceback. The batch loop never reaches the next username. The request logs prove this: the successful batch queried first_demo and second_demo; all three slash-name failures queried only a/b and never requested second_demo.

This is a failure to save completed search results, rather than a crash while contacting a website.

## Saved evidence and reproduction

Every case under evidence/ contains stdout.log, stderr.log, requests.json, and saved-files/. Successful example reports are in evidence/save_txt/, evidence/save_csv/, and evidence/save_xlsx/.

Run the harness with the existing Sherlock virtualenv Python:

```sh
'python' run_sandbox.py
```

Set SHERLOCK_SOURCE to the upstream source clone when running this copy; see README.md for reproduction instructions. On rerun it reuses evidence folders; use a fresh copy for a clean reproduction. Profile URLs contain that run's temporary local server port.

## Relationship to our desktop app

Our Swift desktop app exports CSV itself using an atomic write inside a do/catch block (SherlockDesktop.swift:153–162). It rejects slash-containing usernames, and its search command does not enable upstream TXT/CSV/XLSX output. These tests reproduce an upstream CLI bug; they do not establish a crash in our native export. Failure testing of the native save dialog would be a separate check.

## Recommended next work

Catch directory-creation and report-write errors, explain which destination failed, and preserve remaining searches where appropriate. Define a final exit status for partial export failures. Add regression checks for every format, invalid destinations, and batch continuation. Atomic writes would help avoid incomplete files; interruption during writing was not tested here.

The behavior matches [upstream issue #3119](https://github.com/sherlock-project/sherlock/issues/3119). Proposed fixes already exist in [PR #3123](https://github.com/sherlock-project/sherlock/pull/3123) and [PR #3145](https://github.com/sherlock-project/sherlock/pull/3145). Review and test those before creating a duplicate fix. Neither proposed fix was applied or verified here. No upstream messages or pull requests were submitted.
