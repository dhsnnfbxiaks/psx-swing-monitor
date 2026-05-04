import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from groq import Groq

# --- CONFIGURATION ---
client = Groq(api_key="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")

st.set_page_config(page_title="PSX Swing Trader", layout="wide")
st.title("🛡️ PSX Swing Trade Monitor")

# --- TICKER LIST ---
stocks = {
    "ENGRO.KA": "Engro Corporation", "MEBL.KA": "Meezan Bank", 
    "HUBC.KA": "Hubco", "FFC.KA": "Fauji Fertilizer",
    "OGDC.KA": "OGDC", "PPL.KA": "Pakistan Petroleum",
    "MCB.KA": "MCB Bank", "UBL.KA": "UBL",
    "LUCK.KA": "Lucky Cement", "EPCL.KA": "Engro Polymer",
    "KEL.KA": "K-Electric", "TRG.KA": "TRG Pakistan",
    "BAFL.KA": "Bank Alfalah", "SYS.KA": "Systems Ltd",
    "DCR.KA": "Dewan Cement", "HMB.KA": "Habib Metropolitan Bank",
    "UNITY.KA": "Unity Foods", "WTL.KA": "Worldcall Telecom",
    "CNERGY.KA": "Cnergyico"
}

selected_key = st.sidebar.selectbox("Select Stock:", options=list(stocks.keys()), format_func=lambda x: f"{x} - {stocks[x]}")

# --- APP LOGIC ---
try:
    # Fetch Data
    stock = yf.Ticker(selected_key)
    # We fetch a slightly longer period to ensure we have the "previous" day's data
    data = stock.history(period="1mo")

    if data.empty or len(data) < 2:
        st.error(f"Insufficient data for {selected_key} on Yahoo Finance.")
    else:
        # Calculate Current and Previous Close
        current_price = data['Close'].iloc[-1]
        previous_close = data['Close'].iloc[-2]
        price_diff = current_price - previous_close
        
        # Display Metric with Delta (Up/Down)
        st.metric(
            label=f"Price ({selected_key})", 
            value=f"PKR {current_price:.2f}", 
            delta=f"{price_diff:.2f}"
        )

        # Display Chart
        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
        fig.update_layout(template="plotly_dark", title="3-Month Price Movement", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # AI Analysis
        if st.button("🚀 Analyze with AI"):
            with st.spinner("Analyzing with Groq..."):
                try:
                    summary = data.tail(10).to_string()
                    prompt = f"""
                    Analyze {selected_key} at price {current_price:.2f}.
                    Market Data: {summary}
                    
                    Provide a concise answer:
                    1. SIGNAL: [BUY / SELL / HOLD]
                    2. REASONING: [Explain technical trend + political/economic context]
                    3. ENTRY PRICE (BUY): [Provide price range]
                    4. EXIT PRICE (TARGET): [Provide target price]
                    5. STOP LOSS: [Recommended exit]
                    """
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                    )
                    st.markdown("### 📊 Market & Sentiment Analysis")
                    st.write(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Groq API Error: {e}")
        else:
            st.info("Click the button above to run the AI analysis.")

except Exception as e:
    st.error(f"Application Error: {e}")