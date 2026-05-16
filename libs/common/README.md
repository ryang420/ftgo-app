# common

Shared utilities for cross-cutting technical concerns.

Keep this package focused on infrastructure support such as:

- configuration
- logging
- auth helpers
- message envelope definitions
- outbox helpers
- observability bootstrap

Do not move business rules for specific services into `common`.
