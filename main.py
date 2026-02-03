import os
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import random

app = FastAPI(title="GISP NEXUS OS | Global Intelligence")

# --- QUANT & WHALE ENGINE ---
class NexusCore:
    def __init__(self):
        self.exchange = ccxt.binance()

    def get_intelligence(self, symbol="BTC/USDT"):
        try:
            # 1. Real-time Market Data Ingestion
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            
            # 2. Institutional Indicators (Volatility & Trend)
            df['rsi'] = ta.rsi(df['c'], length=14)
            df['atr'] = ta.atr(df['h'], df['l'], df['c'], length=14)
            
            # 3. Liquidity Analysis (Simulated Whale Impact)
            order_book = self.exchange.fetch_order_book(symbol)
            bids = np.array(order_book['bids'])
            asks = np.array(order_book['asks'])
            
            bid_volume = np.sum(bids[:, 1])
            ask_volume = np.sum(asks[:, 1])
            imbalance = bid_volume / ask_volume
            
            # 4. Precision Signal Logic
            last_price = df['c'].iloc[-1]
            signal = "NEUTRAL"
            if df['rsi'].iloc[-1] < 30 and imbalance > 1.5:
                signal = "INSTITUTIONAL ACCUMULATION (STRONG BUY)"
            elif df['rsi'].iloc[-1] > 70 and imbalance < 0.7:
                signal = "LIQUIDITY DISTRIBUTION (STRONG SELL)"

            return {
                "symbol": symbol,
                "price": last_price,
                "signal": signal,
                "imbalance": round(imbalance, 2),
                "whale_activity": "High" if imbalance > 2.0 or imbalance < 0.5 else "Stable",
                "tp": round(last_price + (df['atr'].iloc[-1] * 2), 2),
                "sl": round(last_price - (df['atr'].iloc[-1] * 1.5), 2)
            }
        except Exception as e:
            return {"error": str(e)}

nexus = NexusCore()

# --- PROFESSIONAL NEXUS TERMINAL (FRONTEND) ---
@app.get("/", response_class=HTMLResponse)
async def terminal():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <title>GISP NEXUS | Intelligence OS</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body { background: #05070a; color: #00f2ff; font-family: 'JetBrains Mono', monospace; }
            .glass { background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.1); backdrop-filter: blur(10px); }
            .neon-border { border: 1px solid #00f2ff; box-shadow: 0 0 10px rgba(0, 242, 255, 0.2); }
        </style>
    </head>
    <body class="p-6">
        <header class="flex justify-between items-center mb-10 border-b border-cyan-900 pb-4">
            <h1 class="text-3xl font-bold tracking-tighter">GISP <span class="text-white">NEXUS v1.0</span></h1>
            <div class="text-right text-xs">
                <p>SERVER STATUS: <span class="text-green-500 underline">ONLINE</span></p>
                <p id="clock">UTC: --:--:--</p>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="glass p-6 rounded-xl neon-border">
                <h2 class="text-gray-500 text-sm mb-4 uppercase">Liquidity Imbalance</h2>
                <div id="imbalance" class="text-4xl font-bold">0.00</div>
                <p id="whale_status" class="text-xs mt-2 text-cyan-700 font-bold">MONITORING WHALES...</p>
            </div>

            <div class="glass p-6 rounded-xl md:col-span-2 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4 opacity-5 text-6xl italic">AI ENGINE</div>
                <h2 class="text-gray-500 text-sm mb-4 uppercase">Institutional Signal</h2>
                <div id="signal" class="text-2xl font-bold text-white">SCANNING MARKET...</div>
                <div class="mt-8 grid grid-cols-3 gap-4">
                    <div><p class="text-[10px] text-gray-500">ENTRY</p><p id="entry" class="text-lg">0.00</p></div>
                    <div><p class="text-[10px] text-gray-500 text-green-500">TARGET (TP)</p><p id="tp" class="text-lg text-green-400">0.00</p></div>
                    <div><p class="text-[10px] text-gray-500 text-red-500">PROTECTION (SL)</p><p id="sl" class="text-lg text-red-400">0.00</p></div>
                </div>
            </div>
        </div>

        <script>
            async function updateNexus() {
                try {
                    const res = await fetch('/api/v1/data');
                    const data = await res.json();
                    document.getElementById('signal').innerText = data.signal;
                    document.getElementById('imbalance').innerText = data.imbalance;
                    document.getElementById('entry').innerText = '$' + data.price.toLocaleString();
                    document.getElementById('tp').innerText = '$' + data.tp.toLocaleString();
                    document.getElementById('sl').innerText = '$' + data.sl.toLocaleString();
                    document.getElementById('whale_status').innerText = 'WHALE ACTIVITY: ' + data.whale_activity;
                } catch(e) { console.log("Nexus Sync Error"); }
            }
            setInterval(updateNexus, 5000);
            setInterval(() => { document.getElementById('clock').innerText = 'UTC: ' + new Date().toUTCString().split(' ')[4]; }, 1000);
            updateNexus();
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/data")
def get_data():
    return nexus.get_intelligence("BTC/USDT")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
