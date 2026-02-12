# SOFR Futures Analyzer - Quick Reference

## 🚀 Getting Started

### Installation
```bash
pip install -r requirements.txt
```

## 🌐 Web Interface (Recommended)

### Start the App
```bash
streamlit run app.py
```
or
```bash
./run_streamlit.sh
```

### Features
- ✅ Interactive parameter controls
- ✅ Real-time chart updates
- ✅ Multi-contract comparison
- ✅ One-click export
- ✅ No coding required

**Access**: Opens automatically in your browser at `http://localhost:8501`

---

## 💻 Command Line Interface

### Basic Commands

```bash
# Single contract analysis
python main.py --contract MAR26

# Multiple contracts
python main.py --contract MAR26 JUN26 SEP26 DEC26

# Custom parameters
python main.py --contract JUN26 --lookback 60 --min-touches 3

# Export results
python main.py --contract MAR26 --export

# Comparison chart
python main.py --contract MAR26 JUN26 SEP26 --compare --export

# Text-only output
python main.py --contract DEC26 --no-chart
```

### CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--contract` | Contract(s) to analyze | `--contract MAR26` |
| `--lookback` | Days of historical data | `--lookback 60` |
| `--min-touches` | Minimum level touches | `--min-touches 3` |
| `--export` | Export charts and CSV | `--export` |
| `--compare` | Multi-contract chart | `--compare` |
| `--no-chart` | Text output only | `--no-chart` |
| `--config` | Config file path | `--config config.yaml` |

---

## 📊 Understanding the Output

### Support Levels (Green)
- Price levels where buying interest prevented further decline
- Closer levels = stronger immediate support

### Resistance Levels (Red)
- Price levels where selling pressure prevented further rise
- Closer levels = stronger immediate resistance

### Level Strength
- 🟢 **Strong** (≥0.8): High confidence, multiple touches
- 🟡 **Moderate** (0.6-0.8): Medium confidence
- 🔴 **Weak** (<0.6): Lower confidence

---

## ⚙️ Configuration

### Quick Settings (Streamlit Sidebar)
- **Lookback Period**: 30-365 days (default: 90)
- **Minimum Touches**: 2-10 touches (default: 2)
- **Price Tolerance**: Clustering range (default: 0.005)
- **Strength Threshold**: Min confidence (default: 0.6)

### Advanced Settings (config.yaml)
Edit `config.yaml` for:
- Data sources
- Volume profile settings
- Fibonacci levels
- Chart styling
- Export paths

---

## 📁 File Outputs

### During Streamlit Session
- Interactive charts in browser
- Real-time updates

### Exported Files (output/ directory)
- `{CONTRACT}_{TIMESTAMP}.html` - Interactive chart
- `{CONTRACT}_levels_{TIMESTAMP}.csv` - Level data
- `comparison_{TIMESTAMP}.html` - Multi-contract chart

---

## 🔧 Troubleshooting

### Streamlit won't start
```bash
# Check installation
pip install streamlit

# Check port availability
streamlit run app.py --server.port 8080
```

### No data displayed
```bash
# Verify data directory
ls data/

# Check config
cat config.yaml
```

### Charts not rendering
- Clear browser cache (Ctrl+Shift+Delete)
- Try incognito/private mode
- Restart Streamlit app

---

## 📚 Documentation

- **Streamlit Guide**: [STREAMLIT.md](STREAMLIT.md)
- **Full README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Examples**: Run `./examples.sh`

---

## 🎯 Tips

1. **Start Simple**: Use default settings first
2. **Tune Gradually**: Adjust one parameter at a time
3. **Export Early**: Save analysis before changing settings
4. **Compare Contracts**: Use comparison mode for spread analysis
5. **Watch Strength**: Focus on strong (🟢) levels for trading decisions

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Trading futures involves substantial risk. Always conduct your own analysis and consult with financial advisors before making trading decisions.

---

**Last Updated**: February 2026  
**Version**: 1.0.0 with Streamlit Frontend
