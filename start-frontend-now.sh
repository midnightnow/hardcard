#!/bin/bash
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend
echo "Starting VetSorcery frontend on http://localhost:5173"
exec python3 -m http.server 5173 --bind 0.0.0.0