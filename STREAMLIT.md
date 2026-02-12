# Streamlit Frontend Guide

## Overview

The Streamlit frontend provides an interactive web interface for the SOFR Futures Support & Resistance Analyzer.

## Installation

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Running the App

### Start the Streamlit app:

```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

### Command-line options:

```bash
# Run on a specific port
streamlit run app.py --server.port 8080

# Run without auto-opening browser
streamlit run app.py --server.headless true
```

## Features

### 1. Contract Selection
- Select one or multiple SOFR futures contracts
- Available contracts: MAR26, JUN26, SEP26, DEC26

### 2. Detection Parameters
- **Lookback Period**: Number of days of historical data (30-365 days)
- **Minimum Touches**: Required price touches to validate a level (2-10)
- **Price Tolerance**: Clustering tolerance in basis points (0.001-0.050)
- **Strength Threshold**: Minimum level strength score (0.0-1.0)

### 3. Visualization Options
- Toggle volume display
- Adjust maximum levels per side (3-10)
- Interactive candlestick charts with support/resistance levels

### 4. Analysis Modes

#### Single Contract Mode
- Detailed analysis per contract
- Interactive price chart with S/R levels
- Key metrics and statistics
- Level details with strength scores and distances

#### Multi-Contract Comparison
- Side-by-side contract comparison
- Price evolution comparison chart
- Summary table with all contracts

### 5. Export Options
- Export charts as HTML files
- Export level data as CSV files
- Files saved to `output/` directory

## Navigation

### Sidebar
- Configure all analysis parameters
- Select contracts and analysis mode
- Run analysis with the "Run Analysis" button

### Main Area
- View analysis results
- Interactive charts
- Level details and statistics
- Export controls

## Tips

1. **First Time Use**: Start with default parameters to get familiar with the interface
2. **Multiple Contracts**: Use comparison mode when analyzing 2+ contracts
3. **Parameter Tuning**: Adjust min_touches and price_tolerance for different market conditions
4. **Export**: Export charts before changing parameters to preserve your analysis

## Keyboard Shortcuts

- `R` - Rerun the app
- `Ctrl/Cmd + K` - Clear cache
- `?` - Show keyboard shortcuts help

## Troubleshooting

### App won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8501 is already in use

### No data displayed
- Verify data files exist in the `data/` directory
- Check `config.yaml` for correct data source settings

### Charts not rendering
- Clear browser cache
- Try a different browser
- Restart the Streamlit app

## Configuration

The app automatically loads settings from `config.yaml`. You can override most settings through the sidebar UI.

For persistent changes, edit `config.yaml` directly.

## Performance

- Analysis is cached to improve performance
- Re-run analysis only when parameters change
- Large lookback periods may take longer to process

## Support

For issues or questions, refer to the main [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md).
