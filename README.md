# SOFR Futures Support & Resistance Analyzer

A Python-based trading analysis tool for identifying horizontal support and resistance levels in SOFR (Secured Overnight Financing Rate) futures contracts.

## Overview

This project analyzes SOFR futures contracts (pricing format: 100 - rate) and identifies key support and resistance levels to assist in trading decisions.

## Features

- **Multi-Contract Analysis**: Analyze multiple SOFR futures contracts (MAR26, JUN26, SEP26, DEC26, etc.)
- **Support & Resistance Detection**: Automatically identifies horizontal support and resistance levels
- **Visualization**: Interactive charts with marked S/R levels
- **Historical Analysis**: Uses price action and volume data
- **Customizable Parameters**: Adjust lookback periods, sensitivity, and detection methods

## Supported Contracts

- Quarterly SOFR futures (Mar, Jun, Sep, Dec expirations)
- Contract format: 100 - SOFR rate

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run app.py
```

The Streamlit app provides:
- Interactive parameter configuration
- Real-time chart updates
- Multi-contract comparison
- Easy export options

See [STREAMLIT.md](STREAMLIT.md) for detailed Streamlit usage guide.

### Command Line Interface

#### Basic Analysis

```python
python main.py --contract MAR26
```

#### Analyze Multiple Contracts

```python
python main.py --contract MAR26 JUN26 SEP26 DEC26
```

#### Custom Parameters

```python
python main.py --contract JUN26 --lookback 60 --min-touches 3
```

## Configuration

Edit `config.yaml` to customize:
- Data sources
- Detection sensitivity
- Minimum number of touches for level validation
- Lookback periods
- Visualization settings

## Project Structure

```
Trade/
├── README.md
├── STREAMLIT.md             # Streamlit frontend guide
├── requirements.txt
├── config.yaml
├── main.py                  # CLI entry point
├── app.py                   # Streamlit web app
├── .streamlit/              # Streamlit configuration
│   └── config.toml
├── src/
│   ├── __init__.py
│   ├── data_handler.py      # SOFR data fetching and processing
│   ├── level_detector.py    # S/R level detection algorithms
│   ├── analyzer.py           # Main analysis logic
│   └── visualizer.py         # Chart generation
├── data/
│   └── sample_data.csv       # Sample SOFR data
└── output/                   # Export directory
```

## Methods Used

1. **Pivot Points**: Identifies local highs and lows
2. **Price Clustering**: Finds price levels with repeated tests
3. **Volume Profile**: Incorporates volume data for level validation
4. **Fibonacci Retracements**: Optional Fibonacci-based levels

## Output

- Console output with detected levels
- Interactive charts (HTML/PNG)
- CSV export of support/resistance levels

## Requirements

- Python 3.8+
- pandas, numpy for data processing
- matplotlib, plotly for visualization
- yfinance or custom data source for market data

## Disclaimer

This tool is for educational and informational purposes only. Trading futures involves substantial risk of loss. Always conduct your own analysis and consult with a financial advisor before making trading decisions.
