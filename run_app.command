#!/bin/bash
# Double-clickable macOS launcher for FuzzyTravel AI
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "================================================="
echo "   FuzzyTravel AI — Σύστημα Τουριστικών Προτάσεων"
echo "   Πανεπιστήμιο Πειραιώς (UNIPI 2026)"
echo "================================================="

if [ ! -d "venv" ]; then
    echo "[1/3] Δημιουργία εικονικού περιβάλλοντος (venv)..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[2/3] Εγκατάσταση εξαρτήσεων (requirements.txt)..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "[3/3] Εκκίνηση εφαρμογής Streamlit..."
# Open browser after a brief delay
(sleep 2 && open "http://localhost:8501") &

streamlit run ui/app.py --server.port 8501
