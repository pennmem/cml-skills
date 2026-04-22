---
name: neurorad-pipeline
description: Navigate, interpret, walk through, and debug the Computational Memory Lab's Neurorad Pipeline for iEEG electrode localization on rhino2. Use this skill whenever the user says "neurorad" (strongest trigger), or mentions any of BrainX, VoxTool, ASHS, T1↔T2 registration, FreeSurfer recon-all in an iEEG context, coregistration of CT to MRI, MNI normalization of patient brains, whole-brain segmentation, runpipeline.sh, wholebrainseg.sh, $RAMROOT, /data10/RAM/subjects/, T00_*_mprage, T01_*_CT, RAM_maint or sudas accounts, subject codes like R1001P or R1724J, DICOM conversion for iEEG subjects, VOX_coords_mother.txt, voxel_coordinates.json, electrode localization, jacksheet, System 4 / Elemem configs, or asks about the steps that map iEEG electrode contacts to anatomical labels. Also use it when a lab member describes a failure in any of these steps and needs to debug. This skill is read-only by default — it reads pipeline scripts and wiki docs but never executes pipeline commands unless the user explicitly requests execution.
---

# Neurorad Pipeline

Help lab developers and pipeline runners understand, operate, and debug the Computational Memory Lab's Neurorad Pipeline — the system that localizes intracranial EEG (iEEG) electrodes by registering a post-implant CT to a pre-implant T1/T2 MRI, segmenting brain regions, and mapping each contact to an anatomical label.

## Environment check (do this first)

This skill only works on rhino2. Before answering any substantive question, confirm the environment:

1. Check whether `/data10/RAM/subjects/` exists. If it doesn't, you are not on rhino. Tell the user the skill is designed for Claude Code running on `rhino2.psych.upenn.edu` and that you can still answer doc-level questions from the bundled references but cannot read live scripts or subject data. Proceed with reference-only answers.
2. If the user gives a subject code (e.g., `R1001P`), do not export `$SUBJECT` yourself. Tell the user to `export SUBJECT=<CODE>` in their own shell. You use the code as a literal in paths you show them.

## What the pipeline does (one screen)

Seven ordered steps:

- **Step 0 — Jacksheet / configs.** Create subject dir under `/data10/RAM/subjects/$SUBJECT/`, build `docs/jacksheet`, and (if running stim experiments on System 4/Elemem) generate `.zip` configs. This is a research-coordinator workflow; the skill answers questions about it but does not walk through it unless asked.
- **Step 1 — Convert imaging.** DICOM → NIfTI for T1 (`mprage`), T2 (`tse`), and CT. QC voxel spacing, contrast, orientation.
- **Step 2 — FreeSurfer.** `recon-all` cortical parcellation on the T1. ~24h.
- **Step 3 — Segmentation + normalization (parallel).** NORM (nonlinear registration to MNI), MTL_SEG (ASHS on T2), WHOLE_BRAIN (BrainX skull-strip + multi-atlas segmentation).
- **Step 4 — VoxTool.** Mark electrode contacts in CT space → `voxel_coordinates.json`, `VOX_coords_mother.txt`.
- **Step 5 — Coregister CT ↔ MRI.**
- **Step 6 — Automatic localization.** Map contacts to anatomical labels.
- **Step 7 — event_creation submodule.** `./submit --localization-only`, then `./submit --montage-only`.

## Key paths on rhino

| What | Path |
|---|---|
| Subject root | `/data10/RAM/subjects/$SUBJECT/` |
| Imaging (`im`) | `/data10/RAM/subjects/$SUBJECT/imaging/$SUBJECT/` |
| Docs / jacksheet (`doc`) | `/data10/RAM/subjects/$SUBJECT/docs/` |
| Behavioral (`beh`) | `/data10/RAM/subjects/$SUBJECT/behavioral/` |
| FreeSurfer inputs | `/data/eeg/freesurfer/mris_used/$SUBJECT/` |
| FreeSurfer outputs | `/data/eeg/freesurfer/subjects/$SUBJECT/` |
| autoloc symlink | `/data10/RAM/subjects/$SUBJECT/imaging/autoloc` → `.../imaging/$SUBJECT/` |
| `$RAMROOT` (convention) | `/data10/RAM/subjects/$SUBJECT/imaging` |

