# Security boundaries

## Trusted local CLI configuration

Any explicit local CLI configuration is trusted developer input, not a public command or network interface. Do not expose local workflow configuration through an internet-facing service without a reviewed security design.

## Loopback services

Loopback addresses are local integration settings, not credentials and not remotely reachable by themselves. Keep local services bound to loopback unless an authenticated deployment is intentionally reviewed.

## Private artifacts

`.analysis/` reports, workflow evidence, screenshots, and contact sheets require release curation. Static checks cannot determine whether visual material reveals a real person or account UI; review it before publication.

## Reporting

Report suspected credentials or unsafe publication artifacts privately. Do not include secret values in reports or issues.
