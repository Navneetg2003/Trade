"""
Trading Visualizer
Creates interactive charts with support and resistance levels
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from typing import Dict, List
from .level_detector import Level
import os


class TradingVisualizer:
    """Creates visualizations for trading analysis"""
    
    def __init__(self, config: Dict):
        """
        Initialize visualizer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.viz_config = config.get('visualization', {})
        self.colors = self.viz_config.get('color_scheme', {})
        
    def create_chart(self, results: Dict, output_path: str = None):
        """
        Create an interactive chart with support/resistance levels
        
        Args:
            results: Analysis results dictionary
            output_path: Path to save the chart (optional)
        """
        df = results['data']
        contract = results['contract']
        support_levels = results['support_levels']
        resistance_levels = results['resistance_levels']
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(f'SOFR Futures - {contract}', 'Volume')
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # Add support levels
        for level in support_levels:
            # Main horizontal line
            fig.add_hline(
                y=level.price,
                line_dash="dash",
                line_color=self.colors.get('support', '#44FF44'),
                line_width=2,
                opacity=0.7,
                annotation_text=f"S: {level.price:.4f} ({level.strength})",
                annotation_position="right",
                row=1, col=1
            )
            
            # Add markers for touches
            if level.touches:
                touch_dates = [t['date'] for t in level.touches]
                touch_prices = [t['price'] for t in level.touches]
                
                fig.add_trace(
                    go.Scatter(
                        x=touch_dates,
                        y=touch_prices,
                        mode='markers',
                        marker=dict(
                            color=self.colors.get('support', '#44FF44'),
                            size=8,
                            symbol='triangle-up'
                        ),
                        name=f'Support {level.price:.4f}',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Add resistance levels
        for level in resistance_levels:
            # Main horizontal line
            fig.add_hline(
                y=level.price,
                line_dash="dash",
                line_color=self.colors.get('resistance', '#FF4444'),
                line_width=2,
                opacity=0.7,
                annotation_text=f"R: {level.price:.4f} ({level.strength})",
                annotation_position="right",
                row=1, col=1
            )
            
            # Add markers for touches
            if level.touches:
                touch_dates = [t['date'] for t in level.touches]
                touch_prices = [t['price'] for t in level.touches]
                
                fig.add_trace(
                    go.Scatter(
                        x=touch_dates,
                        y=touch_prices,
                        mode='markers',
                        marker=dict(
                            color=self.colors.get('resistance', '#FF4444'),
                            size=8,
                            symbol='triangle-down'
                        ),
                        name=f'Resistance {level.price:.4f}',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        # Add moving averages if available
        if 'SMA_20' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['SMA_20'],
                    mode='lines',
                    line=dict(color='orange', width=1),
                    name='SMA 20',
                    opacity=0.7
                ),
                row=1, col=1
            )
        
        if 'SMA_50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['SMA_50'],
                    mode='lines',
                    line=dict(color='purple', width=1),
                    name='SMA 50',
                    opacity=0.7
                ),
                row=1, col=1
            )
        
        # Volume bars
        colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] 
                  else 'green' for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                marker_color=colors,
                name='Volume',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f'SOFR Futures Analysis - {contract}',
            xaxis_title='Date',
            yaxis_title='Price (100 - rate)',
            width=self.viz_config.get('width', 1400),
            height=self.viz_config.get('height', 800),
            hovermode='x unified',
            xaxis_rangeslider_visible=False
        )
        
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        # Save or show
        if output_path:
            export_format = self.viz_config.get('export_format', 'html')
            
            if export_format == 'html' or export_format == 'both':
                html_path = output_path.replace('.png', '.html')
                fig.write_html(html_path)
                print(f"Chart saved to: {html_path}")
            
            if export_format == 'png' or export_format == 'both':
                fig.write_image(output_path)
                print(f"Chart saved to: {output_path}")
        else:
            fig.show()
        
        return fig
    
    def create_multi_contract_comparison(self, results_dict: Dict[str, Dict], 
                                        output_path: str = None):
        """
        Create a comparison chart for multiple contracts
        
        Args:
            results_dict: Dictionary of analysis results for multiple contracts
            output_path: Path to save the chart
        """
        fig = make_subplots(
            rows=len(results_dict), cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=[f"{contract}" for contract in results_dict.keys()]
        )
        
        for i, (contract, results) in enumerate(results_dict.items(), 1):
            df = results['data']
            
            # Add candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=contract,
                    showlegend=False
                ),
                row=i, col=1
            )
            
            # Add S/R levels
            for level in results['support_levels']:
                fig.add_hline(
                    y=level.price,
                    line_dash="dash",
                    line_color=self.colors.get('support', '#44FF44'),
                    line_width=1,
                    opacity=0.5,
                    row=i, col=1
                )
            
            for level in results['resistance_levels']:
                fig.add_hline(
                    y=level.price,
                    line_dash="dash",
                    line_color=self.colors.get('resistance', '#FF4444'),
                    line_width=1,
                    opacity=0.5,
                    row=i, col=1
                )
        
        fig.update_layout(
            title='SOFR Futures Multi-Contract Analysis',
            height=400 * len(results_dict),
            width=self.viz_config.get('width', 1400),
            xaxis_rangeslider_visible=False
        )
        
        if output_path:
            fig.write_html(output_path)
            print(f"Multi-contract chart saved to: {output_path}")
        else:
            fig.show()
        
        return fig
    
    def export_levels_to_csv(self, results: Dict, output_path: str):
        """
        Export support and resistance levels to CSV
        
        Args:
            results: Analysis results
            output_path: Path to save CSV file
        """
        contract = results['contract']
        
        # Prepare data
        rows = []
        
        for level in results['support_levels']:
            rows.append({
                'Contract': contract,
                'Type': 'Support',
                'Price': level.price,
                'Strength': level.strength,
                'Last Test': level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A',
                'Num Touches': len(level.touches)
            })
        
        for level in results['resistance_levels']:
            rows.append({
                'Contract': contract,
                'Type': 'Resistance',
                'Price': level.price,
                'Strength': level.strength,
                'Last Test': level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A',
                'Num Touches': len(level.touches)
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        print(f"Levels exported to: {output_path}")
