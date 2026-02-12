#!/bin/bash
# Example usage scripts for the SOFR Futures Analyzer

echo "SOFR Futures Analyzer - Example Commands"
echo "========================================"
echo ""

# Streamlit Web Interface
echo "WEB INTERFACE (Streamlit):"
echo "--------------------------------------"
echo "1. Launch web interface:"
echo "   streamlit run app.py"
echo "   or"
echo "   ./run_streamlit.sh"
echo ""
echo "2. Launch on custom port:"
echo "   streamlit run app.py --server.port 8080"
echo ""
echo ""

# Command Line Interface
echo "COMMAND LINE INTERFACE (CLI):"
echo "--------------------------------------"

# Example 1: Basic analysis
echo "1. Basic analysis of MAR26 contract:"
echo "   python main.py --contract MAR26"
echo ""

# Example 2: Multiple contracts
echo "2. Analyze quarterly contracts:"
echo "   python main.py --contract MAR26 JUN26 SEP26 DEC26"
echo ""

# Example 3: Export results
echo "3. Export charts and data:"
echo "   python main.py --contract MAR26 --export"
echo ""

# Example 4: Custom parameters
echo "4. Custom lookback and sensitivity:"
echo "   python main.py --contract JUN26 --lookback 60 --min-touches 3"
echo ""

# Example 5: Comparison chart
echo "5. Multi-contract comparison:"
echo "   python main.py --contract MAR26 JUN26 SEP26 --compare --export"
echo ""

# Example 6: Text-only output
echo "6. Text report only (no charts):"
echo "   python main.py --contract DEC26 --no-chart"
echo ""

echo "========================================"
echo "For more information, see QUICKSTART.md"
