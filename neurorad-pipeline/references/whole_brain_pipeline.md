# Whole-Brain Volumetric Segmentation (AHEAD)

Part of Step 3. Multi-atlas segmentation of the T1 MRI, producing per-voxel anatomical labels across the whole brain.

## Setup

1. Place the T1 MRI in `$RAMROOT/$SUBJECT/` with the exact filename:

   ```
   T00_${SUBJECT}_mprage.nii.gz
   ```

   If you only have `.nii`, `gzip` it first.

2. Launch a screen as `RAM_maint`, then:

   ```bash
   slursh 10G
   export SUBJECT=<SUBJECT_CODE>
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ```

## Run brain extraction first (strongly recommended)

Extra neck or face tissue in the T1 can make atlas registrations go sideways, producing labels outside the brain. The brain-extraction step (BrainX, `brain_extraction.md`) produces a clean brain mask that fixes this. Run BrainX first, then pass the `BRAIN` argument so the whole-brain pipeline uses the mask.

## Run the pipeline

```bash
~/imaging-scripts/wholebrainseg.sh $SUBJECT [BRAIN]
```

A series of jobs will be submitted. Monitor with `qstat`. The first stage is a set of pairwise registration jobs (one per atlas image), all running simultaneously:

```
1331129 0.50029 register_1 sudas  r  05/02/2015 09:32:57 RAM.q@node43   1
1331130 0.50029 register_1 sudas  r  05/02/2015 09:32:57 RAM.q@node43   1
...
```

While these run, you'll see periodic logging like:

```
Job 1331161 is in state r
Job 1331162 is in state r
Job 1331163 is in state r
(Sat May 2 09:55:50 EDT 2015) Still waiting for 28 jobs
```

Once all first-stage jobs complete, the pipeline automatically launches stage two (label-fusion jobs named `lf_T00_...`):

```
1331180 0.51000 lf_T00_R10 sudas  r  05/02/2015 10:15:57 RAM.q@node36   1
```

## Check completion

When no jobs remain in `qstat`, segmentation is either done or failed at some intermediate stage. Because `qstat` job names don't show subject IDs, if you're running multiple subjects verify completion by checking for the output file:

```bash
$RAMROOT/$SUBJECT/T00_${SUBJECT}_mprage_brainBrainExtractionBrain/T00_${SUBJECT}_mprage_brainBrainExtractionBrain_wholebrainseg.nii.gz
```

## Verify in ITK-SNAP

```bash
~sudas/bin/itksnap-3.2.0-20141023-Linux-x86_64/bin/itksnap \
  -g $RAMROOT/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
  -s $RAMROOT/$SUBJECT/T00_${SUBJECT}_mprage_brainBrainExtractionBrain/T00_${SUBJECT}_mprage_brainBrainExtractionBrain_wholebrainseg.nii.gz \
  -l ~sudas/bin/localization/wholebrainlabels_itksnaplabelfile.txt
```

## Common failure: labels outside the brain

The most common issue is labels appearing outside the brain, particularly towards the bottom of the volume. This usually means neck tissue threw off atlas registration. The overall segmentation may look fine except for isolated "islands" of incorrect labels surrounded by the correct region.

Fix: run BrainX first, then rerun whole-brain segmentation with the `BRAIN` argument. The labels outside the brain will disappear and the interior labels will look cleaner.
