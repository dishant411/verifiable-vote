# Privacy

Use synthetic `example.invalid` contacts and test accounts only. No biometrics, government ID images or identity-proofing documents are collected by these wrappers. Upstream credentials, server trustee keys and the database stay in ignored `.runtime/`; credentials file permissions are 0600. Never publish `.runtime/` or a database backup.

The application retains voter-to-ciphertext links, submission timestamps and IP addresses according to upstream behavior. Local HTTP access logs may record URLs. Alias export is data minimization, not strong anonymity. The demo disables external error telemetry and outbound email. It does not establish a production retention policy, log audit, data protection agreement, or unlinkable issuance. Do not upload real roster data.
