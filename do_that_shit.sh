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

# Busy in parallel
sudo "$PYTHON" busy_script.py --device "$DEVICE" &
BUSY_PID=$!

cleanup() {
  if kill -0 "$BUSY_PID" 2>/dev/null; then
    sudo kill "$BUSY_PID" 2>/dev/null || true
    sleep 0.2
    sudo kill -9 "$BUSY_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

# Run experiments (sequential)
sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.5 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.1 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.05 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"

sudo "$PYTHON" gpu_clock_latency_experiments.py \
  --cooldown 0.01 --filename "$FILE_NAME" --device "$DEVICE" --frequencies "${FREQUENCIES[@]}"