Shell aliases available on rhino (once `SUBJECT` is exported): `newsub` (creates subject dir tree), `im` (cd to imaging/$SUBJECT), `doc` (cd to docs/), `beh` (cd to behavioral/). Surface these when walking a user through setup — they save keystrokes.

Pipeline scripts (for hybrid source-reading, see "Interpreting scripts" below):

- `~RAM_maint/imaging-scripts/` — `runpipeline.sh`, `wholebrainseg.sh`, segmentation helpers
- `~sudas/bin/` — utilities like `c3ddcm2nii.sh`, `visloc`, the bundled `itksnap` and `c3d`
- `~sudas/DARPA/scripts/` — older/alternate location some wiki pages point to
- `/home2/RAM_maint/elemem_scripts/` — `make_mon.py`, `generate_configs.py`, `parameters.py`

Standard filenames:

- T1 MRI: `T00_${SUBJECT}_mprage.nii.gz`
- T2 MRI: `T00_${SUBJECT}_tse.nii.gz`
- CT: `T01_${SUBJECT}_CT.nii.gz`

## Reference file map

Read the matching reference file on demand — don't preload them. Paths are relative to this skill's `references/` directory.

| Topic | File |
|---|---|
| Full pipeline overview (entry point) | `pipeline_overview.md` |
| Obtaining imaging from Jefferson (Step 1) | `jefferson_imaging_workflow.md` |
| DICOM → NIfTI conversion (Step 1) | `automatic_dicom_conversion.md` |
| System 4 / Elemem config generation (Step 0) | `creating_config_file_system4.md` |
| FreeSurfer `recon-all` (Step 2) | `surface_reconstructions.md` |
| MNI nonlinear normalization "NORM" (Step 3) | `nonlinear_normalization.md` |
| BrainX skull-stripping (Step 3) | `brain_extraction.md` |
| Whole-brain multi-atlas segmentation (Step 3) | `whole_brain_pipeline.md` |
| VoxTool electrode annotation (Step 4) | `voxtool.md` |
| CT ↔ MRI coregistration (Step 5) | `coregistration.md` |
| Manual coregistration fixes | `coregistration_fix.md` |
| Fixing failed T1↔T2 registration (ASHS) | `T1T2Fix.md` |
| Automatic localization (Step 6) | `localization.md` |
| ITK-SNAP visualization scripts | `visloc.md` |

**Gaps in this snapshot** — flag these to the user if they come up; point them at the upstream wiki or the `neurorad_pipeline` repo:

- **MTL segmentation (ASHS)** — the upstream wiki's `MTL_pipeline` page wasn't included. `pipeline_overview.md` Step 3 references it but the details aren't bundled here.
- **Jacksheet creation** — the `Creating_a_Jacksheet` page wasn't included. For anything beyond the one-line summary in `pipeline_overview.md` Step 0, send the user upstream.
- **Blender/Blend4Web electrode viz** — referenced from Step 7 ("Visualize and check results") but not bundled.

**Additional v2 topics inline in `pipeline_overview.md`** (not separate reference files): re-implant / new montage workflow, bypassing the localization pipeline with `generate_fake_pairs_contacts.py`. Point the user at the relevant section of the overview.

## Modes of use

### Find things
"Where is the script that does X?" → Point to the reference file AND the script path on rhino. When useful, run `grep -rn` to show the relevant lines.

### Walk through a step
"I'm at step N, what do I do?" → Open the matching reference file. Reproduce commands verbatim. For every command, annotate the account it runs under:

