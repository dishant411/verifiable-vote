# Upstream assessment

Inspected 2026-10-02. Candidate: [benadida/helios-server](https://github.com/benadida/helios-server).

Pinned revision: `88621e3196961ec03fe54bbd3a1c2196e715e9a2`, committed 2026-08-15, “Add CSRF protection to state-changing views (#496)”. This is recent maintenance evidence, not an assurance of ongoing support, formal audit, certification, or absence of vulnerabilities. The repository contains a Python 3.13/uv lockfile, Django 5.2.9, browser booth, verifier UI, and upstream CI using PostgreSQL 16. No tagged release was selected: the exact commit and frozen lockfile define this experiment.

License: Apache-2.0, verified from upstream LICENSE. This wrapper uses Apache-2.0. Preserve upstream licensing when distributing downloaded code; the bootstrap leaves upstream LICENSE intact. No AGPL civic software is embedded. Transitive dependency licensing and vulnerability review remain release gates.

## Why Helios first

It is a complete voting application with existing UI and authentication, not merely a cryptographic toolkit. Its testable flow gets us to encrypted ballots and a tally faster than assembling a fresh system. [Upstream FAQ](https://vote.heliosvoting.org/faq) describes browser encryption and ballot trackers, and recommends against high-stakes public-office Internet elections.

ElectionGuard remains an alternative cryptographic toolkit if a reviewed gap requires a different architecture; adding it alongside Helios is not automatically helpful. Decidim is deferred until civic deliberation/participation becomes the actual task.

## Source findings

- `helios/models.py`: `Voter.user`, voter email/login fields, `Voter.vote`, and `CastVote.voter` create voter-to-ciphertext links. `CastVote.cast_ip` stores submission IP. Aliases do not remove server-side linkage.
- `Voter.store_vote`: replaces the counted vote according to cast time. `Election.compute_tally` iterates the current non-empty voter votes. This is revoting, not a spent anonymous token/nullifier.
- `CastVote.verify_and_store`: verifies ballot proofs before storing the counted vote; quarantined votes require release. Race handling needs separate PostgreSQL/queue validation.
- `Election.freeze`: combines trustee public keys and freezes election configuration. `generate_voters_hash` is a TODO that currently returns without generating a voter-list hash. Do not claim roster completeness or signed roster evidence.
- `generate_trustee`/`helios_trustee_decrypt`: default Helios trustee stores a secret key in the server database. Our demo uses this convenience. A single operator has decryption capability; an unavailable admin UI action does not cryptographically prevent individual decryption.
- `helios/workflows/homomorphic.py`: verifies election UUID/hash, answer proofs and subgroup membership; implements aggregate tally and decryption proof checks. We call these methods directly rather than writing cryptography.
- `helios/datatypes/legacy.py`: cast ballot serialization excludes answer/randomness; audit serialization can include them. Our export excludes those fields. Disclosure of encryption randomness can provide transferable choice evidence; excluding it from one export does not establish receipt-freeness.
- `heliosverifier/verify.html`: upstream verifier fetches live election endpoints. Our minimal offline harness uses Python public proof APIs and local exported evidence. This is operational independence from the server, not implementation independence.

All source links can be inspected at the pinned [commit](https://github.com/benadida/helios-server/tree/88621e3196961ec03fe54bbd3a1c2196e715e9a2).
