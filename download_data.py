#!/usr/bin/env python3
"""
Download real SOFR futures data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

ticker_mapping = config['data_source']['ticker_mapping']

# Download as much history as available
print("Downloading real SOFR futures data from Yahoo Finance...")
print("=" * 70)

for contract, base_ticker in ticker_mapping.items():
    print(f"\nDownloading {contract} ({base_ticker})...")
    
    # Try multiple ticker formats
    ticker_variants = [
        base_ticker,
        base_ticker.replace('.CBT', ''),  # Without exchange
        f"SR{contract[3:5]}{contract[:3]}.CBT",  # Alternative format
        f"ZQ{contract[3:5]}{contract[:3]}=F",  # Futures format
    ]
    
    data = None
    successful_ticker = None
    
    for ticker in ticker_variants:
        try:
            # Try to get maximum available history (2 years)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 2 years
            
            print(f"  Trying {ticker}...", end=" ")
            
            # Download data
            temp_data = yf.download(
                ticker, 
                start=start_date, 
                end=end_date,
                progress=False,
                auto_adjust=False
            )
            
            if not temp_data.empty:
                data = temp_data
                successful_ticker = ticker
                print("✓")
                break
            else:
                print("no data")
        except:
            print("failed")
            continue
    
    if data is not None:
        # Prepare data
        df = data.copy()
        df = df.reset_index()
        
        # Rename columns
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        
        # Keep only needed columns
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Format date
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Round to tick size (0.005)
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].round(4)
        
        # Save to CSV
        filename = f'data/{contract}.csv'
        df.to_csv(filename, index=False)
        
        print(f"  ✓ Downloaded successfully!")
        print(f"    Ticker used: {successful_ticker}")
        print(f"    Period: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"    Days: {len(df)}")
        print(f"    Price range: {df['Low'].min():.4f} - {df['High'].max():.4f}")
        print(f"    Avg volume: {df['Volume'].mean():,.0f}")
        print(f"    Saved to: {filename}")
        
    else:
        print(f"  ❌ No data available for {contract} (tried {len(ticker_variants)} ticker formats)")

print("\n" + "=" * 70)
print("Download complete!")
