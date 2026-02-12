"""
SOFR Analyzer
Main analysis class that coordinates data fetching, level detection, and reporting
"""

import pandas as pd
from typing import Dict, List, Tuple
from .data_handler import SOFRDataHandler
from .level_detector import LevelDetector, Level


class SOFRAnalyzer:
    """Main analyzer for SOFR futures support and resistance"""
    
    def __init__(self, config: Dict):
        """
        Initialize analyzer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_handler = SOFRDataHandler(config)
        self.level_detector = LevelDetector(config)
        self.analysis_config = config.get('analysis', {})
        
    def analyze_contract(self, contract: str) -> Dict:
        """
        Analyze a single SOFR futures contract
        
        Args:
            contract: Contract name (e.g., 'MAR26')
            
        Returns:
            Dictionary with analysis results
        """
        # Fetch data
        lookback_days = self.config['detection']['lookback_days']
        df = self.data_handler.get_contract_data(contract, lookback_days)
        
        # Add technical indicators
        df = self.data_handler.calculate_indicators(df)
        
        # Detect levels
        support_levels, resistance_levels = self.level_detector.find_support_resistance(df)
        
        # Get current price
        current_price = df['Close'].iloc[-1]
        current_date = df.index[-1]
        
        # Filter and rank levels
        max_levels = self.analysis_config.get('max_levels_per_side', 5)
        
        # Get nearest levels
        nearest_supports = self.level_detector.get_nearest_levels(
            support_levels, current_price, max_levels
        )
        nearest_resistances = self.level_detector.get_nearest_levels(
            resistance_levels, current_price, max_levels
        )
        
        # Calculate strength scores
        for level in nearest_supports:
            level.strength_score = self.level_detector.calculate_level_strength_score(level, df)
        
        for level in nearest_resistances:
            level.strength_score = self.level_detector.calculate_level_strength_score(level, df)
        
        # Sort by price
        nearest_supports.sort(key=lambda x: x.price, reverse=True)
        nearest_resistances.sort(key=lambda x: x.price)
        
        # Compile results
        results = {
            'contract': contract,
            'current_price': current_price,
            'current_date': current_date,
            'data': df,
            'support_levels': nearest_supports,
            'resistance_levels': nearest_resistances,
            'all_support_levels': support_levels,
            'all_resistance_levels': resistance_levels,
            'statistics': self._calculate_statistics(df, nearest_supports, nearest_resistances)
        }
        
        return results
    
    def analyze_multiple_contracts(self, contracts: List[str]) -> Dict[str, Dict]:
        """
        Analyze multiple SOFR futures contracts
        
        Args:
            contracts: List of contract names
            
        Returns:
            Dictionary mapping contract names to analysis results
        """
        results = {}
        
        for contract in contracts:
            print(f"\nAnalyzing {contract}...")
            results[contract] = self.analyze_contract(contract)
        
        return results
    
    def _calculate_statistics(self, df: pd.DataFrame, 
                             supports: List[Level], 
                             resistances: List[Level]) -> Dict:
        """
        Calculate statistical information about the analysis
        
        Args:
            df: Price data DataFrame
            supports: Support levels
            resistances: Resistance levels
            
        Returns:
            Dictionary with statistics
        """
        current_price = df['Close'].iloc[-1]
        
        # Find nearest support and resistance
        nearest_support = None
        nearest_resistance = None
        
        if supports:
            supports_below = [s for s in supports if s.price < current_price]
            if supports_below:
                nearest_support = max(supports_below, key=lambda x: x.price)
        
        if resistances:
            resistances_above = [r for r in resistances if r.price > current_price]
            if resistances_above:
                nearest_resistance = min(resistances_above, key=lambda x: x.price)
        
        # Calculate distances
        support_distance = (current_price - nearest_support.price) if nearest_support else None
        resistance_distance = (nearest_resistance.price - current_price) if nearest_resistance else None
        
        # Calculate range
        trading_range = None
        if nearest_support and nearest_resistance:
            trading_range = nearest_resistance.price - nearest_support.price
            position_in_range = (current_price - nearest_support.price) / trading_range
        else:
            position_in_range = None
        
        stats = {
            'current_price': current_price,
            'nearest_support': nearest_support.price if nearest_support else None,
            'nearest_resistance': nearest_resistance.price if nearest_resistance else None,
            'support_distance': support_distance,
            'resistance_distance': resistance_distance,
            'support_distance_pct': (support_distance / current_price * 100) if support_distance else None,
            'resistance_distance_pct': (resistance_distance / current_price * 100) if resistance_distance else None,
            'trading_range': trading_range,
            'position_in_range': position_in_range,
            'total_support_levels': len(supports),
            'total_resistance_levels': len(resistances),
            'atr': df['ATR'].iloc[-1] if 'ATR' in df.columns else None
        }
        
        return stats
    
    def print_analysis_report(self, results: Dict):
        """
        Print a formatted analysis report
        
        Args:
            results: Analysis results dictionary
        """
        print(f"\n{'='*70}")
        print(f"SOFR FUTURES ANALYSIS REPORT - {results['contract']}")
        print(f"{'='*70}")
        print(f"Date: {results['current_date'].strftime('%Y-%m-%d')}")
        print(f"Current Price: {results['current_price']:.4f}")
        
        implied_rate = self.data_handler.convert_to_rate(results['current_price'])
        print(f"Implied SOFR Rate: {implied_rate:.3f}%")
        
        stats = results['statistics']
        
        print(f"\n{'-'*70}")
        print("SUPPORT LEVELS")
        print(f"{'-'*70}")
        
        if results['support_levels']:
            print(f"{'Price':<12} {'Distance':<12} {'Strength':<10} {'Last Test':<15} {'Status'}")
            print(f"{'-'*70}")
            
            for level in results['support_levels']:
                distance = results['current_price'] - level.price
                distance_pct = (distance / results['current_price']) * 100
                
                # Determine status
                if level == self._get_nearest_level(results['support_levels'], 
                                                   results['current_price'], 'below'):
                    status = "← NEAREST"
                elif level.strength >= self.analysis_config.get('strong_level', 3):
                    status = "STRONG"
                else:
                    status = "MODERATE"
                
                last_test = level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A'
                
                print(f"{level.price:<12.4f} "
                      f"{distance:>6.4f} ({distance_pct:>5.2f}%) "
                      f"{level.strength:<10} "
                      f"{last_test:<15} "
                      f"{status}")
        else:
            print("No support levels detected")
        
        print(f"\n{'-'*70}")
        print("RESISTANCE LEVELS")
        print(f"{'-'*70}")
        
        if results['resistance_levels']:
            print(f"{'Price':<12} {'Distance':<12} {'Strength':<10} {'Last Test':<15} {'Status'}")
            print(f"{'-'*70}")
            
            for level in results['resistance_levels']:
                distance = level.price - results['current_price']
                distance_pct = (distance / results['current_price']) * 100
                
                # Determine status
                if level == self._get_nearest_level(results['resistance_levels'], 
                                                   results['current_price'], 'above'):
                    status = "← NEAREST"
                elif level.strength >= self.analysis_config.get('strong_level', 3):
                    status = "STRONG"
                else:
                    status = "MODERATE"
                
                last_test = level.last_test.strftime('%Y-%m-%d') if level.last_test else 'N/A'
                
                print(f"{level.price:<12.4f} "
                      f"{distance:>6.4f} ({distance_pct:>5.2f}%) "
                      f"{level.strength:<10} "
                      f"{last_test:<15} "
                      f"{status}")
        else:
            print("No resistance levels detected")
        
        print(f"\n{'-'*70}")
        print("STATISTICS")
        print(f"{'-'*70}")
        
        if stats['nearest_support']:
            print(f"Nearest Support:    {stats['nearest_support']:.4f} "
                  f"(-{stats['support_distance']:.4f}, {stats['support_distance_pct']:.2f}%)")
        
        if stats['nearest_resistance']:
            print(f"Nearest Resistance: {stats['nearest_resistance']:.4f} "
                  f"(+{stats['resistance_distance']:.4f}, {stats['resistance_distance_pct']:.2f}%)")
        
        if stats['trading_range']:
            print(f"Trading Range:      {stats['trading_range']:.4f}")
            print(f"Position in Range:  {stats['position_in_range']*100:.1f}%")
        
        if stats['atr']:
            print(f"ATR (14):           {stats['atr']:.4f}")
        
        print(f"{'='*70}\n")
    
    def _get_nearest_level(self, levels: List[Level], price: float, direction: str) -> Level:
        """Get nearest level in specified direction"""
        if direction == 'below':
            candidates = [l for l in levels if l.price < price]
            return max(candidates, key=lambda x: x.price) if candidates else None
        else:  # above
            candidates = [l for l in levels if l.price > price]
            return min(candidates, key=lambda x: x.price) if candidates else None
