# Election record

`evidence/sample-election.json` is a checked-in synthetic example. `scripts/demo.sh export` writes a local download-ready JSON file after results are released. This is not a new public server endpoint.

Envelope fields:

| Field | Meaning |
| --- | --- |
| protocolVersion | Exact wrapper version |
| election | Public Helios legacy election object, including public key and frozen configuration |
| electionFingerprint | Upstream election hash; compare against independently recorded opening fingerprint |
| ballots | Counted latest ballots only: alias, tracker and public encrypted vote/proofs |
| trustees | Upstream public trustee key, knowledge proof, decryption factors/proofs; synthetic email only |
| encryptedTally | Public encrypted aggregate and number tallied |
| result | Published tally checked against decryption |

No private trustee key, password, voter login/email, ballot plaintext/randomness, or IP address is included by the exporter. This does not anonymize the underlying Helios databases. Trustee contact fields are public upstream data; never export real-person records without a reviewed policy.

The record omits superseded submissions, authoritative roster evidence, revoked credentials, full event history, signatures, and inclusion/completeness commitments. Uniqueness of aliases inside one package does not prove one eligible human per ballot. Voters should check their final tracker against authentic final evidence. Internally consistent adversarial evidence remains possible if the trusted opening fingerprint/roster/publication is not established independently.

Verification fails for changed ciphertext (including with recomputed tracker), forged tracker, wrong manifest fingerprint, changed result/proof/aggregate, removed or duplicated ballot, and unexpected plaintext fields in our tested mutations. This is not exhaustive validation of all malicious JSON or upstream proof implementations.
