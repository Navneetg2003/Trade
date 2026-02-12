@echo off
REM Launch script for SOFR Futures Analyzer Streamlit App (Windows)

echo ==========================================
echo SOFR Futures Analyzer - Web Interface
echo ==========================================
echo.
echo Starting Streamlit app...
echo The app will open in your default browser
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch Streamlit
streamlit run app.py --server.headless false --server.port 8501
