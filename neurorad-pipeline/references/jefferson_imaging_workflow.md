# Requesting Jefferson Imaging

How to obtain imaging for Jefferson subjects through their internal server.

## Request workflow

1. Open Chrome on a Jefferson desktop (or via remote desktop) and go to **TJUH intranet** from the Jefferson Links bookmark.
2. Click the **Employee** tab.
3. Click the **IS&T / BioMed** tab.
4. Click **Service Requests**. Log into Service-Now with your Jefferson credentials.
5. Click **Request Something**.
6. In the left panel, click **Reports**, then **Jefferson Data Request Form**.
7. Select **Jefferson Medical Imaging Data Request Form** and fill in:
   - **Department**: Neurology
   - **Building**: 900 Walnut St, JHN
   - **Floor / Room**: 7th / 714
   - **Request type**: Prospective Clinical Trial
   - **Study info**: JeffTrial `6950`; Local IRB `14F.452`
   - **Principal Investigator**: Michael Sperling (`mrs101`)
8. Get patient information from EPIC:
   - **Name and MRN**: top-left panel of the patient overview.
   - **Accession numbers**: **Imaging** tab. Copy numbers for every study relevant to the protocol (MRI T1/T2, CT, fMRI, DWI, etc.).
   - Add name, MRN, and each accession number to the **Patient Information Radiology Research** table in the form.
9. Check **Agree**, click **Submit**. You'll get a confirmation email in your Jefferson account.

## Retrieving the data

1. When the request is completed, you'll receive a second email.
2. Go to Jefferson's Office 365 SharePoint.
3. Navigate to the **RadiologyImagingDataRequest** site.
4. Find the numbered folder for your request.
5. Descend into folders until you reach the **DICOM** folder.
6. Download the **`PAT_0000`** folder to your laptop or a flash drive.

## Identifying scans

Open the DICOM series in ITK-SNAP. Distinguish scans by number of images, voxel spacing, and fluid contrast:

- **T1**: 0.8–1.0 mm isotropic spacing. Fluid appears dark.
- **T2**: 0.5 × 0.5 × 2–4 mm. 30–60 images. Fluid appears bright.
- **CT**: 0.5 × 0.5 × ~1.0 mm. 100–150 images.

Rename the scans to the pipeline's standard filenames (`T00_${SUBJECT}_mprage.nii.gz`, `T00_${SUBJECT}_tse.nii.gz`, `T01_${SUBJECT}_CT.nii.gz`), transfer to rhino, and proceed with the rest of the pipeline (see `pipeline_overview.md`).
