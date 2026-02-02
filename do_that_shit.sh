#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <filename> <device> <freq1> [freq2 freq3 ...]"
  exit 1
fi

FILE_NAME=$1
DEVICE=$2
shift 2
FREQUENCIES=("$@")

PYTHON=/home/ssw969/moeboostvenv/bin/python
# Run experiments (sequential)
sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.5 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.1 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.05 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.01 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"
