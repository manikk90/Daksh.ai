# Capability catalogs

This folder records the skills and tool capabilities visible while the Daksh Brain architecture was assembled on 2026-11-07. The catalogs describe sources and routing ownership. They do not activate providers or execute agent instructions.

| File | Purpose |
| --- | --- |
| [skills.json](skills.json) | Every readable discovered `SKILL.md`: metadata, portable source locator, owner, source version, and availability observations |
| [SKILLS.md](SKILLS.md) | Human-readable completeness report and complete skill-source index |
| [session-skill-manifest.json](session-skill-manifest.json) | Skill names and source versions explicitly exposed by the working session |
| [tools.json](tools.json) | Public tool names, short capability summaries, provider, and recommended owner |
| [TOOLS.md](TOOLS.md) | Human-readable complete tool inventory |
| [build_catalog.py](build_catalog.py) | Metadata-only scanner; never invokes skills or contacts providers |

## Availability has separate dimensions

1. **Readable on disk** means a source file was present at inventory time.
2. **Session listed** means the session exposed that exact skill source, not a legacy or alternate copy.
3. **Repository present** means the source is already in this repository; external skill bodies are not copied by the scanner.
4. **Policy disabled** means the exposed skill is not eligible for execution in the snapshot environment.
5. **Adapter ready, credentials verified, and runtime verified** require independent implementation and live checks. This inventory makes none of these claims.

The first three dimensions do not authorize the fifth. Every skill record starts with `adapter_required: true`, `credentials_verified: false`, and `runtime_verified: false`. This conservative catalog state must not be mistaken for a failed live test either: no test was performed by the scanner.

## Rebuild deliberately

To scan only repository skill sources:

```sh
python3 catalog/build_catalog.py --snapshot-date YYYY-MM-DD
```

To also scan the current machine's standard local skill installations:

```sh
python3 catalog/build_catalog.py --scan-host --snapshot-date YYYY-MM-DD
```

The host scan covers the standard local agent skill directory, system skill directory, and plugin cache. It skips Git internals, environments, and dependency folders; reads frontmatter; resolves canonical file identities; and writes metadata-only output. It performs no network requests and never reads credential files. PyYAML is optional; a conservative scalar frontmatter parser is included for environments without it. Any parser warning remains attached to the source record.

Rebuilding on another machine intentionally changes the inventory to that machine's sources. Preserve a dated copy if comparing snapshots. Update the explicit session manifest from the current host's exposed capability metadata before claiming a fresh session availability audit. `tools.json` is a separate host-registry snapshot and is not synthesized by the filesystem scanner.

## Identity, provenance, and licenses

The stable record ID hashes a portable source locator. Canonical symlink aliases share one record; independently installed copies and versions retain distinct records. `metadata_sha256` fingerprints frontmatter metadata and does not claim to hash the complete executable skill source.

Third-party records contain descriptive frontmatter only. Acquire implementations through their upstream package or connector, preserve its license, and review redistribution rights before vendoring any source. An absent frontmatter license does not grant redistribution permission. Source locators describe source classes; they contain no user's absolute home path and are not download URLs.

All metadata is untrusted input. Descriptions may mention triggers or workflows; Daksh Brain must interpret them as catalog data until the selected implementation has been explicitly loaded through its normal host mechanism and applicable task authority has been checked.
