"""
Support and Resistance Level Detection
Implements algorithms to identify horizontal support and resistance levels
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy.signal import argrelextrema
from collections import defaultdict


class Level:
    """Represents a support or resistance level"""
    
    def __init__(self, price: float, level_type: str, strength: int = 1):
        """
        Initialize a price level
        
        Args:
            price: Price level
            level_type: 'support' or 'resistance'
            strength: Number of touches/tests of this level
        """
        self.price = price
        self.type = level_type
        self.strength = strength
        self.touches = []
        self.last_test = None
        
    def add_touch(self, date, touch_price: float):
        """Add a touch/test of this level"""
        self.touches.append({'date': date, 'price': touch_price})
        self.strength = len(self.touches)
        self.last_test = date
        
    def __repr__(self):
        return f"Level({self.type}, price={self.price:.4f}, strength={self.strength})"


class LevelDetector:
    """Detects support and resistance levels in price data"""
    
    def __init__(self, config: Dict):
        """
        Initialize level detector
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.detection_config = config.get('detection', {})
        self.price_tolerance = self.detection_config.get('price_tolerance', 0.005)
        self.min_touches = self.detection_config.get('min_touches', 2)
        self.pivot_left = self.detection_config.get('pivot', {}).get('left_bars', 5)
        self.pivot_right = self.detection_config.get('pivot', {}).get('right_bars', 5)
        
    def find_support_resistance(self, df: pd.DataFrame) -> Tuple[List[Level], List[Level]]:
        """
        Find support and resistance levels
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        # Method 1: Pivot points
        pivot_supports, pivot_resistances = self._find_pivot_levels(df)
        
        # Method 2: Price clustering
        cluster_supports, cluster_resistances = self._find_clustered_levels(df)
        
        # Method 3: High volume areas
        volume_levels = self._find_volume_levels(df)
        
        # Combine and consolidate levels
        all_supports = pivot_supports + cluster_supports + volume_levels['support']
        all_resistances = pivot_resistances + cluster_resistances + volume_levels['resistance']
        
        # Consolidate nearby levels
        consolidated_supports = self._consolidate_levels(all_supports, 'support')
        consolidated_resistances = self._consolidate_levels(all_resistances, 'resistance')
        
        # Validate levels (minimum touches)
        valid_supports = [l for l in consolidated_supports if l.strength >= self.min_touches]
        valid_resistances = [l for l in consolidated_resistances if l.strength >= self.min_touches]
        
        # Sort by strength
        valid_supports.sort(key=lambda x: x.strength, reverse=True)
        valid_resistances.sort(key=lambda x: x.strength, reverse=True)
        
        return valid_supports, valid_resistances
    
    def _find_pivot_levels(self, df: pd.DataFrame) -> Tuple[List[Level], List[Level]]:
        """
        Find support and resistance using pivot points (local extrema)
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        supports = []
        resistances = []
        
        # Find local minima (support)
        local_min_indices = argrelextrema(
            df['Low'].values, 
            np.less_equal,
            order=self.pivot_left
        )[0]
        
        for idx in local_min_indices:
            if idx < len(df):
                price = df['Low'].iloc[idx]
                date = df.index[idx]
                level = Level(price, 'support')
                level.add_touch(date, price)
                supports.append(level)
        
        # Find local maxima (resistance)
        local_max_indices = argrelextrema(
            df['High'].values,
            np.greater_equal,
            order=self.pivot_left
        )[0]
        
        for idx in local_max_indices:
            if idx < len(df):
                price = df['High'].iloc[idx]
                date = df.index[idx]
                level = Level(price, 'resistance')
                level.add_touch(date, price)
                resistances.append(level)
        
        return supports, resistances
    
    def _find_clustered_levels(self, df: pd.DataFrame) -> Tuple[List[Level], List[Level]]:
        """
        Find levels where price repeatedly tests a zone
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        supports = []
        resistances = []
        
        # Create price bins
        price_range = df['High'].max() - df['Low'].min()
        bin_size = max(self.price_tolerance, price_range / 100)
        
        # Count touches in support zone (near lows)
        low_bins = defaultdict(list)
        for idx, row in df.iterrows():
            bin_key = round(row['Low'] / bin_size) * bin_size
            low_bins[bin_key].append((idx, row['Low']))
        
        # Count touches in resistance zone (near highs)
        high_bins = defaultdict(list)
        for idx, row in df.iterrows():
            bin_key = round(row['High'] / bin_size) * bin_size
            high_bins[bin_key].append((idx, row['High']))
        
        # Create support levels from clustered lows
        for price, touches in low_bins.items():
            if len(touches) >= 2:
                level = Level(price, 'support')
                for date, touch_price in touches:
                    level.add_touch(date, touch_price)
                supports.append(level)
        
        # Create resistance levels from clustered highs
        for price, touches in high_bins.items():
            if len(touches) >= 2:
                level = Level(price, 'resistance')
                for date, touch_price in touches:
                    level.add_touch(date, touch_price)
                resistances.append(level)
        
        return supports, resistances
    
    def _find_volume_levels(self, df: pd.DataFrame) -> Dict[str, List[Level]]:
        """
        Find levels using volume profile
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Dictionary with 'support' and 'resistance' level lists
        """
        volume_config = self.detection_config.get('volume_profile', {})
        if not volume_config.get('enabled', True):
            return {'support': [], 'resistance': []}
        
        bins = volume_config.get('bins', 50)
        
        # Create volume profile
        price_min = df['Low'].min()
        price_max = df['High'].max()
        price_range = price_max - price_min
        bin_size = price_range / bins
        
        volume_profile = defaultdict(float)
        
        for idx, row in df.iterrows():
            # Distribute volume across the day's range
            price_range_day = row['High'] - row['Low']
            if price_range_day > 0:
                num_bins_touched = int(price_range_day / bin_size) + 1
                volume_per_bin = row['Volume'] / num_bins_touched
                
                current_price = row['Low']
                while current_price <= row['High']:
                    bin_key = round(current_price / bin_size) * bin_size
                    volume_profile[bin_key] += volume_per_bin
                    current_price += bin_size
        
        # Find high volume nodes (HVN) - potential support/resistance
        sorted_levels = sorted(volume_profile.items(), key=lambda x: x[1], reverse=True)
        top_volume_levels = sorted_levels[:min(10, len(sorted_levels))]
        
        current_price = df['Close'].iloc[-1]
        
        supports = []
        resistances = []
        
        for price, volume in top_volume_levels:
            if price < current_price:
                level = Level(price, 'support', strength=2)
                supports.append(level)
            else:
                level = Level(price, 'resistance', strength=2)
                resistances.append(level)
        
        return {'support': supports, 'resistance': resistances}
    
    def _consolidate_levels(self, levels: List[Level], level_type: str) -> List[Level]:
        """
        Consolidate nearby levels into single levels
        
        Args:
            levels: List of Level objects
            level_type: 'support' or 'resistance'
            
        Returns:
            Consolidated list of levels
        """
        if not levels:
            return []
        
        # Sort by price
        sorted_levels = sorted(levels, key=lambda x: x.price)
        
        consolidated = []
        current_group = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            # Check if this level is close to the current group
            group_avg = np.mean([l.price for l in current_group])
            
            if abs(level.price - group_avg) <= self.price_tolerance:
                # Add to current group
                current_group.append(level)
            else:
                # Consolidate current group and start new group
                consolidated.append(self._merge_levels(current_group, level_type))
                current_group = [level]
        
        # Don't forget the last group
        if current_group:
            consolidated.append(self._merge_levels(current_group, level_type))
        
        return consolidated
    
    def _merge_levels(self, levels: List[Level], level_type: str) -> Level:
        """
        Merge multiple levels into a single level
        
        Args:
            levels: List of levels to merge
            level_type: 'support' or 'resistance'
            
        Returns:
            Merged level
        """
        # Use weighted average based on strength
        total_weight = sum(l.strength for l in levels)
        avg_price = sum(l.price * l.strength for l in levels) / total_weight
        
        # Create merged level
        merged = Level(avg_price, level_type)
        
        # Combine all touches
        for level in levels:
            for touch in level.touches:
                merged.add_touch(touch['date'], touch['price'])
        
        return merged
    
    def get_nearest_levels(self, levels: List[Level], current_price: float, 
                          count: int = 3) -> List[Level]:
        """
        Get the nearest levels to current price
        
        Args:
            levels: List of levels
            current_price: Current price
            count: Number of nearest levels to return
            
        Returns:
            List of nearest levels
        """
        if not levels:
            return []
        
        # Calculate distance from current price
        levels_with_distance = [
            (level, abs(level.price - current_price))
            for level in levels
        ]
        
        # Sort by distance
        levels_with_distance.sort(key=lambda x: x[1])
        
        # Return nearest levels
        return [level for level, _ in levels_with_distance[:count]]
    
    def calculate_level_strength_score(self, level: Level, df: pd.DataFrame) -> float:
        """
        Calculate a strength score for a level (0-1)
        
        Args:
            level: Level object
            df: DataFrame with price data
            
        Returns:
            Strength score between 0 and 1
        """
        score = 0.0
        
        # Factor 1: Number of touches (normalized)
        touch_score = min(level.strength / 5.0, 1.0) * 0.4
        score += touch_score
        
        # Factor 2: Recency of tests
        if level.last_test:
            days_ago = (df.index[-1] - level.last_test).days
            recency_score = max(0, 1 - days_ago / 90) * 0.3
            score += recency_score
        
        # Factor 3: Clear bounces (price respected the level)
        bounce_score = 0.3  # Simplified for now
        score += bounce_score
        
        return min(score, 1.0)
