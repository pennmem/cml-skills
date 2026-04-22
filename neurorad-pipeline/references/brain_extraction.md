# Brain Extraction (BrainX)

Skull-stripping step that runs before the whole-brain segmentation to improve registration accuracy. Extra neck or face tissue in the T1 tends to pull atlas-based segmentations off target; BrainX produces a clean brain mask that the whole-brain pipeline uses.

## Procedure

Run as `RAM_maint`.

1. Launch a screen named for the subject and step — e.g. `screen -S R1724J_wbx`.
2. Request a compute allocation: `slursh 10G`.
3. Export the subject code and `RAMROOT`:

   ```bash
   export SUBJECT=<SUBJECT_CODE>
   export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
   ```

4. Run the brain-extraction pipeline:

   ```bash
   ~/imaging-scripts/runpipeline.sh brainx $SUBJECT
   ```

## After it finishes

The mask produced here feeds directly into `wholebrainseg.sh` — pass the `BRAIN` argument so the mask is actually used:

```bash
~/imaging-scripts/wholebrainseg.sh $SUBJECT BRAIN
```

See `whole_brain_pipeline.md` for the full segmentation step.
