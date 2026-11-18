#!/usr/bin/env bash
# Fetch the behavioral files of the Penn Electrophysiology of Encoding and Retrieval Study (PEERS),
# Experiments 1-5, from the public release: OpenNeuro ds004395, version 2.0.0 (CC0).
#
#   usage:  fetch_peers.sh [DEST]        (default DEST = ./peers-data)
#
# Only the behavioral event files (*_beh.tsv), the participant table and the dataset's own documentation are
# downloaded: 6,564 event files, about 1 GB on disk, well under a minute. No EEG is fetched (the EEG is ~8.7 TB
# and is kept in git-annex, as are the word-pool files under stimuli/, so git never pulls them).
#
# The clone is "blob-less" and sparse: git downloads only the files matched below. It needs git >= 2.25 and
# access to github.com. Re-running the script is safe; it does nothing if the files are already there.
set -euo pipefail
DEST=${1:-peers-data}
REPO=https://github.com/OpenNeuroDatasets/ds004395
PIN=798377a4d                # the commit of version 2.0.0 (1 June 2023) against which selftest.py was written
mkdir -p "$DEST"
cd "$DEST"
if [ ! -d ds004395/.git ]; then
  git clone --quiet --filter=blob:none --no-checkout "$REPO" ds004395
  git -C ds004395 sparse-checkout init --no-cone
  git -C ds004395 sparse-checkout set \
      '/README' '/CHANGES' '/dataset_description.json' '/participants.tsv' '/participants.json' \
      '/sub-*/ses-*/beh/*_beh.tsv' \
      '/sub-LTP063/ses-0/beh/*_beh.json' '/sub-LTP063/ses-8/beh/*_beh.json' '/sub-LTP063/ses-15/beh/*_beh.json' \
      '/sub-LTP331/ses-0/beh/*_beh.json' '/sub-LTP393/ses-5/beh/*_beh.json'
  git -C ds004395 checkout --quiet
fi
HEAD=$(git -C ds004395 rev-parse --short=9 HEAD)
N=$(find ds004395 -name '*_beh.tsv' | wc -l | tr -d ' ')
echo "PEERS behavioral files: $N in $(pwd)/ds004395 (commit $HEAD)"
if [ "$HEAD" != "$PIN" ]; then
  echo "NOTE: the dataset has moved past the commit the self-test was written against ($PIN)."
  echo "      Run selftest.py; if counts differ, read CHANGES in the dataset before trusting old numbers."
fi
