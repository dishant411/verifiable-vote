# Roadmap: reuse first, evidence before claims

## 0. Evaluate and reproduce an existing application (current)

Delivered: pinned Helios checkout, locked dependencies, local synthetic election UI, password roster, encrypted test ballots, revote/tally fixture, public sample export, offline upstream proof checks, tampering/eligibility integration tests, explicit limitations.

Incomplete gates: PostgreSQL baseline suite; race-condition revoting behavior; browser E2E automation; independent protocol review; dependency vulnerability assessment. Current local configuration uses SQLite and eager tasks. It is not a deployment recipe.

## 1. Prove the full pilot workflow

Run PostgreSQL and the normal Celery queue in an isolated environment. Resolve fixture/backend issues without hiding test failures. Reproduce full browser encryption -> authentication -> cast -> revote -> close -> trustee ceremony -> result -> evidence download -> offline checks. Validate concurrent same-voter submissions and delayed verification jobs. Test malformed ballot shapes, tally races, cancellation, outage/recovery, and stale tracker handling. Record trustee and manifest fingerprints independently. Review full dependency lockfile and SBOM before any tagged release.

Select a separately maintained verifier implementation or validate cross-implementation test vectors. Public evidence must support review of voter eligibility/completeness under an explicit privacy policy. Avoid claiming an authoritative roster from pseudonymous aliases alone.

## 2. Decide privacy requirements before extending protocol

Obtain external review of voter/ballot linkage, metadata correlation, trustee collusion, malicious clients, randomness disclosure, and coercion. Helios fails the brief's no-identity-foreign-key requirement. Decide whether its documented privacy model fits the intended low-stakes pilot. Strong unlinkable issuance is a protocol change, not a separate database or a fake token. Reuse a reviewed design or change systems if required. Do not implement homemade cryptography.

Only build a thin evidence-download/inclusion-status UX if the demonstrated upstream flow leaves that gap. Avoid a new monorepo, auth service, credential issuer, blockchain, or custom ballot schema without evidence.

## 3. Low-stakes organization pilot

Before real rosters: external security review, accessibility/usability testing, privacy and retention policy, multi-trustee ceremony and recovery runbooks, reliable backups, voter support, operational rehearsal, and risk acceptance. Pilot with a club/nonprofit/association whose stakes and coercion environment fit the protocol. No government ID documents or biometric collection.

## 4. City advisory and participation

Consider Decidim for proposals, discussion, and participatory budgeting once voting evidence and governance are settled. City advisory use is not certification for binding elections. Login.gov production integration requires eligible government partnership/private contractor arrangement; it is not a blocker for synthetic testing. Identity proofing does not automatically confer election eligibility.

## 5. Public-election research (separate deployment class)

No certification promises. Any binding public-election work requires jurisdiction-specific legal/certification analysis, accessibility, independent cryptographic/security audits, procurement and operations, coercion review, and accepted paper/audit/recount procedures.
