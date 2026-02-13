"""
Trading Visualizer
Creates interactive charts with support and resistance levels
"""

import logging
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List
from .level_detector import Level
import os

logger = logging.getLogger(__name__)


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
        Create an interactive chart with support/resistance levels,
        Bollinger Bands, and RSI indicator.
        
        Args:
            results: Analysis results dictionary
            output_path: Path to save the chart (optional)
        """
        df = results['data']
        contract = results['contract']
        support_levels = results['support_levels']
        resistance_levels = results['resistance_levels']
        
        has_rsi = 'RSI' in df.columns
        has_bb = 'BB_Upper' in df.columns
        
        # Create subplots: Price + Volume + RSI
        row_count = 3 if has_rsi else 2
        row_heights = [0.55, 0.25, 0.20] if has_rsi else [0.7, 0.3]
        subplot_titles = (f'SOFR Futures - {contract}', 'Volume', 'RSI') if has_rsi \
                         else (f'SOFR Futures - {contract}', 'Volume')
        
        fig = make_subplots(
            rows=row_count, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=subplot_titles
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
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if has_bb:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['BB_Upper'],
                    mode='lines', line=dict(color='rgba(173,216,230,0.5)', width=1),
                    name='BB Upper', showlegend=False
                ), row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['BB_Lower'],
                    mode='lines', line=dict(color='rgba(173,216,230,0.5)', width=1),
                    name='BB Lower', fill='tonexty',
                    fillcolor='rgba(173,216,230,0.1)', showlegend=False
                ), row=1, col=1
            )
        
        # Add support levels
        for level in support_levels:
            # Main horizontal line
            opacity = 0.9 if level.strength_score >= 0.8 else 0.6
            width = 2.5 if level.strength_score >= 0.8 else 1.5
            fig.add_hline(
                y=level.price,
                line_dash="dash",
                line_color=self.colors.get('support', '#44FF44'),
                line_width=width,
                opacity=opacity,
                annotation_text=f"S: {level.price:.4f} ({level.strength}t, {level.strength_score:.0%})",
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
            opacity = 0.9 if level.strength_score >= 0.8 else 0.6
            width = 2.5 if level.strength_score >= 0.8 else 1.5
            fig.add_hline(
                y=level.price,
                line_dash="dash",
                line_color=self.colors.get('resistance', '#FF4444'),
                line_width=width,
                opacity=opacity,
                annotation_text=f"R: {level.price:.4f} ({level.strength}t, {level.strength_score:.0%})",
                annotation_position="right",
                row=1, col=1
            )
            
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
                    x=df.index, y=df['SMA_20'],
                    mode='lines', line=dict(color='orange', width=1),
                    name='SMA 20', opacity=0.7
                ), row=1, col=1
            )
        
        if 'SMA_50' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['SMA_50'],
                    mode='lines', line=dict(color='purple', width=1),
                    name='SMA 50', opacity=0.7
                ), row=1, col=1
            )
        
        if 'EMA_9' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['EMA_9'],
                    mode='lines', line=dict(color='cyan', width=1, dash='dot'),
                    name='EMA 9', opacity=0.5
                ), row=1, col=1
            )
        
        # Volume bars
        colors = ['#ef5350' if df['Close'].iloc[i] < df['Open'].iloc[i] 
                  else '#26a69a' for i in range(len(df))]
        
        fig.add_trace(
            go.Bar(
                x=df.index, y=df['Volume'],
                marker_color=colors, name='Volume', showlegend=False
            ), row=2, col=1
        )
        
        # Volume MA
        if 'Volume_MA' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['Volume_MA'],
                    mode='lines', line=dict(color='orange', width=1),
                    name='Vol MA', showlegend=False
                ), row=2, col=1
            )
        
        # RSI subplot
        if has_rsi:
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df['RSI'],
                    mode='lines', line=dict(color='#ab47bc', width=1.5),
                    name='RSI'
                ), row=3, col=1
            )
            # Overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.4, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.4, row=3, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=3, col=1)
            fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'SOFR Futures Analysis - {contract}',
            xaxis_title='Date',
            yaxis_title='Price (100 - rate)',
            width=self.viz_config.get('width', 1400),
            height=self.viz_config.get('height', 900),
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            template='plotly_dark'
        )
        
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        # Save or show
        if output_path:
            export_format = self.viz_config.get('export_format', 'html')
            
            if export_format in ('html', 'both'):
                html_path = output_path if output_path.endswith('.html') else output_path.replace('.png', '.html')
                fig.write_html(html_path)
                logger.info(f"Chart saved to: {html_path}")
            
            if export_format in ('png', 'both'):
                png_path = output_path if output_path.endswith('.png') else output_path.replace('.html', '.png')
                fig.write_image(png_path)
                logger.info(f"Chart saved to: {png_path}")
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
            xaxis_rangeslider_visible=False,
            template='plotly_dark'
        )
        
        if output_path:
            fig.write_html(output_path)
            logger.info(f"Multi-contract chart saved to: {output_path}")
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
        current_price = results['current_price']
        
        # Prepare data
        rows = []
        
        for level in results['support_levels']:
            distance = current_price - level.price
            rows.append({
                'Contract': contract,
                'Type': 'Support',
                'Price': level.price,
                'Strength_Touches': level.strength,
                'Strength_Score': round(level.strength_score, 3),
                'Distance': round(distance, 4),
                'Distance_Pct': round(distance / current_price * 100, 4),
                'Last_Test': level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A',
                'First_Test': level.first_test.strftime('%Y-%m-%d') if level.first_test else 'N/A',
                'Num_Touches': len(level.touches),
                'Avg_Volume_At_Level': round(level.avg_volume_at_level, 0),
            })
        
        for level in results['resistance_levels']:
            distance = level.price - current_price
            rows.append({
                'Contract': contract,
                'Type': 'Resistance',
                'Price': level.price,
                'Strength_Touches': level.strength,
                'Strength_Score': round(level.strength_score, 3),
                'Distance': round(distance, 4),
                'Distance_Pct': round(distance / current_price * 100, 4),
                'Last_Test': level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A',
                'First_Test': level.first_test.strftime('%Y-%m-%d') if level.first_test else 'N/A',
                'Num_Touches': len(level.touches),
                'Avg_Volume_At_Level': round(level.avg_volume_at_level, 0),
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        logger.info(f"Levels exported to: {output_path}")
