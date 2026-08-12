# Security policy

## Supported version

Security fixes are applied to the latest tagged release.

## Reporting

Please use GitHub's private vulnerability reporting for installer path handling,
checksum verification, archive integrity, or command-execution issues. Do not
open a public issue containing an exploit or private machine information.

The installers are intentionally backup-first and refuse linked pet targets,
linked `pets` parents, and Windows reparse-point equivalents. Published files
are covered by SHA-256 checksums. Users should review remote scripts before
piping them into a shell.
