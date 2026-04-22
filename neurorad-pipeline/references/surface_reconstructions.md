# Surface Reconstruction (FreeSurfer `recon-all`)

FreeSurfer cortical parcellation on the pre-implant T1. Takes ~24 hours. This is Step 2 of the pipeline.

## Directories

Go to `/data/eeg/freesurfer`. Two folders live here:

- `mris_used/` — keeps track of which MRIs have been used.
- `subjects/` — where all FreeSurfer outputs are kept.

## Procedure

1. Create a per-subject directory under `mris_used/`:

   ```bash
   mkdir /data/eeg/freesurfer/mris_used/$SUBJECT
   ```

2. Copy the pre-implant T1 (`mprage`) into that directory:

   ```bash
   cp /data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
      /data/eeg/freesurfer/mris_used/$SUBJECT/
   ```

3. Start a named `screen` session. E.g.:

   ```bash
   screen -S R1724J_fs
   ```

4. Use `slursh` (slurm-ssh) instead of running on the head node. FreeSurfer typically requires about 3 GB of RAM, but you can request more to avoid OOM:

   ```bash
   slursh 3G    # typical
   # or
   slursh 32G   # fallback if the 3G run runs out of memory
   ```

5. Run the reconstruction:

   ```bash
   export SUBJECT=<SUBJECT_CODE>
   recon-all -i /data/eeg/freesurfer/mris_used/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
             -all -s $SUBJECT \
             -mail kahana-clinical@sas.upenn.edu & disown
   ```

   Include your email as the last argument to receive notification on completion.

## Recovery

- **Node crashes mid-run.** Re-start from where it crashed:

  ```bash
  recon-all -all -s $SUBJECT -mail kahana-clinical@sas.upenn.edu & disown
  ```

- **Run fails entirely.** Remove the subject's FreeSurfer output directory and start over:

  ```bash
  cd /data/eeg/freesurfer/subjects
  rm -r $SUBJECT
  # then rerun the full recon-all command above
  ```

## Troubleshooting

FreeSurfer's environment settings are no longer set up automatically on rhino (they were causing problems for some users). If you use FreeSurfer, add these lines to your `~/.bashrc`:

```bash
export FREESURFER_HOME=/usr/global/freesurfer
export SUBJECTS_DIR=/data10/eeg/freesurfer/subjects
source $FREESURFER_HOME/SetUpFreeSurfer.sh >/dev/null
```

`SUBJECTS_DIR` may need to be changed to your specific subjects directory path.
