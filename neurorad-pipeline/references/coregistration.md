# Coregistration (CT ↔ MRI)

Step 5 of the pipeline. Registers the post-implant CT to the pre-implant T1 MRI so that electrode contacts marked in CT space (by VoxTool) can be mapped into MRI and atlas space.

## Prerequisites

Usually run after Steps 1–5 are complete. You *can* run it earlier (before segmentations are done) to get an early look at electrode placement in MRI space — but then you must rerun it in label-transfer mode (`NOREG`) once segmentations finish.

## Procedure

1. Log into rhino2. Define `RAMROOT` pointing to the subject's imaging directory:

   ```bash
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ```

2. Place the CT `.nii.gz` file in `$RAMROOT/$SUBJECT/` with this exact filename:

   ```
   T01_${SUBJECT}_CT.nii.gz
   ```

   If you only have `.nii`, `gzip` it first.

3. Run the coregistration. Scripts previously lived at `~sudas/DARPA/scripts`; the current path is `~/imaging-scripts/`:

   ```bash
   ~/imaging-scripts/runpipeline.sh coreg $SUBJECT
   ```

   You should see something like:

   ```
   Your job 1327465 ("coreg$SUBJECT") has been submitted
   ```

4. When the job finishes, output files appear in `$RAMROOT/$SUBJECT/`.

## Verify the result

Load the CT as the main image and the registered MRI as an overlay:

```bash
~sudas/bin/itksnap-3.2.0-20141023-Linux-x86_64/bin/itksnap \
  -g $RAMROOT/$SUBJECT/T01_${SUBJECT}_CT.nii.gz \
  -o $RAMROOT/$SUBJECT/T01_CT_to_T00_mprageANTs_inverse.nii.gz
```

If the overlay is misaligned, see `coregistration_fix.md`.

## Label-transfer-only rerun (`NOREG`)

If you ran coregistration *before* T1/T2 segmentation finished, anatomical labels won't have been transferred into CT space — which is what subsequent automated localization needs. Once segmentations complete, rerun in label-transfer mode (fast, skips the actual registration):

```bash
~RAM_maint/imaging-scripts/runpipeline.sh cores $SUBJECT NOREG
```

Note: the subcommand is `cores` (not `coreg`) and the extra argument is `NOREG`.
