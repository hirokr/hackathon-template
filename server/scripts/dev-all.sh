#!/usr/bin/env bash
set -euo pipefail

api_pid=""
worker_pid=""

cleanup() {
  if [[ -n "$api_pid" ]]; then
    kill "$api_pid" 2>/dev/null || true
  fi

  if [[ -n "$worker_pid" ]]; then
    kill "$worker_pid" 2>/dev/null || true
  fi

  wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM

echo "Starting API server (npm run dev)"
npm run dev &
api_pid=$!

echo "Starting product worker (npm run worker:dev)"
npm run worker:dev &
worker_pid=$!

wait -n "$api_pid" "$worker_pid"
