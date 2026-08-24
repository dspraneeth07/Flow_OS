# flowos-arxiv

arXiv search component as a standalone FlowOS Extension Bundle.

This is the second-pilot port that validates
[`src/bundles/PORTING.md`](../PORTING.md) — the documented recipe for
extracting an in-tree provider into a standalone Bundle distribution.
The bundle ships a single component, `ArXivComponent`, which queries
arXiv's public Atom API for paper metadata.

## Install

```bash
pip install flowos-arxiv
```

The bundle is registered automatically via the `flowos.extensions`
entry-point.  After install, restart your FlowOS server; the
`ArXivComponent` will appear in the palette under the `arxiv` bundle
group.

## Develop

```bash
cd src/bundles/arxiv
pip install -e .
flowos_core extension validate .
```

## Manifest

The extension manifest is shipped at
`src/flowos_arxiv/extension.json` and points at the bundle at
`components/arxiv`.  Components register under the canonical
namespaced ID `ext:arxiv:ArXivComponent@official`.

## Migration

Saved flows referencing the legacy class name `ArXivComponent` or the
old import paths `flowos_core.components.arxiv.arxiv.ArXivComponent` /
`flowos_core.components.arxiv.ArXivComponent` are rewritten to the new
namespaced ID by the migration table in
`src/flowos-core/src/flowos_core/extension/migration/migration_table.json`.
