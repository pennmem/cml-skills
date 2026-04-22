# Nonlinear Normalization to MNI Template ("NORM")

Step 3 of the pipeline. Produces the nonlinear mapping from the subject's T1 MRI to the MNI template, which later allows electrode contact coordinates to be reported in MNI space.

## Prerequisites

The T1-weighted MRI must be available at the appropriate location under `$RAMROOT/autoloc/`. This is either already in place (because you've run or queued the whole-brain segmentation, see `whole_brain_pipeline.md`) or will be shortly.

This step can run independently of the whole-brain and MTL segmentation jobs.

## Procedure

1. Launch a screen as `RAM_maint`, named for the subject:

   ```bash
   screen -S norm1337E
   ```

2. Request memory:

   ```bash
   slursh 10G
   ```

3. Export subject code and `RAMROOT`:

   ```bash
   export SUBJECT=<SUBJECT_CODE>
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ```

4. Run the normalization:

   ```bash
   ~/imaging-scripts/runpipeline.sh norm $SUBJECT
   ```

   You should see:

   ```
   Your job 1327465 ("normR1337E") has been submitted
   ```

## Timing

This job takes **24–36 hours**, noticeably longer than the segmentation jobs. Check status with `qstat` — `norm$SUBJECT` will appear in the output until it's done.

## Verify

Outputs land in `$RAMROOT/$SUBJECT/T00/thickness/`. Open ITK-SNAP and load:

- **Main image**: `/home2/RAM_maint/neurorad_templates/localization/NickOasisTemplate/T_template0.nii.gz`
- **Overlay**: `$RAMROOT/$SUBJECT/T00/thickness/${SUBJECT}CorticalThicknessNormalizedToTemplate.nii.gz` — use a colormap like `Hot`.

A good normalization produces a thickness map that follows the cortical ribbon of the template brain, brighter where cortex is thicker. A bad one will show obvious misalignment. This step rarely fails.

The registered MRI itself isn't saved (to minimize disk usage). The thickness overlay is a good proxy for alignment quality.

## Downstream

- If `norm` finishes **before** automatic localization (Step 6) runs, the localization step will produce MNI coordinates for every contact as part of its normal output. This is the common case — pre-op imaging is usually available hours before post-op.
- If `norm` finishes **after** localization ran, you'll need to rerun the localization step to pick up MNI coordinates.

> **Note**: Interfacing MNI coordinates from this pipeline with the older Talairaching routines is not implemented yet.
