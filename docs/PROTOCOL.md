# Protocol boundary

No new cryptography or anonymous credential protocol is defined here. Election manifests, encrypted ballots, trackers, trustee proofs and tally objects use the pinned Helios legacy datatypes and homomorphic workflow. Our versioned export envelope is `verifiable-vote/helios-demo/v1`; it packages existing public objects for a bounded offline experiment.

Flow: synthetic roster -> upstream password authentication -> browser encryption -> upstream ballot proof validation -> recorded ballot tracker -> most recent valid vote per voter -> encrypted aggregate -> server-trustee decryption proof -> released tally -> local export -> offline proof checks.

The automated sample encrypts via upstream Python APIs. Interactive voters use the existing browser booth. The offline verifier reuses the same upstream crypto implementation and cannot establish eligibility from pseudonymous exported aliases. It supports only the documented small demo, not arbitrary Helios elections.

The scope intentionally differs from the source brief's identity -> anonymous issuer -> ballot box model. No anonymous issuer/nullifier exists in this prototype. That design remains subject to external protocol review. The tracker is not a signed receipt. The election fingerprint is not an authenticated signature. Roster commitments and append-only public log integrity are not established.