- `RAM_maint` → `sudo -s -u RAM_maint` then the command
- `sudas` → less common now; flag when a command still reaches into `~sudas/`
- local user → things like launching VoxTool on a laptop, or `ssh -X`

If the wiki is ambiguous about account, say so rather than guessing.

### Interpret a script
"What does `runpipeline.sh norm` actually do?" → Read the script from disk using the hybrid source policy (below). Explain. Apply the **confidence rule** (below). Do NOT invent code paths, flags, or file outputs not present in the script.

### Debug a failure
"My X failed / looks wrong." → Consult the failure-modes table below first. Match symptoms to a fix. Open the relevant reference file. If the symptom matches nothing in the table, say so and help the user gather diagnostics (log paths, `qstat`, output file existence) rather than speculating.

## Hybrid source policy for script-reading

When the user asks what a script does, read in this order:

1. **Rhino filesystem first.** Try paths in order: `~RAM_maint/imaging-scripts/`, `~sudas/bin/`, `~sudas/DARPA/scripts/`, `/home2/RAM_maint/elemem_scripts/`. Use the actual path you find it at.
2. **GitHub fallback.** If the file isn't on rhino (or you're not on rhino), fetch from the public pennmem repos. Prefer `gh` if installed, otherwise `git clone` over HTTPS or WebFetch to `https://raw.githubusercontent.com/pennmem/<repo>/main/<path>`.
3. **Tell the user which source you used.** One-liner: "Read from `~RAM_maint/imaging-scripts/runpipeline.sh` on rhino" or "Fetched from github.com/pennmem/imaging-scripts@main."
4. **If the script on rhino disagrees with the wiki**, trust the script for what the code does, flag the discrepancy, and note the wiki should be updated.

GitHub repos:

- `pennmem/imaging-scripts` — shell scripts (`runpipeline.sh`, `wholebrainseg.sh`, segmentation helpers)
- `pennmem/neurorad_pipeline` — Python pipeline + release notes
- `pennmem/event_creation` — `./submit` data submission
- `pennmem/voxTool` — VoxTool GUI
- `pennmem/brain_viz` — web localization viewer
- `pennmem/elemem_scripts` — config generation

## The confidence rule

Whenever you explain what a script does based on reading the code, OR make a claim based on a web search, tag the statement as interpretation and give a confidence score out of 10.

- Applies to: script-behavior explanations, online-search-based claims.
- Does NOT apply to: direct wiki quotes, debugging suggestions (already framed as "try this"), environment observations ("this path doesn't exist"), or things the user just told you.

**Example (script):** "The `norm` branch of `runpipeline.sh` dispatches to `ants_normalize.sh`, which wraps ANTs' `antsRegistrationSyN.sh` against the NickOasis template — **interpretation from reading the script, confidence 8/10**."

**Example (search):** "ANTs `antsRegistrationSyN.sh` defaults to a three-stage rigid→affine→SyN registration — **interpretation from ANTs docs, confidence 7/10**."

Lower the score when: the script has unfamiliar custom logic, you had to follow several levels of sourced helpers, or an online source is a forum post rather than official docs. Raise it when the script is short and self-explanatory or the wiki corroborates.

## Failure modes (debugging table)

When a user reports a symptom, match it here before going deeper.

