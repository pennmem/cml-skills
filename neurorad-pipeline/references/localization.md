# Automatic Localization

Step 6 of the pipeline. Maps each electrode contact to anatomical labels using the segmentations produced in Step 3 plus the CT↔MRI coregistration from Step 5.

## Prerequisites

You must have completed **at least Steps 1, 4, and 5**. Normally Steps 2–3 (segmentation) are also done. If they aren't, this step will produce labeled electrode *location* images (useful for manual localization) but no automated label assignments.

## Procedure

1. Log into rhino2. Define `RAMROOT`:

   ```bash
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ```

2. Copy the `VOX_coords_mother.txt` file created in Step 5 to `$RAMROOT/$SUBJECT/`.

3. Connect as `RAM_maint` with X forwarding, activate the right conda env, and run:

   ```bash
   ssh -X RAM_maint@rhino2.psych.upenn.edu
   source activate event_creation
   export SUBJECT=<SUBJECT_CODE>
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ~/imaging-scripts/runpipeline.sh loc $SUBJECT
   ```

   You should see:

   ```
   Your job 1327465 ("locR1001P") has been submitted
   ```

4. When the job finishes, output files appear in `$RAMROOT/$SUBJECT/`.

## Sanity-check the output

These three ITK-SNAP invocations overlay colored spheres on the CT, T1, and T2 at the contact locations — a quick visual check that VoxTool coordinates were mapped correctly.

**CT-space:**

```bash
~sudas/bin/itksnap-3.2.0-20141023-Linux-x86_64/bin/itksnap \
  -g $RAMROOT/$SUBJECT/T01_${SUBJECT}_CT.nii.gz \
  -s $RAMROOT/$SUBJECT/T01_${SUBJECT}_CTelectrodelabels_spheres.nii.gz \
  -l $RAMROOT/$SUBJECT/electrode_snaplabel.txt
```

**T1-space:**

```bash
~sudas/bin/itksnap-3.2.0-20141023-Linux-x86_64/bin/itksnap \
  -g $RAMROOT/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
  -s $RAMROOT/$SUBJECT/T00_${SUBJECT}_mprageelectrodelabels_spheres.nii.gz \
  -l $RAMROOT/$SUBJECT/electrode_snaplabel.txt
```

**T2-space** (only if T2 was collected and processed):

```bash
~sudas/bin/itksnap-3.2.0-20141023-Linux-x86_64/bin/itksnap \
  -g $RAMROOT/$SUBJECT/T00_${SUBJECT}_tse.nii.gz \
  -s $RAMROOT/$SUBJECT/T00_${SUBJECT}_tseelectrodelabels_spheres.nii.gz \
  -l $RAMROOT/$SUBJECT/electrode_snaplabel.txt
```

Repeat any of these with `spheres_mid` instead of `spheres` to visualize bipolar-pair midpoints instead of individual contacts. The label file `electrode_snaplabel.txt` names each contact inside ITK-SNAP.

## Outputs

Many files are generated. The two most important:

- **`electrodelabels.csv`** — contact name + anatomical location from the T1 whole-brain atlas, probed in CT space. If T2 MTL labels are available, they're appended after a `/`.
- **`electrodenames_native.csv`** — same information but probed in native labeling space (T1 or T2). Because label interpolation into CT space can lose fidelity, this is usually the more reliable of the two.

Check both for `nan` or empty cells — these indicate contacts that didn't land in any labeled region.

## MNI coordinates

If nonlinear MNI normalization (Step 3 NORM) is complete, this script also produces MNI coordinates:

- `electrodenames_coordinates_mni.csv` — monopolar MNI coordinates.
- `electrodelabels_and_coordinates_mni_mid.csv` — bipolar (midpoint) MNI coordinates + atlas labels.
