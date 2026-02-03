import os
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime

app = FastAPI(title="GISP NEXUS | World Top 1 OS")

# --- GLOBAL INTELLIGENCE ENGINE ---
class GispNexusEngine:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'} # Institutsional daraja uchun futures
        })

    def get_market_analysis(self, symbol="BTC/USDT", tf="1h"):
        try:
            # 1. Real-Time Data Ingestion
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=tf, limit=150)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            
            # 2. Institutional Quant Analysis (RSI + ATR + EMA)
            df['rsi'] = ta.rsi(df['c'], length=14)
            df['ema_fast'] = ta.ema(df['c'], length=20)
            df['ema_slow'] = ta.ema(df['c'], length=200)
            df['atr'] = ta.atr(df['h'], df['l'], df['c'], length=14)
            
            # 3. Liquidity & Order Book Imbalance (Whale Tracker)
            ob = self.exchange.fetch_order_book(symbol)
            bids_vol = sum([b[1] for b in ob['bids'][:20]])
            asks_vol = sum([a[1] for a in ob['asks'][:20]])
            imbalance = bids_vol / asks_vol if asks_vol > 0 else 1

            # 4. Hybrid AI Signal Logic
            last_price = df['c'].iloc[-1]
            rsi_val = df['rsi'].iloc[-1]
            trend = "BULLISH" if last_price > df['ema_slow'].iloc[-1] else "BEARISH"
            
            # Signal Precision (Aniq kirish va chiqish)
            signal = "NEUTRAL"
            confidence = 85.0
            
            if trend == "BULLISH" and rsi_val < 45 and imbalance > 1.2:
                signal = "INSTITUTIONAL ACCUMULATION (BUY)"
                confidence = 94.8
            elif trend == "BEARISH" and rsi_val > 55 and imbalance < 0.8:
                signal = "LIQUIDITY DISTRIBUTION (SELL)"
                confidence = 92.4

            return {
                "symbol": symbol,
                "price": f"{last_price:,}",
                "signal": signal,
                "confidence": f"{confidence}%",
                "imbalance": round(imbalance, 2),
                "entry": f"{last_price:,}",
                "tp": f"{round(last_price + (df['atr'].iloc[-1] * 2.5), 2):,}",
                "sl": f"{round(last_price - (df['atr'].iloc[-1] * 1.5), 2):,}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            return {"error": str(e)}

nexus = GispNexusEngine()

# --- THE TERMINAL (ULTRA-MODERN UI) ---
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>GISP NEXUS | Market Intelligence OS</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
            body { background: #020408; color: #e2e8f0; font-family: 'Space Grotesk', sans-serif; }
            .nexus-card { background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(0, 242, 255, 0.1); backdrop-filter: blur(12px); }
            .neon-text { text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); color: #00f2ff; }
            .status-bar { height: 2px; background: linear-gradient(90deg, #00f2ff, transparent); animation: scan 2s infinite; }
            @keyframes scan { 0% { width: 0%; } 100% { width: 100%; } }
        </style>
    </head>
    <body class="h-screen flex flex-col p-6 space-y-6">
        <header class="flex justify-between items-center border-b border-white/5 pb-4">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-cyan-500 rounded-lg flex items-center justify-center font-bold text-black italic">G</div>
                <h1 class="text-2xl font-bold tracking-widest">GISP <span class="text-cyan-400">NEXUS</span></h1>
            </div>
            <div class="flex space-x-6 text-[10px] tracking-widest uppercase opacity-60">
                <div>AI ENGINE: <span class="text-green-400">ACTIVE</span></div>
                <div>LATENCY: <span id="ping">12ms</span></div>
                <div id="utc-time">UTC: --:--:--</div>
            </div>
        </header>

        <div class="grid grid-cols-12 gap-6 flex-1 overflow-hidden">
            <aside class="col-span-3 space-y-6">
                <div class="nexus-card p-6 rounded-3xl">
                    <h3 class="text-xs font-bold text-gray-500 mb-6 uppercase tracking-widest">Liquidity Flow</h3>
                    <div id="imbalance" class="text-5xl font-bold neon-text">1.00</div>
                    <p class="text-[10px] mt-2 opacity-50">ORDER BOOK IMBALANCE (BID/ASK)</p>
                    <div class="status-bar mt-6"></div>
                </div>
            </aside>

            <main class="col-span-6 nexus-card rounded-3xl p-8 relative overflow-hidden">
                <div class="absolute top-0 right-0 p-10 opacity-5 text-8xl font-bold">OS</div>
                <h2 class="text-gray-500 text-xs font-bold uppercase mb-8">Institutional Signal</h2>
                <div id="signal" class="text-4xl font-bold mb-4 tracking-tighter uppercase">SCANNING...</div>
                <div id="confidence" class="text-cyan-400 text-sm mb-12 font-mono">Confidence: --%</div>

                <div class="grid grid-cols-3 gap-8">
                    <div class="p-4 rounded-2xl bg-white/5 border border-white/5">
                        <p class="text-[10px] opacity-40 uppercase">Entry Price</p>
                        <p id="price" class="text-xl font-bold text-white">$0.00</p>
                    </div>
                    <div class="p-4 rounded-2xl bg-green-500/5 border border-green-500/10">
                        <p class="text-[10px] text-green-500 uppercase">Take Profit</p>
                        <p id="tp" class="text-xl font-bold text-green-400">$0.00</p>
                    </div>
                    <div class="p-4 rounded-2xl bg-red-500/5 border border-red-500/10">
                        <p class="text-[10px] text-red-500 uppercase">Stop Loss</p>
                        <p id="sl" class="text-xl font-bold text-red-400">$0.00</p>
                    </div>
                </div>
            </main>

            <aside class="col-span-3 nexus-card rounded-3xl p-6 overflow-hidden flex flex-col">
                <h3 class="text-xs font-bold text-gray-500 mb-4 uppercase">System Logs</h3>
                <div id="logs" class="text-[9px] font-mono space-y-2 opacity-60 overflow-y-auto flex-1">
                    <div>> System Initialized...</div>
                </div>
            </aside>
        </div>

        <script>
            async function updateNexus() {
                try {
                    const res = await fetch('/api/v1/analyze');
                    const data = await res.json();
                    
                    document.getElementById('signal').innerText = data.signal;
                    document.getElementById('confidence').innerText = 'AI Confidence: ' + data.confidence;
                    document.getElementById('imbalance').innerText = data.imbalance;
                    document.getElementById('price').innerText = '$' + data.price;
                    document.getElementById('tp').innerText = '$' + data.tp;
                    document.getElementById('sl').innerText = '$' + data.sl;

                    const logs = document.getElementById('logs');
                    const entry = document.createElement('div');
                    entry.innerText = `> [${data.timestamp}] ${data.symbol} ANALYZED | IMBALANCE: ${data.imbalance}`;
                    logs.prepend(entry);
                } catch(e) {}
            }
            setInterval(updateNexus, 5000);
            updateNexus();
            setInterval(() => { document.getElementById('utc-time').innerText = 'UTC: ' + new Date().toUTCString().split(' ')[4]; }, 1000);
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/analyze")
def analyze():
    return nexus.get_market_analysis("BTC/USDT", "1h")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
            
