# Quick Start Guide

## Installation

1. **Clone or navigate to the project directory**
```bash
cd /workspaces/Trade
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Basic Usage

### Analyze a Single Contract

```bash
python main.py --contract MAR26
```

This will:
- Fetch/generate data for the MAR26 contract
- Identify support and resistance levels
- Display a detailed text report
- Show an interactive chart (if not using `--no-chart`)

### Analyze Multiple Contracts

```bash
python main.py --contract MAR26 JUN26 SEP26 DEC26
```

### Export Charts and Data

```bash
python main.py --contract MAR26 --export
```

This saves:
- Interactive HTML chart: `output/MAR26_[timestamp].html`
- CSV with levels: `output/MAR26_levels_[timestamp].csv`

### Multi-Contract Comparison

```bash
python main.py --contract MAR26 JUN26 SEP26 --compare --export
```

## Custom Parameters

### Change Lookback Period

```bash
python main.py --contract JUN26 --lookback 60
```

### Adjust Sensitivity

```bash
python main.py --contract MAR26 --min-touches 3
```

This requires levels to be tested at least 3 times to be considered valid.

## Using Your Own Data

### Option 1: CSV Files

1. Create CSV files in the `data/` directory
2. Name them according to contract: `MAR26.csv`, `JUN26.csv`, etc.
3. Format (with header row):
```csv
Date,Open,High,Low,Close,Volume
2025-11-12,95.4750,95.5100,95.4500,95.4950,125000
2025-11-13,95.4950,95.5200,95.4700,95.5050,138000
```

### Option 2: Configure Data Source

Edit `config.yaml`:

```yaml
data_source:
  provider: "yahoo"  # or "csv" or "api"
  ticker_mapping:
    MAR26: "YOUR_TICKER_SYMBOL"
```

## Understanding the Output

### Sample Report

```
======================================================================
SOFR FUTURES ANALYSIS REPORT - MAR26
======================================================================
Date: 2026-02-12
Current Price: 96.1768
Implied SOFR Rate: 3.823%

SUPPORT LEVELS
Price        Distance     Strength   Last Test       Status
96.1026      0.0742       2          2026-02-05      ← NEAREST
95.9726      0.2042       3          2026-01-28      STRONG
```

**Interpreting the Data:**

- **Price**: The horizontal support/resistance level
- **Distance**: How far the level is from current price
- **Strength**: Number of times price tested this level (higher = stronger)
- **Last Test**: Most recent date price touched this level
- **Status**: 
  - NEAREST: Closest level to current price
  - STRONG: 3+ touches
  - MODERATE: 2 touches

### SOFR Pricing

SOFR futures are quoted as: **100 - SOFR rate**

- Price of 95.50 = 4.50% implied rate
- Price of 96.00 = 4.00% implied rate

**Higher price = Lower rate**

## Configuration

Edit `config.yaml` to customize:

```yaml
detection:
  lookback_days: 90           # Historical data period
  min_touches: 2              # Minimum touches for valid level
  price_tolerance: 0.005      # Clustering tolerance (0.5 bp)
  
visualization:
  width: 1400                 # Chart width in pixels
  height: 800                 # Chart height
  export_format: "html"       # "html", "png", or "both"
```

## Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --contract CONTRACTS      One or more contracts to analyze
  --lookback DAYS          Number of days of historical data
  --min-touches N          Minimum touches to validate a level
  --export                 Export charts and CSV files
  --compare                Create multi-contract comparison chart
  --config FILE            Path to config file (default: config.yaml)
  --no-chart               Skip chart generation (text only)
  -h, --help              Show help message
```

## Examples

### Example 1: Quick Analysis
```bash
python main.py --contract JUN26
```

### Example 2: Detailed Export
```bash
python main.py --contract MAR26 JUN26 --export
```

### Example 3: Sensitive Detection
```bash
python main.py --contract SEP26 --min-touches 3 --lookback 120
```

### Example 4: Comparison View
```bash
python main.py --contract MAR26 JUN26 SEP26 DEC26 --compare --export
```

## Troubleshooting

### No data available
- The tool will generate sample data for testing if real data isn't available
- Add your own CSV files to the `data/` directory
- Configure a data provider in `config.yaml`

### Charts not displaying
- Use `--no-chart` for text-only output
- Use `--export` to save charts as HTML files you can open in a browser

### Module not found errors
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Add Real Data**: Place CSV files in `data/` directory
2. **Customize Detection**: Adjust parameters in `config.yaml`
3. **Automate**: Set up scheduled analysis with cron or task scheduler
4. **Integrate**: Use the analysis results in your trading workflow

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review the [config.yaml](config.yaml) for all options
- Examine the sample output in the `output/` directory
