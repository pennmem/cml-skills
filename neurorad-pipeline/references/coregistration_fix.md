# Manual Coregistration of T1 and CT in ITK-SNAP

If the automatic coregistration (`runpipeline.sh coreg`) produces a misaligned result, use ITK-SNAP's semi-automatic registration tool to manually align the CT to the T1, then feed the resulting transform back into the pipeline.

Video walkthrough of the registration tool: <https://youtu.be/RT_M_EPzdyY>

## Load the images

1. **File → Open** the T1 MRI (`${SUBJECT}_mprage.nii.gz`) as a **Main Image**.
2. **File → Add Another Image** to load the CT (`${SUBJECT}_CT.nii.gz`).

## Register

Use **Tools → Registration**. General workflow:

1. With MRI as main and CT as overlay, if they don't look close to each other (or one isn't even in the field of view), in the **Manual** tab click **Match By → Center of Mass** to bring them near each other. If that still doesn't overlap them, use the Interactive Tool to drag things into approximate place.

2. Switch to the **Automatic** tab. Keep the transformation model at **Rigid** and similarity metric at **Mutual Information**. Click **Run Registration**. If that aligns them well, jump to "Save the transform" below.

3. If automatic registration didn't work, go back to **Manual**. Use the mouse to rotate and translate the CT (the dashed circles guide you) until it's close. Rotation and translation sliders exist too but the mouse is usually faster. Leave scaling alone — CT and MRI should be the same physical size unless a rare scanner artifact is at play.

4. Use overlay view, different colormaps, and transparency (`q` / `w` / `e`) to evaluate alignment quality.

5. Often a rough manual alignment gives the automatic registration enough of a push to work. Once you're roughly aligned, try **Run Registration** again from the **Automatic** tab.

## Picking stim sites (optional side use)

If you need to pick stim sites from this view, adjust the overlay opacity until both brain anatomy and contacts are visible. Cross-reference with the implant map to identify contacts in stimulation hot spots.

## Save the transform and feed it back into the pipeline

1. When you're satisfied with the alignment, save the transform using the disk icon. Save into the subject's `autoloc` directory.

2. Rerun the coregistration pipeline in manual-transform mode:

   ```bash
   ~/imaging-scripts/runpipeline.sh coreg R1001P USEMANUAL TRANSFORMFILE.txt
   ```

   Replace `R1001P` with the actual subject code and `TRANSFORMFILE.txt` with your saved transform filename.
