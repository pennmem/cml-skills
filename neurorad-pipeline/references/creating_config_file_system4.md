# Creating a Configuration File for System 4 (Elemem)

Config files are `.zip` bundles containing `.json` parameters and `.csv` montage files used to run experiments on System 4 (Elemem). Research sites load the bundle into Elemem to run a given experiment for a given patient.

> **Audience**: research coordinators. Config files are generated automatically from templates in `/home2/RAM_maint/elemem_scripts`.

## Workflow

1. Obtain a valid **jacksheet** and **electrode implant sheet** from the clinical site. Remove all non-brain channels. Copy the jacksheet into `/data10/RAM/subjects/$SUBJECT/docs`.

2. Switch to the `RAM_maint` account:

   ```bash
   sudo -s -u RAM_maint
   ```

3. Create the **`area.txt`** file (one line per lead, space-delimited: lead name then contact surface area):

   ```bash
   cd /data10/RAM/subjects/$SUBJECT/docs
   vim area.txt
   ```

   Example:

   ```
   LA 5.024
   LB 5.024
   LC 6.184
   ```

   Current surface areas used across sites:

   - PMT depthalon: `5.024`
   - DIXI microdeep: `5.024`
   - AdTech depth: `6.184`
   - Any micros: `0.001`

4. Create the montage files. Run as `RAM_maint`:

   ```bash
   conda activate elemem_clf
   python ~/elemem_scripts/make_mon.py
   ```

5. Create **`stim.txt`** with the stimulation sites chosen by the clinical team based on the localization:

   ```bash
   cd /data10/RAM/subjects/$SUBJECT/docs
   vim stim.txt
   ```

   - Format: experiment name on the line, then space-delimited pairs. Per the wiki text, **RepFR2 and OPS are the currently supported stim experiments**; the wiki's example also includes a `CPS` line, so CPS support may exist or be planned — check with the experiment analyst if generating CPS configs.

   Example `stim.txt` (as given in the wiki):

   ```
   RepFR2 LA1_LA2 LB1_LB2 LC1_LC2
   OPS LA1_LA2 LA2_LA3 LA3_LA4
   OPS LB1_LB2 LB2_LB3
   LC1_LC2 LC2_LC3 LC3_LC4
   CPS LC1_LC2 LC2_LC3
   ```

   - For **RepFR2**: all requested sites on one line → one config per site.
   - For **OPS** and **CPS**: each line creates one config containing those pairs.
   - Skip lines by prefixing with `#` (useful for avoiding long CPS classifier-fitting runs when you don't need them).

6. Generate all configs (still as `RAM_maint`, with `elemem_clf` active):

   ```bash
   python ~/elemem_scripts/generate_configs.py
   ```

   Follow the interactive prompts. This produces stim and non-stim configs in `/data10/RAM/subjects/$SUBJECT/docs` as a zip file. Both `stim.txt` and `area.txt` must exist in that directory for stim-config generation to succeed.

7. **Manually verify every config before sending it out.** In particular, for stim experiments confirm:
   - The correct contact pairs are being stimulated.
   - Experiment-specific stim parameters match the template configs in `~/elemem_scripts` (unless the experiment analyst has specified otherwise).

   If you spot issues, alert the experiment analyst or the System Development team.

## Updating or adding configs

Do **not** edit the scripts directly from the `RAM_maint` account. The canonical source is the `elemem_scripts` repo:

```bash
git clone https://github.com/pennmem/elemem_scripts.git
```

Workflow:

1. Upload a template (`template_<EXP_NAME>_config.json`) into `/home2/RAM_maint/elemem_scripts`.
2. Update `parameters.py` with the experiment's stim parameters and extend `get_stim_params()` accordingly.
3. Update `generate_configs.py` if needed — see `set_stim_config()`.

If you're new to git, consult the System Development team before opening a PR.
