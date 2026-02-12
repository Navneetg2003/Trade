# Streamlit Frontend Features

## 📋 Overview

The Streamlit frontend transforms the SOFR Futures Analyzer into an interactive web application, making technical analysis accessible without requiring command-line expertise.

## 🎯 Key Features

### 1. Interactive Sidebar Controls

#### Contract Selection
- **Multi-select dropdown** for choosing contracts
- Default contracts: MAR26, JUN26, SEP26, DEC26
- Can select single or multiple contracts simultaneously
- Dynamic updates based on configuration file

#### Detection Parameters (Real-time Adjustment)
- **Lookback Period Slider**: 30-365 days
  - Visual slider for easy adjustment
  - Default: 90 days
  - Tooltip with explanation
  
- **Minimum Touches Slider**: 2-10 touches
  - Validates support/resistance levels
  - Higher values = stricter validation
  - Default: 2 touches

- **Price Tolerance Input**: 0.001-0.050
  - Fine-grained control with step increments
  - Controls level clustering sensitivity
  - Default: 0.005 (0.5 basis points)

- **Strength Threshold Slider**: 0.0-1.0
  - Filters levels by confidence score
  - Default: 0.6
  - Visual scale with step of 0.1

#### Visualization Options
- **Show Volume Toggle**: Enable/disable volume bars
- **Max Levels Slider**: 3-10 levels per side
  - Controls display density
  - Prevents chart clutter

#### Analysis Mode Selection
- Radio buttons for mode switching:
  - **Single Contract**: Detailed individual analysis
  - **Multi-Contract Comparison**: Side-by-side comparison

### 2. Dashboard Layout

#### Header Section
- Clear title and branding
- Separation with visual dividers
- Analysis timestamp display

#### Metrics Display (Single Contract)
Four-column metric cards showing:
- **Current Price**: Latest closing price with 4 decimal precision
- **Support Levels**: Count of detected support levels
- **Resistance Levels**: Count of detected resistance levels  
- **Volatility**: Percentage-based volatility metric

#### Interactive Charts
- **Plotly-based candlestick charts**
  - Zoom and pan capabilities
  - Hover tooltips with detailed information
  - Responsive design
  - Export to PNG from chart menu

- **Support/Resistance Level Overlays**
  - Green dashed lines for support
  - Red dashed lines for resistance
  - Price labels on the right side
  - Adjustable opacity

- **Volume Bars** (optional)
  - Color-coded by price direction
  - Red for down days, green for up days
  - Synchronized with price chart
  - Separate subplot for clarity

#### Levels Summary Panel
Located in right column beside chart:

**Resistance Levels Expander** (Red 🔴)
- Collapsible accordion-style display
- Numbered levels (1, 2, 3...)
- Price with 4 decimal precision
- Touch count
- Strength indicator (Strong/Moderate/Weak with emoji)
- Percentage distance from current price

**Support Levels Expander** (Green 🟢)
- Same format as resistance levels
- Sorted by proximity to current price
- Distance calculated as negative percentage

### 3. Multi-Contract Comparison Mode

#### Comparison Table
- **Structured DataTable** with columns:
  - Contract name
  - Current price
  - Number of support levels
  - Number of resistance levels
  - Nearest support level
  - Nearest resistance level
- Sortable columns
- Full-width display
- Hidden index for cleaner look

#### Price Evolution Chart
- **Multi-line Time Series**
  - One line per contract
  - Different colors per contract
  - Unified hover mode
  - Horizontal legend at top
  - Date on X-axis, Price on Y-axis
  - 600px height for detailed view

#### Expandable Contract Details
- One expander per contract
- Shows top 3 support and resistance levels
- Compact text format
- Touch count displayed
- Easy scanning of multiple contracts

### 4. Statistics Section

Five-column statistics display:
- **Mean Price**: Average price over analysis period
- **Price Range**: High - Low spread
- **Average Volume**: Mean daily volume
- **Trend**: Detected trend direction (Up/Down/Sideways)
- **Days Analyzed**: Total data points used

### 5. Export Functionality

#### Chart Export
- Button-triggered export
- Saves interactive HTML file
- Includes all interactivity
- Timestamped filename format: `{CONTRACT}_{TIMESTAMP}.html`
- Success/error notifications

