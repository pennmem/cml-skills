# `visloc` — Visualize Depth Electrode Localizations

Once logged into rhino/rhino2, `visloc` is a convenience wrapper that launches ITK-SNAP with the appropriate images loaded for a subject.

## Usage

```bash
~sudas/bin/visloc <modality> <SUBJECT>
```

Where `<modality>` is one of:

- `ct` — open in CT space
- `t1` — open in T1 MRI space
- `t2` — open in T2 MRI space

**Example:**

```bash
~sudas/bin/visloc t1 R1001P
```
