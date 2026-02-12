# Sample SOFR Futures Data

This directory contains sample CSV data files for SOFR futures contracts.

## File Format

Each CSV file should have the following columns:
- Date: Trading date (YYYY-MM-DD)
- Open: Opening price
- High: High price
- Low: Low price
- Close: Closing price
- Volume: Trading volume

## Example

```csv
Date,Open,High,Low,Close,Volume
2025-11-12,95.4750,95.5100,95.4500,95.4950,125000
2025-11-13,95.4950,95.5200,95.4700,95.5050,138000
...
```

## Contract Naming

Files should be named according to the contract:
- MAR26.csv - March 2026 contract
- JUN26.csv - June 2026 contract
- SEP26.csv - September 2026 contract
- DEC26.csv - December 2026 contract

## Data Sources

SOFR futures data can be obtained from:
- CME Group (primary exchange)
- Financial data providers (Bloomberg, Refinitiv)
- Yahoo Finance (limited availability)
- Interactive Brokers, TD Ameritrade APIs

## Note

If no CSV files are present, the application will generate sample data for testing purposes.
