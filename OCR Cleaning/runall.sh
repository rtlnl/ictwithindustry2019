#!/bin/bash

num_procs=$1

declare -A pids=( )

for filename in ../../data/RTLNieuws\ OCR/*; do
  while (( ${#pids[@]} >= num_procs )); do
    wait -n
    for pid in "${!pids[@]}"; do
      kill -0 "$pid" &>/dev/null || unset "${pids[$pid]}"
    done
  done
  python clean_ocr.py $filename 
done

