#!/bin/bash
# Launch script for SOFR Futures Analyzer Streamlit App

echo "=========================================="
echo "SOFR Futures Analyzer - Web Interface"
echo "=========================================="
echo ""
echo "Starting Streamlit app..."
echo "The app will open in your default browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run app.py --server.headless false --server.port 8501
