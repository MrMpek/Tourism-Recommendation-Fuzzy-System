@echo off
chcp 65001 > nul
echo ====================================================
echo   FuzzyTravel AI - Εμπειρο Συστημα Τουριστικων Προτασεων
echo   Πανεπιστημιο Πειραιως (UNIPI 2026)
echo ====================================================
echo.

IF NOT EXIST venv (
    echo [1/3] Δημιουργια εικονικου περιβαλλοντος (venv)...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [2/3] Εγκατασταση εξαρτησεων (requirements.txt)...
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate.bat
)

echo.
echo [3/3] Εκκινηση εφαρμογης Streamlit...
echo Η εφαρμογη ανοιγει στον browser στη διευθυνση: http://localhost:8501
streamlit run ui\app.py

pause
