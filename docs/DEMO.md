# Demo walkthrough

1. Run `bash scripts/demo.sh setup && bash scripts/demo.sh serve` from the repository root.
2. Open http://localhost:8000/helios/e/synthetic-demo-v2. Read the synthetic-research and revoting notice.
3. Select “Vote in this election”, start the booth, choose Garden or Library, review and encrypt, then submit.
4. Authenticate as `alice` using the ignored local credentials file. Save the tracker and check its ballot page. Repeat as `bob`. Use separate browser sessions or the upstream logout/cast-done behavior.
5. Alice may vote again. Her latest valid ballot replaces her previous counted ballot; the old tracker can still refer to submission history but must not be treated as final inclusion.
6. Use the site login/Dev Login for the synthetic administrator. Open the election page; compute tally, combine decryptions and release results. Stop new casting once tally begins.
7. Export with `bash scripts/demo.sh export --short-name synthetic-demo-v2 --output "$PWD/.runtime/manual-election.json"`.
8. Stop the server. Run `bash scripts/demo.sh verify "$PWD/.runtime/manual-election.json" --expected-fingerprint YOUR_OPENING_FINGERPRINT --tracker YOUR_FINAL_TRACKER`.

The automated `sample` action makes a separate completed election; it does not close the manual election. It intentionally generates fresh keys and ciphertexts. The checked-in sample is a stable public fixture; its fingerprint is recorded in README. You can clone this repo on another machine, set up dependencies once, and verify without the originating database/server. Keep a trustworthy copy of the software and opening fingerprint.

Stop the server with Ctrl-C. No public deployment has been made. If a synthetic election is already tallied, choose a new short name via the Python seed action rather than trying to reopen it. Existing seed data is retained across starts.

## Local interface

The demo includes a responsive election directory, election overview, themed Helios
booth, authentication page, and ballot receipt with copy/download controls.
Presentation assets and template overrides live in `demo/ui/`. `ui_urls.py` and
`ui_middleware.py` serve these local assets; the pinned upstream checkout, ballot
handlers, encryption libraries, and proof APIs are not edited. Administrator pages
retain the upstream actions within the shared visual theme.

Open `http://localhost:8000/` for the election directory. Restart the demo server
after changing templates because Django caches compiled templates. No external
fonts or UI service is required.
