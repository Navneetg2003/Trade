"""
Data Handler for SOFR Futures
Handles data fetching, processing, and formatting for SOFR futures contracts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import os


class SOFRDataHandler:
    """Handles SOFR futures data fetching and processing"""
    
    def __init__(self, config: Dict):
        """
        Initialize data handler
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_source = config.get('data_source', {})
        self.provider = self.data_source.get('provider', 'csv')
        self.ticker_mapping = self.data_source.get('ticker_mapping', {})
        
    def get_contract_data(self, contract: str, lookback_days: int = 90) -> pd.DataFrame:
        """
        Fetch historical data for a SOFR futures contract
        
        Args:
            contract: Contract name (e.g., 'MAR26', 'JUN26')
            lookback_days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        if self.provider == 'yahoo':
            return self._fetch_yahoo_data(contract, lookback_days)
        elif self.provider == 'csv':
            return self._load_csv_data(contract)
        else:
            raise ValueError(f"Unsupported data provider: {self.provider}")
    
    def _fetch_yahoo_data(self, contract: str, lookback_days: int) -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance
        
        Args:
            contract: Contract name
            lookback_days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        ticker = self.ticker_mapping.get(contract)
        
        if not ticker:
            print(f"Warning: No ticker mapping for {contract}, using sample data")
            return self._generate_sample_data(contract, lookback_days)
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Fetch data from Yahoo Finance
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                print(f"No data returned for {contract}, generating sample data")
                return self._generate_sample_data(contract, lookback_days)
            
            # Standardize column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            data['Contract'] = contract
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {contract}: {e}")
            print("Generating sample data instead")
            return self._generate_sample_data(contract, lookback_days)
    
    def _load_csv_data(self, contract: str) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            contract: Contract name
            
        Returns:
            DataFrame with OHLCV data
        """
        csv_path = self.data_source.get('csv_path', 'data/')
        file_path = os.path.join(csv_path, f"{contract}.csv")
        
        if not os.path.exists(file_path):
            print(f"CSV file not found for {contract}, generating sample data")
            return self._generate_sample_data(contract, 90)
        
        try:
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            data['Contract'] = contract
            return data
        except Exception as e:
            print(f"Error loading CSV for {contract}: {e}")
            return self._generate_sample_data(contract, 90)
    
    def _generate_sample_data(self, contract: str, days: int = 90) -> pd.DataFrame:
        """
        Generate sample SOFR futures data for testing
        
        Args:
            contract: Contract name
            days: Number of days of data
            
        Returns:
            DataFrame with sample OHLCV data
        """
        # SOFR futures trade around 95.00-96.00 (representing 4-5% rate)
        base_price = 95.50
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate realistic price movement
        np.random.seed(hash(contract) % 2**32)  # Deterministic per contract
        
        returns = np.random.normal(0, 0.02, days)  # Small daily changes
        close_prices = base_price + np.cumsum(returns)
        
        # Add some trending behavior
        trend = np.linspace(0, 0.3, days)
        close_prices += trend
        
        # Generate OHLC from close
        data = []
        for i, date in enumerate(dates):
            close = close_prices[i]
            daily_range = abs(np.random.normal(0, 0.015))
            
            high = close + daily_range * np.random.uniform(0.5, 1.0)
            low = close - daily_range * np.random.uniform(0.5, 1.0)
            open_price = low + (high - low) * np.random.uniform(0.3, 0.7)
            
            volume = int(np.random.uniform(50000, 200000))
            
            data.append({
                'Date': date,
                'Open': round(open_price, 4),
                'High': round(high, 4),
                'Low': round(low, 4),
                'Close': round(close, 4),
                'Volume': volume,
                'Contract': contract
            })
        
        df = pd.DataFrame(data)
        df.set_index('Date', inplace=True)
        
        return df
    
    def convert_to_rate(self, price: float) -> float:
        """
        Convert SOFR futures price to implied rate
        
        Args:
            price: Futures price (100 - rate format)
            
        Returns:
            Implied SOFR rate
        """
        return 100 - price
    
    def convert_to_price(self, rate: float) -> float:
        """
        Convert SOFR rate to futures price
        
        Args:
            rate: SOFR rate
            
        Returns:
            Futures price (100 - rate format)
        """
        return 100 - rate
    
    def calculate_tick_value(self, price_change: float) -> float:
        """
        Calculate dollar value of price change
        
        Args:
            price_change: Change in futures price
            
        Returns:
            Dollar value of the change
        """
        tick_size = self.config['contract_specs']['tick_size']
        tick_value = self.config['contract_specs']['tick_value']
        
        ticks = price_change / tick_size
        return ticks * tick_value
    
    def get_multiple_contracts(self, contracts: List[str], 
                              lookback_days: int = 90) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple contracts
        
        Args:
            contracts: List of contract names
            lookback_days: Number of days of historical data
            
        Returns:
            Dictionary mapping contract names to DataFrames
        """
        data_dict = {}
        
        for contract in contracts:
            print(f"Fetching data for {contract}...")
            data_dict[contract] = self.get_contract_data(contract, lookback_days)
        
        return data_dict
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        df = df.copy()
        
        # Simple moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Volume moving average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Average True Range (ATR)
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()
        
        return df
