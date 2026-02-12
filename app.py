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
    
    with col1:
        st.metric(
            "Current Price",
            f"{results['current_price']:.4f}",
            help="Latest closing price"
        )
    
    with col2:
        st.metric(
            "Support Levels",
            len(results['support_levels']),
            help="Number of detected support levels"
        )
    
    with col3:
        st.metric(
            "Resistance Levels",
            len(results['resistance_levels']),
            help="Number of detected resistance levels"
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
        
        # Resistance levels
        with st.expander("🔴 Resistance Levels", expanded=True):
            if results['resistance_levels']:
                for i, level in enumerate(results['resistance_levels'], 1):
                    st.markdown(f"""
                    **Level {i}**: `{level.price:.4f}`  
                    Touches: {level.touches} | Strength: {format_level_strength(level.strength_score)}  
                    Distance: {((level.price / results['current_price'] - 1) * 100):.2f}%
                    """)
                    st.markdown("---")
            else:
                st.info("No resistance levels detected")
        
        # Support levels
        with st.expander("🟢 Support Levels", expanded=True):
            if results['support_levels']:
                for i, level in enumerate(results['support_levels'], 1):
                    st.markdown(f"""
                    **Level {i}**: `{level.price:.4f}`  
                    Touches: {level.touches} | Strength: {format_level_strength(level.strength_score)}  
                    Distance: {((level.price / results['current_price'] - 1) * 100):.2f}%
                    """)
                    st.markdown("---")
            else:
                st.info("No support levels detected")
    
    # Statistics section
    if results['statistics']:
        st.subheader("📈 Statistics")
        
        stats = results['statistics']
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Mean Price", f"{stats.get('mean_price', 0):.4f}")
        with col2:
            st.metric("Price Range", f"{stats.get('price_range', 0):.4f}")
        with col3:
            st.metric("Avg Volume", f"{stats.get('avg_volume', 0):,.0f}")
        with col4:
            st.metric("Trend", stats.get('trend', 'N/A').capitalize())
        with col5:
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
        comparison_data.append({
            'Contract': contract_name,
            'Current Price': f"{results['current_price']:.4f}",
            'Support Levels': len(results['support_levels']),
            'Resistance Levels': len(results['resistance_levels']),
            'Nearest Support': f"{results['support_levels'][0].price:.4f}" if results['support_levels'] else 'N/A',
            'Nearest Resistance': f"{results['resistance_levels'][0].price:.4f}" if results['resistance_levels'] else 'N/A',
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
            
            with col1:
                st.markdown("**🔴 Resistance Levels**")
                if results['resistance_levels']:
                    for i, level in enumerate(results['resistance_levels'][:3], 1):
                        st.text(f"{i}. {level.price:.4f} (Touches: {level.touches})")
                else:
                    st.text("None detected")
            
            with col2:
                st.markdown("**🟢 Support Levels**")
                if results['support_levels']:
                    for i, level in enumerate(results['support_levels'][:3], 1):
                        st.text(f"{i}. {level.price:.4f} (Touches: {level.touches})")
                else:
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
