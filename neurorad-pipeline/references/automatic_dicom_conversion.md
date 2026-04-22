# Automatic DICOM → NIfTI Conversion

Step 1 utility. Many programs convert DICOM series to NIfTI volumes; the lab's default is a shell wrapper around `convert3d` (the command-line tool distributed with ITK-SNAP).

> **Regardless of method**, always open the resulting `.nii.gz` files in an image viewer and visually confirm they look right before moving on. Automated conversion can silently produce bad output.

## Script

The conversion script traverses the entire input directory tree, finds every DICOM series, converts each one, and writes `.nii.gz` files into the output directory.

```bash
~sudas/bin/c3ddcm2nii.sh input_dir output_dir
```

**Typical inputs:**

- `input_dir` — top-level directory where imaging data was uploaded, e.g. `/data10/RAM/subjects/R1001P/imaging`.
- `output_dir` — where to place the converted `.nii.gz` files.

After conversion, rename the files to the pipeline's standard names:

- T1 MRI → `T00_${SUBJECT}_mprage.nii.gz`
- T2 MRI → `T00_${SUBJECT}_tse.nii.gz`
- CT → `T01_${SUBJECT}_CT.nii.gz`

And place them in `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/`.
