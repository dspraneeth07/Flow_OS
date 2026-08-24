# Docling Bundle

Docling components for FlowOS packaged as a standalone Extension Bundle.

## Components

- Docling
- Docling Serve
- Export DoclingDocument
- Chunk DoclingDocument

## Install

The bundle is installed with FlowOS in the 1.10 workspace. The base package includes `docling-core` for the `DoclingDocument` schema. For standalone local conversion:

```bash
uv pip install "flowos-docling[local]"
```

Chunking and picture-description support use separate optional extras. Chunking
does not install the full local converter/OCR stack:

```bash
uv pip install "flowos-docling[chunking]"
uv pip install "flowos-docling[image-description]"
```

## Develop

```bash
uv run flowos_core extension validate src/bundles/docling/src/flowos_docling
uv run pytest src/bundles/docling/tests
```