| Symptom | Likely cause | Fix → ref |
|---|---|---|
| Segmentation edges look wrong around gyri/sulci | Image-quality issue | Manual ITK-SNAP correction; `whole_brain_pipeline.md` |
| Segmentation labels floating outside brain, esp. below | Registration pulled by neck/face tissue in T1 | BrainX first, then re-run whole-brain; `brain_extraction.md` + `whole_brain_pipeline.md` |
| ASHS / T1↔T2 registration fails | ASHS internal FLIRT failed | Copy T1↔T2 transform from coreg, rerun `mtlseg.sh`; `T1T2Fix.md` |
| Whole-brain seg hangs | Resolution too high for atlas registration | `c3d <img> -resample 50x50x100% -o <out>`; `whole_brain_pipeline.md` |
| CT ↔ T1 coreg visibly wrong | Auto-reg failed | ITK-SNAP Tools → Registration manual fix, then `runpipeline.sh coreg $SUBJECT USEMANUAL <tfm>`; `coregistration_fix.md` |
| MNI normalization fails | Neck tissue, bad orientation, or negative-intensity T1 | Crop with `c3d ... -region`; reorient with `c3d -swapdim RSP`; clip negatives; `nonlinear_normalization.md` |
| Images not in same bounding box | Mismatched field of view | `c3d img1 img2 -mbb ...`; general c3d fix |
| Coreg done before segmentation finished | Out-of-order pipeline (common when pre/post imaging arrive together) | Once seg completes, `runpipeline.sh cores $SUBJECT NOREG` transfers labels without redoing registration; `coregistration.md` |
| VoxTool threshold change wiped labels | User changed threshold mid-session | Save interim JSON before threshold changes; merge after; `voxtool.md` |
| `electrodelabels.csv` has NaNs / empty cells | Contacts without overlap with any segmentation label | Often means a contact is outside the brain mask or segmentation failed regionally; check seg quality first |

If nothing matches, gather diagnostics:

- `qstat` for running/queued jobs
- Existence check of the expected output file (each ref file lists it)
- Tail relevant log under `$RAMROOT/$SUBJECT/`
- `ls -la` the subject imaging dir

## Execution posture (read-only by default)

**Never run unprompted.** Even when the user describes a problem that obviously needs a pipeline step re-run, propose the command for them to run, don't run it yourself. Commands off-limits by default: `runpipeline.sh`, `wholebrainseg.sh`, `recon-all`, `ants*`, `c3d` (when it writes output), `itksnap`, `ssh`, `sudo -s -u`, `screen`, `slursh`, `qsub`/`qdel`, anything under `elemem_scripts/`.

**Read-only actions are fine:** `ls`, `cat`, `head`, `tail`, `grep`, `find`, `file`, `stat`, `qstat` (read-only), `c3d -info` (read-only query).

**Explicit-execution exception.** If the user says something unambiguous like "run it," "go ahead and execute that," or "submit the job" — confirm once ("Run `X` as RAM_maint? This will submit a job."), then do it. Any hedge from the user cancels.

## Guardrails

- **Don't invent filenames, paths, environment variables, or flags** that aren't in the wiki references, the scripts you actually read, or the user's own message. If uncertain, say "I don't see this documented — want me to grep for it?"
- **Don't invent variable names.** `$SUBJECT`, `$RAMROOT`, `$FREESURFER_HOME`, `$SUBJECTS_DIR` are real. If you'd need a variable that isn't in the wiki to complete a command, stop and ask.
- **Don't guess at out-of-scope internals.** If asked about classifier training, `event_creation` internals beyond `./submit --localization-only` and `--montage-only`, `brain_viz`, Ramulator, or anything not in the references, say "this isn't covered in the pipeline docs — the relevant repo is `github.com/pennmem/<X>`" and stop.
- **Wiki quoting.** The reference files are Markdown (converted from MediaWiki). Quote them as Markdown. If a command in the wiki looks wrong given what you see in the script, flag the discrepancy.
- **Subject IDs.** Real subject codes (e.g., `R1001P`) are fine to echo — they're research codes, not PHI. Still, don't read subject `behavioral/` directories unless the user's question explicitly requires it.
- **Account annotation.** Every shell command you show should say which account it runs under. If the wiki is silent, say so.

## Rule summary

1. Check the environment before answering.
2. Open reference files on demand — use the file map.
3. Read scripts from rhino first, GitHub as fallback, and always disclose the source.
4. Apply the confidence rule to script-interpretations and search-based claims.
5. Debug via the failure-modes table first.
6. Read-only by default; explicit confirmation before any execution.
7. Don't invent. Don't guess out-of-scope. Annotate accounts.
