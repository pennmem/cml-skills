# Fixing Failed T1↔T2 Registration (ASHS)

If ASHS's internal T1↔T2 registration fails, you can substitute the T1↔T2 transform computed by the coregistration step. Because of this, coregistration (Step 5) must be complete before applying this fix.

## Procedure

The fix: copy the transform produced by the coregistration script to overwrite the one ASHS computes, then rerun `mtlseg.sh`.

Run as `RAM_maint`:

```bash
sudo -s -u RAM_maint
cd $RAMROOT
~/bin/c3d/bin/c3d_affine_tool \
  T00_tse_to_T00_mprageANTs0GenericAffine_RAS.mat \
  -oitk T00/sfseg/flirt_t2_to_t1/flirt_t2_to_t1_ITK.txt
```

After this completes, rerun `mtlseg.sh` to pick up the substituted transform.
