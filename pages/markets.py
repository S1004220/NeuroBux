import streamlit as st
import plotly.graph_objects as go
import requests
import pandas as pd
import time
from datetime import datetime

def markets_page():
    st.header("📈 Markets")
    
    # Investment platform links WITHOUT logos - simple URL structure
    INVESTMENT_PLATFORMS = {
        "🇮🇳 India": {
            "Zerodha": "https://zerodha.com/",
            "Groww": "https://groww.in/",
            "Angel One": "https://www.angelone.in/",
            "Upstox": "https://upstox.com/",
            "INDmoney": "https://www.indmoney.com/"
        },
        "🇺🇸 US": {
            "Robinhood": "https://www.robinhood.com/",
            "Public": "https://public.com/",
            "M1 Finance": "https://www.m1.com/",
            "Fidelity": "https://www.fidelity.com/",
            "Charles Schwab": "https://www.schwab.com/"
        },
        "🇪🇺 EU": {
            "eToro": "https://www.etoro.com/",
            "Trading 212": "https://www.trading212.com/",
            "Degiro": "https://www.degiro.com/",
            "Interactive Brokers": "https://www.interactivebrokers.com/",
            "Saxo Bank": "https://www.home.saxo/"
        },
        "🇯🇵 Japan": {
            "SBI Securities": "https://www.sbisec.co.jp/",
            "Rakuten Securities": "https://www.rakuten-sec.co.jp/",
            "Monex": "https://www.monex.co.jp/",
            "Matsui Securities": "https://www.matsui.co.jp/",
            "Interactive Brokers": "https://www.interactivebrokers.com/"
        },
        "Crypto": {
            "Coinbase": "https://www.coinbase.com/",
            "Binance": "https://www.binance.com/",
            "WazirX": "https://wazirx.com/",
            "CoinDCX": "https://coindcx.com/",
            "Kraken": "https://www.kraken.com/"
        },
        "Commodities": {
            "TD Ameritrade": "https://www.tdameritrade.com/",
            "E*TRADE": "https://www.etrade.com/",
            "Interactive Brokers": "https://www.interactivebrokers.com/",
            "Charles Schwab": "https://www.schwab.com/",
            "Fidelity": "https://www.fidelity.com/"
        }
    }
    
    # Alpha Vantage API functions
    def get_stock_data_alpha_vantage(symbol):
        """Get stock data using Alpha Vantage API"""
        api_key = st.secrets.get("alpha_vantage_api_key")
        
        if not api_key:
            return None, "API key not configured"
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key,
                "outputsize": "compact"
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index')
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df.index = pd.to_datetime(df.index)
                df = df.astype(float)
                df = df.sort_index()
                return df.tail(30), None
            elif "Error Message" in data:
                return None, data["Error Message"]
            elif "Note" in data:
                return None, "API rate limit reached. Please wait a minute."
            else:
                return None, "Unknown error occurred"
                
        except Exception as e:
            return None, str(e)
    
    def get_crypto_data_alpha_vantage(symbol):
        """Get crypto data using Alpha Vantage"""
        api_key = st.secrets.get("alpha_vantage_api_key")
        
        if not api_key:
            return None, "API key not configured"
        
        try:
            crypto_symbol = symbol.replace("-USD", "")
            
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": crypto_symbol,
                "market": "USD",
                "apikey": api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if "Time Series (Digital Currency Daily)" in data:
                time_series = data["Time Series (Digital Currency Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient='index')
                
                df['Close'] = df['4a. close (USD)'].astype(float)
                df['Open'] = df['1a. open (USD)'].astype(float)
                df['High'] = df['2a. high (USD)'].astype(float)
                df['Low'] = df['3a. low (USD)'].astype(float)
                df['Volume'] = df['5. volume'].astype(float)
                
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(30), None
            elif "Error Message" in data:
                return None, data["Error Message"]
            else:
                return None, "Crypto data not available"
                
        except Exception as e:
            return None, str(e)
    
    # Test Alpha Vantage connection
    def test_alpha_vantage_connection():
        """Test Alpha Vantage API connection"""
        try:
            with st.spinner("Testing Alpha Vantage connection..."):
                df, error = get_stock_data_alpha_vantage("AAPL")
                
                if df is not None:
                    return True, "✅ Alpha Vantage connected successfully"
                else:
                    return False, f"❌ Alpha Vantage error: {error}"
                    
        except Exception as e:
            return False, f"❌ Connection failed: {str(e)}"
    
    # Test connection
    with st.spinner("Connecting to Alpha Vantage..."):
        connected, status_msg = test_alpha_vantage_connection()
        
        if connected:
            st.success(status_msg)
        else:
            st.error(status_msg)
            
            if "API key not configured" in status_msg:
                st.error("**Alpha Vantage API Key Missing**")
                st.code('alpha_vantage_api_key = "YOUR_API_KEY_HERE"')
            
            # Show investment platforms even when data fails
            st.markdown("---")
            st.subheader("💰 Investment Platforms (Always Available)")
            
            region = st.selectbox("Choose investment region", list(INVESTMENT_PLATFORMS.keys()))
            platforms = INVESTMENT_PLATFORMS[region]
            
            cols = st.columns(len(platforms))
            for idx, (platform_name, platform_url) in enumerate(platforms.items()):
                with cols[idx]:
                    if st.button(f"📱 {platform_name}", key=f"offline_{platform_name}"):
                        st.success(f"🚀 Opening {platform_name}...")
                        st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            return

    # Markets universe - ALL REGIONS RESTORED
    universe = {
        "🇮🇳 India": ["RELIANCE.BSE", "TCS.BSE", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL"],
        "🇺🇸 US": ["AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "NVDA", "META"],
        "🇪🇺 EU": ["ASML.AS", "SAP.DE", "NESN.SW", "MC.PA", "RDSA.AS"],
        "🇯🇵 Japan": ["7203.T", "6758.T", "9984.T", "6861.T", "8306.T"],
        "Crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "SOL-USD"],
        "Commodities": ["GC=F", "SI=F", "CL=F", "NG=F", "HG=F"],
        "Popular ETFs": ["SPY", "QQQ", "VTI", "VOO", "IWM"]
    }
    
    region = st.selectbox("Pick region / asset class", list(universe.keys()))
    symbols = universe[region]
    
    # Investment platforms section WITHOUT logos
    st.markdown("---")
    st.subheader(f"💰 Start Investing in {region}")
    
    # Map regions to appropriate platforms
    platform_key = region
    if region == "🇪🇺 EU":
        platform_key = "🇪🇺 EU"
    elif region == "🇯🇵 Japan":
        platform_key = "🇯🇵 Japan"
    elif region == "Commodities":
        platform_key = "Commodities"
    elif region == "Popular ETFs":
        platform_key = "🇺🇸 US"  # ETFs use US platforms
    elif "Crypto" in region:
        platform_key = "Crypto"
    else:
        platform_key = region
    
    platforms = INVESTMENT_PLATFORMS.get(platform_key, INVESTMENT_PLATFORMS["🇺🇸 US"])
    
    cols = st.columns(len(platforms))
    for idx, (platform_name, platform_url) in enumerate(platforms.items()):
        with cols[idx]:
            if st.button(f"📱 {platform_name}", key=f"invest_{platform_name}"):
                st.success(f"🚀 Opening {platform_name}...")
                st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
    
    # Create tabs for symbols
    symbol_names = []
    for s in symbols:
        name = s.replace("-USD", "").replace("^", "").replace(".BSE", "").replace(".AS", "").replace(".DE", "").replace(".SW", "").replace(".PA", "").replace(".T", "").replace("=F", "")
        symbol_names.append(name)
    
    tabs = st.tabs(symbol_names)

    for tab, sym in zip(tabs, symbols):
        with tab:
            st.subheader(f"📊 {sym}")
            
            # Fetch data with Alpha Vantage
            with st.spinner(f"Loading {sym} data from Alpha Vantage..."):
                if "-USD" in sym:  # Crypto
                    df, error = get_crypto_data_alpha_vantage(sym)
                else:  # All other stocks
                    df, error = get_stock_data_alpha_vantage(sym)
                
                time.sleep(1)
            
            if df is not None and not df.empty:
                # Create enhanced chart
                fig = go.Figure()
                
                # Add candlestick chart
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=sym,
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ))
                
                fig.update_layout(
                    title=f"{sym} - 30-Day Chart",
                    template="plotly_dark",
                    height=450,
                    xaxis_title="Date",
                    yaxis_title="Price",
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)

                # Display comprehensive metrics
                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                change = (latest.Close - previous.Close) / previous.Close * 100
                
                col1, col2, col3, col4 = st.columns(4)
                
                # Currency based on region
                if region == "🇮🇳 India":
                    currency = "₹"
                elif region == "🇪🇺 EU":
                    currency = "€"
                elif region == "🇯🇵 Japan":
                    currency = "¥"
                else:
                    currency = "$"
                
                col1.metric("Current Price", f"{currency}{latest.Close:.2f}")
                col2.metric("Daily Change", f"{change:+.2f}%")
                col3.metric("Day High", f"{currency}{latest.High:.2f}")
                col4.metric("Day Low", f"{currency}{latest.Low:.2f}")
                
                # Investment buttons WITHOUT logos
                st.markdown("---")
                st.subheader(f"💳 Ready to Invest in {sym}?")
                
                invest_cols = st.columns(3)
                top_platforms = list(platforms.items())[:3]
                
                for idx, (platform_name, platform_url) in enumerate(top_platforms):
                    with invest_cols[idx]:
                        clean_symbol = sym.replace('.BSE', '').replace('.AS', '').replace('.DE', '').replace('.SW', '').replace('.PA', '').replace('.T', '').replace('=F', '')
                        if st.button(f"🛒 Buy {clean_symbol}", key=f"buy_{sym}_{platform_name}", type="primary"):
                            st.balloons()
                            st.success(f"🎯 Opening {platform_name} to invest in {sym}")
                            st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)
            
            else:
                st.error(f"❌ Unable to load data for {sym}")
                if error:
                    st.error(f"Error: {error}")
                    
                    if "rate limit" in error.lower():
                        st.warning("⏳ Alpha Vantage rate limit reached. Please wait a moment.")
                    elif "not available" in error.lower():
                        st.info("💡 Limited data availability for this symbol on Alpha Vantage. Investment platforms are still accessible below.")
                
                # Show investment options even without data
                st.markdown("---")
                st.subheader(f"💰 Invest in {sym} via Platforms")
                
                invest_cols = st.columns(3)
                top_platforms = list(platforms.items())[:3]
                
                for idx, (platform_name, platform_url) in enumerate(top_platforms):
                    with invest_cols[idx]:
                        if st.button(f"📱 {platform_name}", key=f"fallback_{sym}_{platform_name}"):
                            st.success(f"🚀 Opening {platform_name}...")
                            st.markdown(f'<a href="{platform_url}" target="_blank">🔗 Open {platform_name}</a>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.caption("💡 Professional financial data with Alpha Vantage")
