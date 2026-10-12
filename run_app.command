#!/bin/bash
# Double-clickable macOS launcher for FuzzyTravel AI
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================="
echo "   FuzzyTravel AI — Σύστημα Τουριστικών Προτάσεων"
echo "================================================="
echo "Εκκίνηση εφαρμογής..."

# Open browser after a brief delay
(sleep 2 && open "http://localhost:8501") &

# Start streamlit
./venv/bin/streamlit run ui/app.py --server.port 8501
