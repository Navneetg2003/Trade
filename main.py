#!/usr/bin/env python3
"""
SOFR Futures Support & Resistance Analyzer
Main entry point for the trading analysis tool

Usage:
    python main.py --contract MAR26
    python main.py --contract MAR26 JUN26 SEP26 DEC26
    python main.py --contract JUN26 --lookback 60 --export
"""

import argparse
import logging
import yaml
import os
import sys
from datetime import datetime

from src.analyzer import SOFRAnalyzer
from src.visualizer import TradingVisualizer


def setup_logging(verbose: bool = False):
    """Configure logging for the application"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    # Quiet down noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('yfinance').setLevel(logging.WARNING)


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        print(f"Warning: Config file {config_path} not found, using defaults")
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


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='SOFR Futures Support & Resistance Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single contract
  python main.py --contract MAR26
  
  # Analyze multiple contracts
  python main.py --contract MAR26 JUN26 SEP26 DEC26
  
  # Custom lookback period
  python main.py --contract JUN26 --lookback 60
  
  # Export charts and data
  python main.py --contract MAR26 --export
  
  # Multi-contract comparison chart
  python main.py --contract MAR26 JUN26 SEP26 --compare
        """
    )
    
    parser.add_argument(
        '--contract', 
        nargs='+',
        help='Contract(s) to analyze (e.g., MAR26, JUN26, SEP26, DEC26)'
    )
    
    parser.add_argument(
        '--lookback',
        type=int,
        help='Number of days of historical data to analyze'
    )
    
    parser.add_argument(
        '--min-touches',
        type=int,
        help='Minimum number of touches to validate a level'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export charts and CSV data'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Create multi-contract comparison chart'
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--no-chart',
        action='store_true',
        help='Skip chart generation (text output only)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose/debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger('main')
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.lookback:
        config['detection']['lookback_days'] = args.lookback
    
    if args.min_touches:
        config['detection']['min_touches'] = args.min_touches
    
    # Determine contracts to analyze
    if args.contract:
        contracts = args.contract
    else:
        contracts = config.get('contracts', ['MAR26', 'JUN26', 'SEP26', 'DEC26'])
    
    print("="*70)
    print("SOFR FUTURES SUPPORT & RESISTANCE ANALYZER")
    print("="*70)
    print(f"Analyzing contracts: {', '.join(contracts)}")
    print(f"Lookback period: {config['detection']['lookback_days']} days")
    print(f"Minimum touches: {config['detection']['min_touches']}")
    print("="*70)
    
    # Initialize analyzer and visualizer
    analyzer = SOFRAnalyzer(config)
    visualizer = TradingVisualizer(config)
    
    # Analyze contracts
    results_dict = {}
    
    for contract in contracts:
        try:
            results = analyzer.analyze_contract(contract)
            results_dict[contract] = results
            
            # Print report
            analyzer.print_analysis_report(results)
            
            # Export individual chart if requested
            if args.export and not args.no_chart:
                output_dir = config['visualization']['export_path']
                os.makedirs(output_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                chart_path = os.path.join(output_dir, f"{contract}_{timestamp}.html")
                
                visualizer.create_chart(results, chart_path)
                
                # Export CSV
                csv_path = os.path.join(output_dir, f"{contract}_levels_{timestamp}.csv")
                visualizer.export_levels_to_csv(results, csv_path)
            
            elif not args.no_chart and not args.compare:
                # Show individual chart
                visualizer.create_chart(results)
                
        except Exception as e:
            print(f"Error analyzing {contract}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create comparison chart if requested
    if args.compare and len(results_dict) > 1 and not args.no_chart:
        print(f"\nGenerating multi-contract comparison chart...")
        
        if args.export:
            output_dir = config['visualization']['export_path']
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            comparison_path = os.path.join(output_dir, f"comparison_{timestamp}.html")
            visualizer.create_multi_contract_comparison(results_dict, comparison_path)
        else:
            visualizer.create_multi_contract_comparison(results_dict)
    
    print("\nAnalysis complete!")
    
    if args.export:
        print(f"\nOutput files saved to: {config['visualization']['export_path']}")


if __name__ == '__main__':
    main()
