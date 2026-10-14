# Maintaining the 4 Mina Parent Hub

The published page (`index.html`) is encrypted. The readable page is never committed.

1. `HUB_CODE=<class code> python3 tools/unlock.py` → recreates `tools/page.html`
2. Edit the `CONTENT` block at the top of the script in `tools/page.html`
   (`UPDATED`, `WEEK_BLOCKS`, `TODAY_NOTES`, `NO_ECA`, `PE_GROUPS`, `ROTATION`,
   `EVENTS`, `NEWSLETTER`, `FAQ`, `CONTACTS`, `TIMETABLE`).
3. `HUB_CODE=<class code> python3 tools/build.py` → rewrites `index.html`
4. Commit `index.html` only, then push.

Requires `pip install cryptography`.
