# Workflows

This folder contains all n8n workflow JSON files used in this thesis, organized into two subfolders:

- **`ddc-base/`** — All 9 original workflows from the DDC CAD-to-data toolkit, kept unchanged as reference
- **`thesis/`** — Workflows adapted or newly created for this thesis

---

## How Workflows Are Related

The thesis pipeline is built on top of the DDC toolkit. The diagram below shows which DDC workflows feed into which thesis workflows:

```
DDC Base                        Thesis Workflows
────────────────────────        ──────────────────────────────────
n8n_1 (basic conversion)   →   n8n_ifc_validation_adapted
n8n_4 (validation)         →   n8n_ifc_validation_adapted
n8n_3 (batch conversion)   →   n8n_fault_injection_batch
n8n_8 (ETL extract)        →   n8n_qto_extraction
n8n_9 (QTO report)         →   n8n_qto_extraction
                                n8n_bqi_scoring        (original)
                                n8n_risk_register       (original)
```

---

## Importing a Workflow into n8n

1. Open n8n in your browser
2. Go to **Workflows → Import from File**
3. Select the `.json` file from this folder
4. Update the **Setup / Set Variables** node with the correct file paths for your server
5. Click **Execute Workflow**

> **Important:** All DDC workflows have hardcoded paths (e.g. `C:\Users\Artem Boiko\...`). Always update these paths before running.

---

## Subfolder Guide

| Subfolder | Contents | Purpose |
|-----------|----------|---------|
| `ddc-base/` | All 9 original DDC workflow JSONs | Reference — do not modify these files |
| `thesis/` | Adapted and custom workflow JSONs | Working workflows for this thesis |
