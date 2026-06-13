#!/usr/bin/env bash
set -e

PORT="${PORT:-8501}"

streamlit run app.py \
  --server.address=0.0.0.0 \
  --server.port="$PORT" \
  --server.headless=true \
  --browser.gatherUsageStats=false
