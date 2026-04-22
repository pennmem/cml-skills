# VoxTool — Electrode Annotation

Step 4 of the pipeline. VoxTool is a semi-automated GUI for extracting electrode contact coordinates from a post-implant CT. It thresholds the CT to produce a cloud of high-density voxels (metallic contacts + some artifacts like staples, wires, or dental hardware), then lets you label each contact.

## Installing VoxTool

Requires `conda` or `miniconda`.

```bash
git clone https://github.com/pennmem/voxTool.git
conda env create -f conda_env.yml
conda activate vt
cd voxTool
python launch_pyloc.py
```

> **Platform note**: VoxTool runs well on some newer Macs and not others. Windows support has also been inconsistent. At some point the lab needs to update VoxTool to Python 3 and reformulate its packages.

## Loading the CT

After launching VoxTool:

1. Click **Load Scan** (bottom left) and open the post-implant CT. If you resampled the CT earlier, use the resampled one. The CT should be in NIfTI format, in the imaging directory — typically `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/T01_${SUBJECT}_CT.nii.gz`. *(The VoxTool wiki example literally shows `T00_R1350D_CT.nii.gz`; this looks like a typo — the pipeline's canonical CT filename is `T01_*_CT.nii.gz` per the Step 1 QC in `pipeline_overview.md`. If a file with either prefix exists, use whatever the Step 1 conversion actually produced.)*
2. At the top of the window, the **CT Threshold** bar defaults to `99.96`. This percentile determines which voxels appear in the point cloud.
   - Lowering the threshold shows more voxels (visible contacts increase, but so does noise and tissue).
   - Raising it shows fewer voxels (cleaner, but you may lose contacts).
   - CT quality drives how much adjustment is needed. Lower-quality CTs usually want a lower threshold.
   - Adjust in small steps (≤ 0.2) per update. Larger jumps tend to crash VoxTool.

**Critical warning**: changing the threshold after labeling some electrodes will lose those labels. If you have to re-threshold mid-session, save out interim results first, then merge the output files after.

## Labeling electrodes

General workflow:

1. **Load the CT**, adjusting the threshold as needed. To adjust: change the number in the CT Threshold bar, then press **Update**.
   - To continue a previous session, use **Load Coordinates** and select the existing JSON coordinate file.

2. **Press Define Leads.** In the pop-up, enter each implanted lead's name, dimensions, type, and (if applicable) microcontact brand. Click **Submit** after each lead, then **Confirm** to apply them to the main screen.
   - **Names must match the jacksheet exactly.**
   - Dimensions are rows (x) × columns (y). For depths and strips, use (number of contacts × 1).
   - Type is Strip, Grid, or Depth.
   - For macro/micro leads, select the micro brand.
   - **Request the sheet that specifies the number of contacts per shank**, not the one that maps channel numbers to recorded contacts — some contacts may be skipped in the montage if there are too many.
   - **All contacts visible in the CT must be labeled**, even if they aren't listed in the jacksheet. The reverse is fine: contacts in the jacksheet that don't appear in the CT mean nothing extra. What breaks things is the other direction — the pipeline errors if a contact listed in the jacksheet is *missing* from the VoxTool output.

3. **Pick a lead** from the **Label** dropdown (upper left).

4. **Click a contact** in the CT. Enter its contact number to the right, then press **Submit**. Contacts are numbered incrementally from the deepest contact (tip of the electrode) outward to the base (surface of the scalp).

   Two semi-automatic options:

   - **Interpolate**: mark the two ends of a depth/strip (or four corners of a grid), then press **Interpolate** to fill in the middle. Press **Interpolate** again for additional contacts if needed.
   - **Seeding**: press **Seeding** to toggle on. VoxTool will extrapolate the next contact as you click, auto-incrementing the number. Double-check the result — occasionally two contacts receive the same location.

5. **Press Add Micro-Contacts** for macro/micro leads. (UTSW's micros are Behnke-Fried.)

6. **Save** using **Save as**. With **Include Bipolar Pairs** checked, midpoints of neighboring contacts are saved as well.

   Save to both locations:

   - `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/`
   - `/data10/RAM/subjects/$SUBJECT/tal/`

   Also upload to the ASANA localization task.

## Outputs

- `voxel_coordinates.json` — structured contact coordinates.
- `VOX_coords_mother.txt` — flat text form used by the downstream localization step.
