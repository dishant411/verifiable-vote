# Threat model and limitations

Scope: synthetic, non-government, loopback-only research demonstration. Assets: eligibility roster/passwords, ballot secrecy, election configuration, counted ballot set, key material, authentic public evidence, availability. Actors: voters, administrators, server/trustees, observers, malicious clients, coercers and attackers with database or browser access.

| Threat | Existing control / experiment | Unresolved risk |
| --- | --- | --- |
| Unknown voter | Closed roster and upstream election-specific password authentication tested | Roster administrator controls eligibility; no real-person uniqueness |
| Repeated submissions | Latest valid ballot counted; sequential revote tested | Concurrent writes/jobs and close/tally races not tested |
| Altered ballot or manifest | Upstream proofs, fingerprint and tracker checks | Dishonest server can supply different valid election; external fingerprint comparison needed |
| Altered aggregate/result | Recompute aggregate and upstream trustee proof/decryption checks | Same crypto implementation; external review required |
| Missing ballots | Counted tracker inclusion check | No authenticated complete roster or all-submission log in minimal export |
| Server/database compromise | Browser encrypts before submission | Server links voters to ciphertexts/IP; server-held demo trustee can decrypt individually |
| Malicious browser/script | Upstream audited-ballot mechanism exists | Our tests do not establish cast-as-intended; script supply chain/device compromise remains |
| Coercion/vote buying | Revoting can replace a prior ballot | Coercer can watch final voting or demand randomness; no receipt-freeness/coercion-resistance claim |
| Metadata correlation | Minimal export omits IP and login metadata | Internal databases/access logs/timing still expose links |
| Credential theft/recovery | Existing password auth | No new recovery/reissue design, rate-limit validation, passkeys, or identity proofing |
| Trustee collusion or outage | Upstream multi-trustee capabilities exist | Demo is one server trustee; no independent key ceremony or threshold recovery |

## Boundaries

A ballot tracker is a ciphertext fingerprint, not proof of eligibility, authentic election origin, or coercion resistance. Separate databases would not by themselves create unlinkability. Aliases are pseudonyms. Encryption does not make the operator incapable of linking identities to ciphertexts. One server trustee is not distributed trust.

The brief's desired anonymous credentials/no direct voter FK are **not met by Helios**. This is a documented evaluation result; no fake credential layer hides it. Do not use real IDs, face templates, selfies, or real rosters in this demo. Face ID/passkeys may unlock local keys but do not prove entitlement to vote.

## Before exposing beyond loopback

Replace the demo configuration with a separately reviewed deployment. Dev Login, SQLite, eager tasks, debug mode, in-memory email, single trustee, and this local secret storage are development conveniences. Review authentication/session protections, CSRF, TLS, dependency vulnerabilities, browser integrity, evidence publication, incident response, accessibility, privacy, and key custody. Do not claim this harness is ready for real organization or government elections.
