#!/usr/bin/env python3
"""
SOFR Futures Support & Resistance Analyzer - Streamlit Frontend
Interactive web interface for trading analysis
"""

import streamlit as st
import yaml
import os
import sys
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analyzer import SOFRAnalyzer
from src.visualizer import TradingVisualizer


# Page configuration
st.set_page_config(
    page_title="SOFR Futures Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        st.warning(f"Config file {config_path} not found, using defaults")
        return get_default_config()
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_default_config() -> dict:
    """Return default configuration"""
    return {
        'contracts': ['MAR26', 'JUN26', 'SEP26', 'DEC26'],
        'contract_specs': {
            'tick_size': 0.0025,
            'tick_value': 6.25,
            'contract_size': 1000000,
            'pricing': '100_minus_rate'
        },
        'detection': {
            'lookback_days': 90,
            'min_touches': 2,
            'price_tolerance': 0.005,
            'strength_threshold': 0.6,
            'pivot': {'left_bars': 5, 'right_bars': 5},
            'volume_profile': {'enabled': True, 'bins': 50},
            'fibonacci': {'enabled': False}
        },
        'data_source': {
            'provider': 'csv',
            'csv_path': 'data/'
        },
        'visualization': {
            'chart_type': 'candlestick',
            'show_volume': True,
            'highlight_levels': True,
            'color_scheme': {
                'resistance': '#FF4444',
                'support': '#44FF44',
                'neutral': '#FFAA00'
            },
            'width': 1400,
            'height': 800,
            'export_format': 'html',
            'export_path': 'output/'
        },
        'analysis': {
            'strong_level': 3,
            'moderate_level': 2,
            'recent_test_days': 30,
            'max_levels_per_side': 5,
            'round_to': 0.005
        }
    }


def format_level_strength(strength: float) -> str:
    """Format level strength score with color"""
    if strength >= 0.8:
        return "🟢 Strong"
    elif strength >= 0.6:
        return "🟡 Moderate"
    else:
        return "🔴 Weak"


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("📈 SOFR Futures Support & Resistance Analyzer")
    st.caption("Order-book style price ladder | Tick-by-tick precision | Real-time trading levels")
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Load config
        config = load_config()
        
        # Contract selection
        st.subheader("Contract Selection")
        available_contracts = config.get('contracts', ['MAR26', 'JUN26', 'SEP26', 'DEC26'])
        selected_contracts = st.multiselect(
            "Select Contracts to Analyze",
            options=available_contracts,
            default=[available_contracts[0]] if available_contracts else []
        )
        
        st.markdown("---")
        
        # Detection parameters
        st.subheader("Detection Parameters")
        
        lookback_days = st.slider(
            "Lookback Period (days)",
            min_value=30,
            max_value=365,
            value=config['detection']['lookback_days'],
            step=10,
            help="Number of days of historical data to analyze"
        )
        
        min_touches = st.slider(
            "Minimum Touches",
            min_value=2,
            max_value=10,
            value=config['detection']['min_touches'],
            step=1,
            help="Minimum number of price touches to validate a level"
        )
        
        price_tolerance = st.number_input(
            "Price Tolerance",
            min_value=0.001,
            max_value=0.050,
            value=config['detection']['price_tolerance'],
            step=0.001,
            format="%.3f",
            help="Price tolerance for level clustering (in basis points)"
        )
        
        strength_threshold = st.slider(
            "Strength Threshold",
            min_value=0.0,
            max_value=1.0,
            value=config['detection']['strength_threshold'],
            step=0.1,
            help="Minimum level strength score (0-1)"
        )
        
        st.markdown("---")
        
        # Trading specs display
        st.subheader("Contract Specs")
        tick_size = config['contract_specs'].get('tick_size', 0.0025)
        tick_value = config['contract_specs'].get('tick_value', 6.25)
        st.caption(f"Tick: {tick_size:.4f} (${tick_value:.2f}) | Pricing: 100 - Rate")
        
        st.markdown("---")
        
        # Visualization options
        st.subheader("Visualization Options")
        
        show_volume = st.checkbox(
            "Show Volume",
            value=config['visualization'].get('show_volume', True)
        )
        
        max_levels = st.slider(
            "Max Levels per Side",
            min_value=3,
            max_value=10,
            value=config['analysis'].get('max_levels_per_side', 5),
            step=1,
            help="Maximum number of support/resistance levels to display"
        )
        
        st.markdown("---")
        
        # Analysis mode
        st.subheader("Analysis Mode")
        analysis_mode = st.radio(
            "Select Mode",
            options=["Single Contract", "Multi-Contract Comparison"],
            index=0
        )
        
        st.markdown("---")
        
        # Analyze button
        analyze_button = st.button("🔍 Run Analysis", type="primary", use_container_width=True)
    
    # Main content area
    if not selected_contracts:
        st.info("👈 Please select at least one contract from the sidebar to begin analysis")
        
        # Display contract specifications
        st.subheader("Contract Specifications")
        specs = config.get('contract_specs', {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tick Size", f"{specs.get('tick_size', 0.0025)}")
        with col2:
            st.metric("Tick Value", f"${specs.get('tick_value', 6.25)}")
        with col3:
            st.metric("Contract Size", f"${specs.get('contract_size', 1000000):,.0f}")
        with col4:
            st.metric("Pricing", specs.get('pricing', '100_minus_rate'))
        
        return
    
    # Update config with user selections
    config['detection']['lookback_days'] = lookback_days
    config['detection']['min_touches'] = min_touches
    config['detection']['price_tolerance'] = price_tolerance
    config['detection']['strength_threshold'] = strength_threshold
    config['visualization']['show_volume'] = show_volume
    config['analysis']['max_levels_per_side'] = max_levels
    
    # Run analysis when button is clicked
    if analyze_button:
        with st.spinner('Analyzing contracts... This may take a moment.'):
            try:
                # Initialize analyzer and visualizer
                analyzer = SOFRAnalyzer(config)
                visualizer = TradingVisualizer(config)
                
                # Store results
                results_dict = {}
                
                # Analyze each selected contract
                for contract in selected_contracts:
                    try:
                        results = analyzer.analyze_contract(contract)
                        results_dict[contract] = results
                    except Exception as e:
                        st.error(f"Error analyzing {contract}: {str(e)}")
                
                # Store results in session state
                st.session_state['results'] = results_dict
                st.session_state['analysis_time'] = datetime.now()
                st.success("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Display results if available
    if 'results' in st.session_state and st.session_state['results']:
        results_dict = st.session_state['results']
        
        # Display analysis timestamp
        if 'analysis_time' in st.session_state:
            st.caption(f"Last analyzed: {st.session_state['analysis_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.markdown("---")
        
        # Single contract mode
        if analysis_mode == "Single Contract":
            for contract_name, results in results_dict.items():
                display_single_contract_analysis(contract_name, results, config)
                st.markdown("---")
        
        # Multi-contract comparison mode
        else:
            if len(results_dict) > 1:
                display_multi_contract_comparison(results_dict, config)
            else:
                st.warning("Please select multiple contracts for comparison mode")


def display_single_contract_analysis(contract_name: str, results: dict, config: dict):
    """Display analysis results for a single contract"""
    
    st.header(f"📊 {contract_name} Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate strong and moderate levels
    strong_support = len([l for l in results['support_levels'] if l.strength_score >= 0.8])
    moderate_support = len([l for l in results['support_levels'] if 0.6 <= l.strength_score < 0.8])
    strong_resistance = len([l for l in results['resistance_levels'] if l.strength_score >= 0.8])
    moderate_resistance = len([l for l in results['resistance_levels'] if 0.6 <= l.strength_score < 0.8])
    
    with col1:
        st.metric(
            "Current Price",
            f"{results['current_price']:.4f}",
            help="Latest closing price"
        )
    
    with col2:
        total_support = strong_support + moderate_support
        support_delta = f"🟢{strong_support} 🟡{moderate_support}"
        st.metric(
            "Support Levels",
            total_support,
            delta=support_delta,
            help="Strong and Moderate support levels"
        )
    
    with col3:
        total_resistance = strong_resistance + moderate_resistance
        resistance_delta = f"🟢{strong_resistance} 🟡{moderate_resistance}"
        st.metric(
            "Resistance Levels",
            total_resistance,
            delta=resistance_delta,
            help="Strong and Moderate resistance levels"
        )
    
    with col4:
        if results['statistics']:
            volatility = results['statistics'].get('volatility', 0) * 100
            st.metric(
                "Volatility",
                f"{volatility:.2f}%",
                help="Price volatility"
            )
    
    st.markdown("---")
    
    # Two columns: Chart and Levels
    col_chart, col_levels = st.columns([2, 1])
    
    with col_chart:
        st.subheader("Price Chart")
        
        # Create interactive chart
        fig = create_plotly_chart(results, config)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_levels:
        st.subheader("Key Levels")
        
        # Filter levels by strength
        strong_resistance = [l for l in results['resistance_levels'] if l.strength_score >= 0.8]
        moderate_resistance = [l for l in results['resistance_levels'] if 0.6 <= l.strength_score < 0.8]
        
        strong_support = [l for l in results['support_levels'] if l.strength_score >= 0.8]
        moderate_support = [l for l in results['support_levels'] if 0.6 <= l.strength_score < 0.8]
        
        # Create order-book style price ladder
        st.markdown("### 📊 Price Ladder")
        
        current = results['current_price']
        tick_size = config['contract_specs'].get('tick_size', 0.0025)
        
        # Combine and sort all levels
        all_levels = []
        for level in strong_resistance:
            all_levels.append({'price': level.price, 'type': 'resistance', 'strength': 'strong', 'touches': level.strength})
        for level in moderate_resistance:
            all_levels.append({'price': level.price, 'type': 'resistance', 'strength': 'moderate', 'touches': level.strength})
        for level in strong_support:
            all_levels.append({'price': level.price, 'type': 'support', 'strength': 'strong', 'touches': level.strength})
        for level in moderate_support:
            all_levels.append({'price': level.price, 'type': 'support', 'strength': 'moderate', 'touches': level.strength})
        
        # Sort from high to low (like order book)
        all_levels.sort(key=lambda x: x['price'], reverse=True)
        
        # Create table data
        if all_levels:
            tick_value = config['contract_specs'].get('tick_value', 6.25)
            table_html = '<table style="width:100%; font-family: monospace; font-size: 13px; border-collapse: collapse;">'
            table_html += '<thead><tr style="background: #262730; font-weight: bold;">'
            table_html += '<th style="padding: 8px; text-align: center;">Level</th>'
            table_html += '<th style="padding: 8px; text-align: right;">Price</th>'
            table_html += '<th style="padding: 8px; text-align: center;">Touches</th>'
            table_html += '<th style="padding: 8px; text-align: right;">Ticks</th>'
            table_html += '<th style="padding: 8px; text-align: right;">$ Value</th>'
            table_html += '<th style="padding: 8px; text-align: right;">Distance</th>'
            table_html += '</tr></thead><tbody>'
            
            for lvl in all_levels:
                price_diff = lvl['price'] - current
                ticks = int(price_diff / tick_size)
                pct = (price_diff / current) * 100
                dollar_value = abs(ticks) * tick_value
                
                # Color coding
                if lvl['type'] == 'resistance':
                    if lvl['strength'] == 'strong':
                        row_color = '#4a1c1c'  # Dark red
                        icon = '🔴'
                    else:
                        row_color = '#3a2c1c'  # Dark orange
                        icon = '🟠'
                else:
                    if lvl['strength'] == 'strong':
                        row_color = '#1c4a1c'  # Dark green
                        icon = '🟢'
                    else:
                        row_color = '#2c3a1c'  # Dark yellow-green
                        icon = '🟡'
                
                table_html += f'<tr style="background: {row_color}; border-bottom: 1px solid #444;">'
                table_html += f'<td style="padding: 6px; text-align: center;">{icon}</td>'
                table_html += f'<td style="padding: 6px; text-align: right; font-weight: bold;">{lvl["price"]:.4f}</td>'
                table_html += f'<td style="padding: 6px; text-align: center;">{lvl["touches"]}</td>'
                table_html += f'<td style="padding: 6px; text-align: right;">{ticks:+d}</td>'
                table_html += f'<td style="padding: 6px; text-align: right;">${dollar_value:.0f}</td>'
                table_html += f'<td style="padding: 6px; text-align: right;">{pct:+.2f}%</td>'
                table_html += '</tr>'
            
            # Add current price row
            table_html += '<tr style="background: #1a1a2e; border: 2px solid #FFD700; font-weight: bold;">'
            table_html += '<td style="padding: 8px; text-align: center;">⭐</td>'
            table_html += f'<td style="padding: 8px; text-align: right; color: #FFD700;">{current:.4f}</td>'
            table_html += '<td style="padding: 8px; text-align: center; color: #FFD700;">CURRENT</td>'
            table_html += '<td style="padding: 8px; text-align: right;">—</td>'
            table_html += '<td style="padding: 8px; text-align: right;">—</td>'
            table_html += '<td style="padding: 8px; text-align: right;">—</td>'
            table_html += '</tr>'
            
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Legend
            st.caption("🔴 Strong Resistance | 🟠 Moderate Resistance | 🟢 Strong Support | 🟡 Moderate Support")
        else:
            st.info("No strong or moderate levels detected")
    
    # Trading Analysis section
    st.markdown("---")
    col_analysis1, col_analysis2 = st.columns(2)
    
    with col_analysis1:
        st.subheader("🎯 Immediate Levels")
        
        # Find nearest support and resistance
        nearest_resistance = None
        nearest_support = None
        
        for level in strong_resistance + moderate_resistance:
            if level.price > results['current_price']:
                if not nearest_resistance or level.price < nearest_resistance.price:
                    nearest_resistance = level
        
        for level in strong_support + moderate_support:
            if level.price < results['current_price']:
                if not nearest_support or level.price > nearest_support.price:
                    nearest_support = level
        
        if nearest_resistance:
            ticks_to_r = int((nearest_resistance.price - results['current_price']) / config['contract_specs'].get('tick_size', 0.0025))
            pct_to_r = ((nearest_resistance.price / results['current_price'] - 1) * 100)
            strength_r = "Strong" if nearest_resistance.strength_score >= 0.8 else "Moderate"
            st.markdown(f"**Next Resistance:** `{nearest_resistance.price:.4f}`")
            st.caption(f"{strength_r} | +{ticks_to_r} ticks | +{pct_to_r:.2f}%")
        else:
            st.info("No resistance detected above")
        
        st.markdown("")
        
        if nearest_support:
            ticks_to_s = int((nearest_support.price - results['current_price']) / config['contract_specs'].get('tick_size', 0.0025))
            pct_to_s = ((nearest_support.price / results['current_price'] - 1) * 100)
            strength_s = "Strong" if nearest_support.strength_score >= 0.8 else "Moderate"
            st.markdown(f"**Next Support:** `{nearest_support.price:.4f}`")
            st.caption(f"{strength_s} | {ticks_to_s} ticks | {pct_to_s:.2f}%")
        else:
            st.info("No support detected below")
    
    with col_analysis2:
        st.subheader("📊 Market Context")
        
        # Calculate range to levels
        if nearest_resistance and nearest_support:
            total_range = nearest_resistance.price - nearest_support.price
            position_in_range = (results['current_price'] - nearest_support.price) / total_range
            
            st.progress(position_in_range)
            st.caption(f"Position in range: {position_in_range*100:.1f}%")
            
            if position_in_range > 0.7:
                st.warning("🔺 Near resistance - potential selling zone")
            elif position_in_range < 0.3:
                st.success("🔻 Near support - potential buying zone")
            else:
                st.info("↔️ Mid-range - neutral zone")
        
        # Statistics
        if results['statistics']:
            stats = results['statistics']
            st.markdown("")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.metric("Avg Volume", f"{stats.get('avg_volume', 0):,.0f}")
                st.metric("Trend", stats.get('trend', 'N/A').capitalize())
            with col_s2:
                st.metric("Price Range", f"{stats.get('price_range', 0):.4f}")
                st.metric("Days Analyzed", len(results['data']))
    
    # Export options
    st.subheader("💾 Export")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"Export {contract_name} Chart", key=f"export_chart_{contract_name}"):
            output_dir = config['visualization']['export_path']
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_path = os.path.join(output_dir, f"{contract_name}_{timestamp}.html")
            
            try:
                visualizer = TradingVisualizer(config)
                visualizer.create_chart(results, chart_path)
                st.success(f"Chart exported to {chart_path}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button(f"Export {contract_name} Data CSV", key=f"export_csv_{contract_name}"):
            output_dir = config['visualization']['export_path']
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = os.path.join(output_dir, f"{contract_name}_levels_{timestamp}.csv")
            
            try:
                visualizer = TradingVisualizer(config)
                visualizer.export_levels_to_csv(results, csv_path)
                st.success(f"Data exported to {csv_path}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")


def display_multi_contract_comparison(results_dict: dict, config: dict):
    """Display multi-contract comparison"""
    
    st.header("📊 Multi-Contract Comparison")
    
    # Create comparison table
    comparison_data = []
    for contract_name, results in results_dict.items():
        # Calculate strong and moderate levels
        strong_support = len([l for l in results['support_levels'] if l.strength_score >= 0.8])
        moderate_support = len([l for l in results['support_levels'] if 0.6 <= l.strength_score < 0.8])
        strong_resistance = len([l for l in results['resistance_levels'] if l.strength_score >= 0.8])
        moderate_resistance = len([l for l in results['resistance_levels'] if 0.6 <= l.strength_score < 0.8])
        
        # Get nearest strong level or moderate if no strong exists
        nearest_support = 'N/A'
        for level in results['support_levels']:
            if level.strength_score >= 0.6:
                nearest_support = f"{level.price:.4f}"
                break
        
        nearest_resistance = 'N/A'
        for level in results['resistance_levels']:
            if level.strength_score >= 0.6:
                nearest_resistance = f"{level.price:.4f}"
                break
        
        comparison_data.append({
            'Contract': contract_name,
            'Current Price': f"{results['current_price']:.4f}",
            'Support (🟢/🟡)': f"{strong_support}/{moderate_support}",
            'Resistance (🟢/🟡)': f"{strong_resistance}/{moderate_resistance}",
            'Nearest Support': nearest_support,
            'Nearest Resistance': nearest_resistance,
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Price comparison chart
    st.subheader("Price Comparison")
    
    fig = go.Figure()
    
    for contract_name, results in results_dict.items():
        df = results['data']
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name=contract_name,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title="Price Evolution Comparison",
        xaxis_title="Date",
        yaxis_title="Price",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Individual contract details
    st.markdown("---")
    st.subheader("Individual Contract Details")
    
    for contract_name, results in results_dict.items():
        with st.expander(f"{contract_name} - Levels Summary", expanded=False):
            col1, col2 = st.columns(2)
            
            # Filter levels
            strong_resistance = [l for l in results['resistance_levels'] if l.strength_score >= 0.8]
            moderate_resistance = [l for l in results['resistance_levels'] if 0.6 <= l.strength_score < 0.8]
            strong_support = [l for l in results['support_levels'] if l.strength_score >= 0.8]
            moderate_support = [l for l in results['support_levels'] if 0.6 <= l.strength_score < 0.8]
            
            with col1:
                st.markdown("**🔴 Resistance**")
                if strong_resistance:
                    st.markdown("🟢 Strong:")
                    for level in strong_resistance[:3]:
                        st.text(f"  {level.price:.4f}")
                if moderate_resistance:
                    st.markdown("🟡 Moderate:")
                    for level in moderate_resistance[:3]:
                        st.text(f"  {level.price:.4f}")
                if not strong_resistance and not moderate_resistance:
                    st.text("None detected")
            
            with col2:
                st.markdown("**🟢 Support**")
                if strong_support:
                    st.markdown("🟢 Strong:")
                    for level in strong_support[:3]:
                        st.text(f"  {level.price:.4f}")
                if moderate_support:
                    st.markdown("🟡 Moderate:")
                    for level in moderate_support[:3]:
                        st.text(f"  {level.price:.4f}")
                if not strong_support and not moderate_support:
                    st.text("None detected")


def create_plotly_chart(results: dict, config: dict):
    """Create an interactive Plotly chart"""
    
    df = results['data']
    show_volume = config['visualization'].get('show_volume', True)
    
    # Create subplots
    if show_volume:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('Price', 'Volume')
        )
    else:
        fig = go.Figure()
    
    # Candlestick chart
    candlestick = go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    )
    
    if show_volume:
        fig.add_trace(candlestick, row=1, col=1)
    else:
        fig.add_trace(candlestick)
    
    # Add support levels
    for level in results['support_levels']:
        fig.add_hline(
            y=level.price,
            line_dash="dash",
            line_color="green",
            opacity=0.6,
            annotation_text=f"S: {level.price:.4f}",
            annotation_position="right",
            row=1 if show_volume else None
        )
    
    # Add resistance levels
    for level in results['resistance_levels']:
        fig.add_hline(
            y=level.price,
            line_dash="dash",
            line_color="red",
            opacity=0.6,
            annotation_text=f"R: {level.price:.4f}",
            annotation_position="right",
            row=1 if show_volume else None
        )
    
    # Add volume bars
    if show_volume:
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                  for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title=f"{results['contract']} - Support & Resistance Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        height=700,
        showlegend=True,
        hovermode='x unified',
        xaxis_rangeslider_visible=False
    )
    
    if show_volume:
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig


if __name__ == '__main__':
    main()
