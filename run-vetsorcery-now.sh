#!/bin/bash

echo "🚀 Starting VetSorcery with minimal setup..."

cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# Use npx to run vite without config file
npx vite@4 serve . --port 5173 --open --config /dev/null