#### CSV Export
- Separate button for data export
- Exports support and resistance levels
- Include level details (price, touches, strength)
- Timestamped filename format: `{CONTRACT}_levels_{TIMESTAMP}.csv`
- Saved to `output/` directory

### 6. User Experience Enhancements

#### Loading States
- **Spinner Animation**: "Analyzing contracts... This may take a moment."
- Prevents multiple simultaneous analyses
- Clear visual feedback

#### Success/Error Messages
- ✅ **Success Toast**: "Analysis complete!"
- ❌ **Error Alerts**: Detailed error messages with traceback
- ⚠️ **Warning Messages**: Configuration issues
- ℹ️ **Info Messages**: Guidance for first-time users

#### Help Text
- Tooltips on all major controls
- Parameter explanations in hover text
- Context-sensitive guidance

#### Responsive Design
- Adapts to different screen sizes
- Wide layout for desktop viewing
- Proper column wrapping on smaller screens
- Full-width charts

### 7. Performance Optimizations

#### Caching
- `@st.cache_data` decorator on config loading
- Prevents redundant file reads
- Faster subsequent runs

#### Session State Management
- Analysis results stored in `st.session_state`
- Prevents re-analysis on parameter changes
- Preserves results across interactions
- Timestamp tracking

#### Conditional Rendering
- Only renders when results exist
- Prevents empty states
- Efficient re-rendering

### 8. Visual Design

#### Color Scheme (Dark Theme)
- **Primary Color**: #FF4444 (Red accent)
- **Background**: #0E1117 (Dark)
- **Secondary Background**: #262730
- **Text**: #FAFAFA (Light)
- Professional trading aesthetic

#### Typography
- Sans-serif font family
- Clear hierarchy with headers
- Monospace for price values
- Proper spacing and padding

#### Layout
- Wide mode enabled by default
- Sidebar expanded on load
- Logical grouping of elements
- Visual separators between sections

### 9. Customization Options

#### Through UI
- All detection parameters
- Visualization toggles
- Export controls
- Analysis modes

#### Through Config File
- Default contract list
- Color schemes
- Tick sizes and values
- Data source settings
- Advanced detection algorithms

### 10. Accessibility Features

#### Keyboard Navigation
- Standard Streamlit shortcuts
- Tab navigation through controls
- Enter to submit

#### Status Indicators
- Clear loading states
- Success/failure feedback
- Progress visibility

#### Error Handling
- Graceful degradation
- Clear error messages
- Helpful suggestions
- Fallback to defaults

## 🎨 Visual Elements

### Level Strength Indicators
- 🟢 **Strong**: High confidence (≥0.8)
- 🟡 **Moderate**: Medium confidence (0.6-0.8)  
- 🔴 **Weak**: Lower confidence (<0.6)

### Chart Annotations
- Support: Green dashed lines with "S:" prefix
- Resistance: Red dashed lines with "R:" prefix
- Current price highlighted
- Volume synchronized

### Interactive Features
- Click and drag to zoom
- Double-click to reset
- Download chart as PNG
- Save chart as HTML
- Toggle traces on/off

## 🔄 Workflow

1. **Configure** parameters in sidebar
2. **Select** contracts to analyze
3. **Click** "Run Analysis" button
4. **View** interactive results
5. **Export** charts and data if needed
6. **Adjust** parameters and re-run
7. **Compare** multiple contracts

## 📱 Browser Compatibility

✅ Tested on:
- Chrome/Chromium
- Firefox
- Safari
- Edge

## 🚀 Performance

- Fast initial load
- Sub-second updates after first analysis
- Efficient caching
- Responsive interaction
- Smooth animations

## 💡 Use Cases

1. **Quick Analysis**: Rapid contract evaluation
2. **Parameter Tuning**: Test different detection settings
3. **Multi-Contract Screening**: Compare opportunities
4. **Export for Sharing**: Generate reports for team
5. **Learning**: Understand S/R detection visually

## 🎓 Learning Curve

- **Beginner**: Use defaults, click analyze - 2 minutes
- **Intermediate**: Adjust parameters - 5 minutes
- **Advanced**: Multi-contract comparison and tuning - 10 minutes

## 📊 Data Visualization Benefits

- **Interactive** over static charts
- **Real-time** parameter effects
- **Comparative** analysis made easy
- **Exportable** for presentations
- **Shareable** HTML reports

---

**The Streamlit frontend makes professional SOFR futures analysis accessible to traders of all experience levels.**
