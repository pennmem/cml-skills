# Neurorad Pipeline v2 — Overview

> This pipeline uses the bash variable `$SUBJECT` in place of a subject code such as `R1001P`. For commands using this variable to execute properly, it needs to be defined by the user, for example: `export SUBJECT="R1001P"`.

The original wiki linked a `Lazy_Pipeline_Jawn.docx` document containing commands for running all steps of the pipeline. *(External media — not included in this skill.)*

## Comparing v1 and v2 outputs

The [release notes](https://github.com/pennmem/neurorad_pipeline/blob/master/RELEASE_NOTES.md) contain information on what has changed in terms of final output formats and stored information. These notes are particularly important for anyone conducting analyses that use localization information (coordinates and atlases in particular) for subjects across different versions of the pipeline.

## Install required software

**Shell scripts**
- [Imaging Scripts](https://github.com/pennmem/imaging-scripts)

**Python components**
- [Event Creation data submission utility](https://github.com/pennmem/event_creation)
- [Neurorad pipeline submodule](https://github.com/pennmem/neurorad_pipeline)
- [voxTool electrode annotation tool](https://github.com/pennmem/voxTool)

**Software for viewing results**
- [ITK-SNAP viewer for cross-sectional images and volume segmentation](http://www.itksnap.org/pmwiki/pmwiki.php)
- [Web-based localization viewer](https://github.com/pennmem/brain_viz)

## Step 0 — Create the jacksheet.txt

1. Create a subject directory under `/data10/RAM/subjects/`. You can use the alias `newsub` to create the subject directory tree:
   - Set the subject variable to the desired subject code: `export SUBJECT=<SUBJECT_CODE>`
   - Type `newsub` to create the subject directory.
2. Create the jacksheet in `/data10/RAM/subjects/$SUBJECT/docs`. The `jacksheet.txt` file is a plaintext file where each line is a recording channel (in increasing order) and an electrode label name, reflecting the actual data mapping. See the "Creating a Jacksheet" wiki page for details *(not included in this skill snapshot)*.
   - You can access this directory using the alias `doc` once the `SUBJECT` variable is set.

Other useful aliases:

- `im` — go to the imaging directory where processed imaging is saved: `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT`.
- `beh` — go to `/data10/RAM/subjects/$SUBJECT/behavioral/`. All behavioral data (and associated EEG) for the subject is uploaded here.
- `doc` — go to `/data10/RAM/subjects/$SUBJECT/docs/`. In addition to the jacksheet, this is where you create configuration files for experiments (if using System 4).
  - Config generation: see `creating_config_file_system4.md`. Config files are `.zip` files containing `.json` info files and `.csv` montage files for running experiments on System 4 (Elemem).

## Step 1 — Convert and organize the pre-implant MRI volumes and post-implant CT

This step prepares imaging to be processed in later steps of the pipeline.

1. These steps should be done as `RAM_maint`.
2. Make sure the subject directory tree `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/` exists. This is where all to-be-processed imaging (T1 and T2 MRIs, and post-implant CT) should be uploaded and where processed imaging (the output of different pipeline steps) will be saved. See Step 0 for how to create the subject directory.
3. If it doesn't exist, make a soft link to `/data/eeg/` for the subject:

   ```bash
   ln -s /data10/RAM/subjects/$SUBJECT/ /data/eeg/$SUBJECT
   ```

4. Also make a soft link called `autoloc` to the leaf-level `$SUBJECT` directory:

   ```bash
   ln -s /data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/ /data10/RAM/subjects/$SUBJECT/imaging/autoloc
   ```

5. Obtain pre-implant 3D T1-weighted and high-res hippocampal coronal T2-weighted scans in `.dcm` format. Instructions to obtain imaging for Jefferson subjects: see `jefferson_imaging_workflow.md`. Imaging for other sites lives in the `incoming` or `imaging` directory already.

6. Convert DICOM to NIfTI. Two ways:
   - In ITK-SNAP: **File → Open main image**, select any of the `.dcm` files in the MRI directory. Always look at the images and run the QC steps below.
   - Script-based: see `automatic_dicom_conversion.md`. A new script using `c3d` (distributed with ITK-SNAP) takes advantage of the robust NIfTI conversion tech used by ITK-SNAP.

### T1 MRI QC

Load the T1-MRI into ITK-SNAP as a Main Image.

1. Save it out with a `.nii.gz` extension. The T1-MRI should be named `T00_${SUBJECT}_mprage.nii.gz`. *(Note: normalization can fail if there is a voxel with negative intensity; use the c3d script approach in this case.)*
2. Confirm it's a pre-implant MRI (no "black holes" or similar artifacts that look like an electrode contact).
3. Confirm it's a non-contrast MRI (post-contrast MRIs have very bright spots all over). Contrast agents alter gray/white/CSF intensity differences and can cause failed brain segmentation or reconstruction. *(Wiki had example contrast vs non-contrast images — not included.)*
4. Identify any previous surgical or other lesion (e.g., prior temporal lobectomy). Note it if present.
5. Note signal quality (graininess, poor white/gray contrast, etc.).
6. Confirm orientation. Use ITK-SNAP's 3-planar anatomical direction markers (A/P, etc.). If markings don't match the image, use **Tools → Reorient image**.
7. Note whether a lot of neck tissue is included — helpful for later troubleshooting.
8. Check **spatial resolution** via **Tools → Image Information → Voxel spacing**. All 3 numbers should be close to 1. If they're substantially higher (≥ 1.5), tell the site this may be the wrong scan. If substantially lower (≤ 0.5), resample to ~1 mm isotropic to avoid memory problems.

### Resampling

Place original images in **both** the imaging directory (`/data10/RAM/subjects/$SUBJECT/imaging`) and the subject directory within imaging (`/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT`). **Resampling should only be done inside the subject directory, leaving originals in the outer imaging dir as backup.**

Run as `RAM_maint`. The resample factor is "current voxel spacing / desired voxel spacing" — e.g., 0.5 mm → 1 mm is `50%`.

```bash
# T1
~/bin/c3d/bin/c3d T00_${SUBJECT}_mprage.nii.gz -o T00_${SUBJECT}_mprage_original.nii.gz -resample 50x50x100% -o T00_${SUBJECT}_mprage.nii.gz
# T2
~/bin/c3d/bin/c3d T00_${SUBJECT}_tse.nii.gz -o T00_${SUBJECT}_tse_original.nii.gz -resample 50x50x100% -o T00_${SUBJECT}_tse.nii.gz
# CT
~/bin/c3d/bin/c3d T01_${SUBJECT}_CT.nii.gz -o T01_${SUBJECT}_CT_original.nii.gz -resample 50x50x100% -o T01_${SUBJECT}_CT.nii.gz
```

### T2 MRI QC

If a hippocampal T2-MRI is available, save it as `T00_${SUBJECT}_tse.nii.gz` and repeat the T1 steps. Additional T2-specific checks:

1. Signal quality, same as T1. Also note contrast of the dark band of tissue within the hippocampus — essential for segmentation. T2-MRIs are particularly susceptible to subject motion (smears, long streaks). *(Wiki had example images — not included.)*
2. Confirm it's a **coronally acquired** scan with high in-plane resolution. Two signs: (a) the number of coronal slices (bottom right outside the coronal view) is much less than the other two directions, and (b) the image looks much sharper in the coronal plane. If not coronal, it isn't suitable for MTL labeling — inform the site.
3. Voxel spacing: the coronal direction (usually z) should be **≤ 3 mm** (otherwise unusable). The other two directions should be **≤ 0.5 mm** (otherwise unusable).
4. Check that the entire hippocampus is imaged. On a sagittal slice containing the hippocampus, confirm the tail of the structure is inside the field of view.
5. Check that coronal slices are perpendicular to the long axis of the hippocampus. In sagittal view, the hippocampus should appear horizontal. If not, note it — the scan is still usable, but inform the site.

### CT QC

Obtain post-implant CT in `.dcm` format and convert to `.nii.gz` following steps 1–5 of MRI conversion. The CT should be named `T01_${SUBJECT}_CT.nii.gz`. *(The wiki literal example spells this `T01_R1001P_CT.nii.gz`; both forms appear in the pipeline.)*

1. Load the CT into ITK-SNAP as a Main Image.
2. Confirm it's a post-implant CT (bright dots that look like electrode contacts).
3. Correctly reconstructed CT has 1 mm thick axial slices with 0.5×0.5 mm in-plane resolution. Quick check: ~512 slices in coronal and sagittal directions, ~200 axial slices. If not, inform the site and ask for a correct reconstruction.
4. Note neck tissue or head tilt — helpful for later troubleshooting.

All images should be placed into the imaging directory on rhino **as well as** inside the `$SUBJECT` directory in imaging. Any resampling should be done from the rhino directory, not on the desktop.

### Voxel-spacing limits (mm)

| Scan | X (axial) | Y (sagittal) | Z (coronal) |
|---|---|---|---|
| T1 MRI | 1 | 1 | 1 |
| T2 MRI | 0.5 | 0.5 | 3 |
| CT | 0.5 | 0.5 | 1 |

## Step 2 — Run FreeSurfer cortical parcellation

[FreeSurfer](https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferWiki) segments the MRI into various brain regions.

Recommended to run as `RAM_maint`: `sudo -s -u RAM_maint`.

1. Make a folder with the subject ID in `/data/eeg/freesurfer/mris_used`:

   ```bash
   mkdir /data/eeg/freesurfer/mris_used/$SUBJECT
   ```

   Copy the 3D T1-weighted scan there. If you downsampled the T1, copy the downsampled version — that's what the pipeline segments:

   ```bash
   cp /data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
      /data/eeg/freesurfer/mris_used/$SUBJECT/
   ```

2. Recommended to run FreeSurfer as a detached `screen` session. `man screen` for more info.
   - Start a screen: `screen` (add `-S <name>` to name it).
   - `slursh 3G`
   - `export SUBJECT=<SUBJECT_CODE>`
   - Run the `recon-all` command (below). Use `kahana-clinical@sas.upenn.edu` (preferred) or a non-upenn personal email for `-mail`.
   - Detach with `Ctrl-A`, `Ctrl-D`.
   - List screens: `screen -ls`. Reattach: `screen -r <screen-id>`. `exit` terminates (may need to exit twice).

3. Run FreeSurfer cortical parcellation on the 3D T1-weighted scan. See `surface_reconstructions.md` for a fuller description.

   Example:

   ```bash
   recon-all -i /data/eeg/freesurfer/mris_used/$SUBJECT/T00_${SUBJECT}_mprage.nii.gz \
             -all -s $SUBJECT \
             -mail kahana-clinical@sas.upenn.edu & disown
   ```

### Common reasons FreeSurfer may fail

1. You didn't copy the (sampled) T1 MRI to the subject's folder in `/data/eeg/freesurfer/mris_used`.
2. Bad imaging:
   - T1-weighted MRI is cropped or cut off at one or more edges.
   - Contrast T1 MRI was used. Contrast agents (e.g., gadolinium) alter tissue intensities, making it harder for FreeSurfer to distinguish gray matter, white matter, and CSF.
   - Low MRI quality (poor resolution or noise). Check voxel spacing and slice count in all three dimensions — see the voxel-spacing table in Step 1.

## Step 3 — Run multi-atlas volume segmentation and MNI registration

Recommended to run as `RAM_maint`: `sudo -s -u RAM_maint`.

### `RAMROOT`

Log into rhino2. Define an environment variable `RAMROOT` pointing to the top-level directory for image analysis:

```bash
export RAMROOT=Full_path_of_top_level_directory
```

Normally:

```bash
export RAMROOT=/data10/RAM/subjects/$SUBJECT/imaging
```

**IMPORTANT**: If running the pipeline for different patients, export a different `RAMROOT` in each terminal window.

All three pipelines (T1 whole brain, T2 ASHS, T1 normalization) can be run simultaneously, typically in different terminal windows to avoid conflicting on-screen debug messages — remember to export `RAMROOT` for each window. Recommended to run each step in its own screen:

```bash
screen -S R1724J_norm
screen -S R1724J_mtl_seg
screen -S R1724J_wbx
```

### Three parallel jobs

1. **NORM** — Non-linear normalization to MNI atlas using the 3D T1. Produces MNI coordinates later. See `nonlinear_normalization.md`.
2. **MTL_SEG** — Multi-atlas volume segmentation of medial temporal lobe using coronal T2. Produces precise MTL sub-structure labeling. *(Wiki links to an `MTL_pipeline` page not included in this skill snapshot — check the upstream wiki or the `neurorad_pipeline` repo.)*
3. **WHOLE BRAIN (with BRAINX)** — Strongly recommended to run brain extraction first, then `wholebrainseg.sh` from the command line. BrainX is not required for NORM or MTL_SEG.
   - Brain extraction: `brain_extraction.md`.
   - Multi-atlas whole-brain segmentation from the T1: `whole_brain_pipeline.md`.

## Step 4 — Annotate electrode locations in CT scan with VoxTool

VoxTool lets us individually mark and label electrodes.

Previously recommended to run as `RAM_maint` (`sudo -s -u RAM_maint`), but for the past couple of years the lab has been running VoxTool **locally**. Follow the steps in the VoxTool link below to download and launch it on your computer.

Record electrode contact names and coordinates in CT space from the post-implant CT using VoxTool in Python. Output files are `voxel_coordinates.json` and `VOX_coords_mother.txt`. Place both in the subject's `autoloc` directory **and** copy to `/data10/RAM/subjects/<SUBJECT_CODE>/tal/` (needed for event_creation submission).

See `voxtool.md` for notes and tips.

## Step 5 — Convert and register the post-implant CT

Aligns the MRI and CT on the same plane.

Recommended to run as `RAM_maint`: `sudo -s -u RAM_maint`.

1. Before running this step, complete all T1 and CT steps above (including VoxTool and T1 segmentation). T2 steps should also be completed if the T2 is usable for automated MTL segmentation. A T2 isn't technically required, but if T2 localization isn't finished first, it won't be properly coregistered.

   **Note**: if a T2 MRI is available but MTL segmentation can't be completed for any unresolvable reason (e.g., T1 and T2 MRIs are only available at different scales), delete the `sfseg` folder (in `/data10/RAM/subjects/<subj_code>/imaging/<subj_code>/T00`, created as the output of MTL segmentation) before proceeding with coregistration.

2. Co-register post-implant CT and pre-implant MRI. See `coregistration.md`.

## Step 6 — Run automatic localization

Aligns electrode locations to all of the imaging.

Run as `RAM_maint`:

```bash
ssh -X RAM_maint@rhino2.psych.upenn.edu
```

1. Generate segmentation/overlay files of contacts and midpoints using `VOX_coords_mother.txt`, and automatically generate anatomic locations of contacts and midpoints for MTL and whole-brain segmentations.
2. Outputs include `.csv` files with coordinates, and electrode sphere files that can be overlaid onto various scans to view contact or bipolar-pair midpoint locations in ITK-SNAP.
3. See `localization.md`.

## Step 7 — Run Neurorad Pipeline `event_creation` submodule

Corrects position of surface electrodes and generates all electrode coordinates and atlas locations. Submits all pipeline steps to be used on rhino.

Run as `RAM_maint`:

```bash
ssh -X RAM_maint@rhino2.psych.upenn.edu
```

1. Requires `event_creation`. Must run as `RAM_maint`. See installation and usage in the [release notes](https://github.com/pennmem/neurorad_pipeline/blob/master/RELEASE_NOTES.md).
2. Run `./submit --localization-only` and follow the prompts to enter the subject ID and localization number (initial is 0):

   ```bash
   slursh
   cd event_creation
   source activate event_creation
   sudo -u RAM_maint
   ./submit --localization-only
   ```

3. Run `./submit --montage-only` and follow the prompts to enter the subject ID and montage number (initial is `0.0`):
   - Use **monopolar** if collecting data using System 1 (syncbox) or System 4.
   - Use **bipolar** for System 3.
4. **Multiple montages**: the subject code for a new montage has `_#` appended — don't leave this out. Event creation recognizes it's the same subject and prompts for the montage number (e.g., `0.0` for original, `0.1` for new montage, `1.1` for new localization / re-implant).

## Bypassing the localization pipeline

By default, events cannot be submitted unless the localization pipeline has completed (generating `contacts.json` and `pairs.json` in `/protocols`). In some cases — imaging quality issues, or when classifiers need to be built before the long-running localization pipeline finishes — `event_creation` requires bypassing localization by creating `contacts.json` and `pairs.json` that contain all channels with null values for coordinates and regions. Riley DeHaan wrote a script for this:

```bash
ssh RAM_maint@localhost
conda activate workshop
python ~/elemem_scripts/generate_fake_pairs_contacts.py
```

Update the subject tracker, noting that localization was bypassed and either couldn't be completed or will need to be updated later once better imaging is received.

## Visualize and check results

1. Visualize segmentation and localization in [ITK-SNAP](http://www.itksnap.org). Pre-made scripts for visualizing relevant images with overlays: see `visloc.md`. A web-based visualization is also available with a simpler interface for both surface and depth electrode info. *(Wiki linked "Electrode Visualizations using Blender and Blend4Web" — not included in this skill snapshot.)*
2. Generate web-based localization viewer.
3. Inspect data and confirm anatomic locations in the depth localization spreadsheet.

## In case of re-implant / new montage

When a subject is re-implanted, the pipeline needs to be rerun with a new subject code that appends the montage number (e.g., `R1###X_1`). The session number resets to zero — the next session will be the first for this new code.

One time-saver: copy over the directories containing segmentations and normalization (these should be `imaging/T00/` and `imaging/T00_${SUBJECT}_mprage_brainBrainExtractionBrain/`), then use the `rename` function to replace the subject ID. The `find` function makes it recursive:

```bash
find autoloc/ -type f -exec rename $SUBJECT $SUBJECT\_1 {} \;
```

Set `SUBJECT` to the **old** subject code before running (e.g., `export SUBJECT=R1690E`).

Also copy over the FreeSurfer cortical parcellation:

```bash
cd /data/eeg/freesurfer/subjects/
cp -r $SUBJECT $SUBJECT\_1
```

## When things go wrong

This section covers common failures in the depth electrode localization pipeline. Usually failures show up as poor segmentation (ASHS MTL or whole-brain) or co-registration failure between T1-MRI and CT.

### 1. Inaccurate segmentation edges / under- or over-segmentation

If the segmentation is in the right anatomical location but edges are inaccurate or certain subregions are under/over-segmented, problems are likely image-quality related. Little to be done unless alternate images are available or you're willing to do manual correction in ITK-SNAP.

### 2. Segmentation completely off (MTL labels outside temporal lobe; labels outside the cranium; etc.)

Likely a registration failure. A majority of the time, the cause is "non-brain junk" in the T1-MRI — particularly neck tissue and face. Often fixable by cropping at the inferior boundary to eliminate neck tissue.

Load the image in ITK-SNAP and identify the axial slice number beyond which you want to discard. Example: image of size 176×190×256 voxels with axial on z (256 slices); to crop all slices beyond z = 224:

```bash
c3d input.nii.gz -region 0x0x0vox 176x190x224vox -o output.nii.gz
```

Delete segmentation directories before rerunning so that incorrect results are actually overwritten. This is good practice to follow up front when converting DICOM to NIfTI.

### 3. T1↔T2 registration failure (ASHS)

See `T1T2Fix.md`.

### 4. Whole-brain segmentation never finishes or is very slow

Likely insufficient memory due to very high-resolution T1 MRI (often 0.5×0.5 mm in-plane from Jefferson). Resample to ~1 mm isotropic:

```bash
c3d input.nii.gz -resample 50x50x100% -o output.nii.gz
```

### 5. CT ↔ T1 coregistration failure

Usually fixable via semi-automatic adjustments in ITK-SNAP. See `coregistration_fix.md`.

### 6. MNI normalization failure

Rare. Usually trimming neck tissue (see item 2) fixes it. Sometimes the MRI has an orientation code that doesn't play nicely with the template. If neck trimming doesn't work, reorient the image to match the template:

```bash
c3d input.nii.gz -swapdim RSP -o output.nii.gz
```

Rerun all other steps (segmentation, coregistration, autoloc) with the new MRI.

Failure can also be caused by negative intensities in the T1 — use the c3d script for the initial saving step instead of saving manually (see Step 1).

### 7. General tip: field-of-view mismatch

T1↔T2, T1↔CT, or T1↔template registrations can fail if one image is completely out of the field of view of the other. Check in ITK-SNAP tile view. One fix is to bring the two images roughly into the same physical bounding box:

```bash
c3d image1.nii.gz image2.nii.gz -mbb -o image2_matched_image1_bounding_box.nii.gz
```

### 8. Voxels labeled outside the brain even after BrainX

If you've manually removed neck tissue in the T1 and run brain extraction, but T1 segmentation still produces voxels outside the brain, you can manually remove them with the brush in ITK-SNAP.
