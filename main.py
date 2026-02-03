import os
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime

app = FastAPI(title="GISP NEXUS OS")

# --- CORE INTELLIGENCE ENGINE ---
class GispNexus:
    def __init__(self):
        # Read-only ulanish (API key shart emas)
        self.exchange = ccxt.binance({'enableRateLimit': True})

    def get_market_data(self, symbol="BTC/USDT"):
        try:
            # 1. Narxlarni olish (OHLCV)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            
            # 2. Indikatorlar (RSI va Trend)
            df['rsi'] = ta.rsi(df['c'], length=14)
            df['ema200'] = ta.ema(df['c'], length=200)
            df['atr'] = ta.atr(df['h'], df['l'], df['c'], length=14)
            
            # 3. Order Book (Likvidlik tahlili)
            ob = self.exchange.fetch_order_book(symbol)
            bids_vol = sum([b[1] for b in ob['bids'][:10]])
            asks_vol = sum([a[1] for a in ob['asks'][:10]])
            imbalance = bids_vol / asks_vol if asks_vol > 0 else 1

            # 4. Signal Mantiqi
            last_price = df['c'].iloc[-1]
            rsi_now = df['rsi'].iloc[-1]
            trend = "BULLISH" if last_price > df['ema200'].iloc[-1] else "BEARISH"
            
            signal = "NEUTRAL"
            if trend == "BULLISH" and rsi_now < 40 and imbalance > 1.2:
                signal = "STRONG BUY (ACCUMULATION)"
            elif trend == "BEARISH" and rsi_now > 60 and imbalance < 0.8:
                signal = "STRONG SELL (DISTRIBUTION)"

            return {
                "symbol": symbol,
                "price": f"{last_price:,}",
                "signal": signal,
                "imbalance": round(imbalance, 2),
                "entry": f"{last_price:,}",
                "tp": f"{round(last_price + (df['atr'].iloc[-1] * 2), 2):,}",
                "sl": f"{round(last_price - (df['atr'].iloc[-1] * 1.5), 2):,}",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            return {"error": str(e)}

engine = GispNexus()

# --- PROFESSIONAL TERMINAL UI ---
@app.get("/", response_class=HTMLResponse)
async def terminal():
    return """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <title>GISP NEXUS | Intelligence Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
            body { background: #010204; color: #00f2ff; font-family: 'JetBrains Mono', monospace; }
            .nexus-border { border: 1px solid rgba(0, 242, 255, 0.2); box-shadow: 0 0 15px rgba(0, 242, 255, 0.05); }
            .glow-text { text-shadow: 0 0 10px rgba(0, 242, 255, 0.6); }
        </style>
    </head>
    <body class="p-4 md:p-10">
        <div class="max-w-6xl mx-auto space-y-6">
            <header class="flex justify-between items-center border-b border-cyan-900 pb-6">
                <div>
                    <h1 class="text-3xl font-bold tracking-widest glow-text">GISP NEXUS OS</h1>
                    <p class="text-[10px] opacity-50 uppercase tracking-[0.2em]">Market Intelligence System v1.0</p>
                </div>
                <div class="text-right">
                    <div class="flex items-center justify-end space-x-2 text-xs">
                        <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span>AI CORE ACTIVE</span>
                    </div>
                    <p id="clock" class="text-[10px] mt-1 opacity-50">UTC: --:--:--</p>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="nexus-border bg-white/5 p-6 rounded-2xl">
                    <p class="text-[10px] text-gray-500 uppercase font-bold">Liquidity Imbalance</p>
                    <div id="imbalance" class="text-5xl font-bold mt-2">1.00</div>
                    <div class="mt-4 h-1 bg-cyan-900 w-full rounded-full overflow-hidden">
                        <div id="bar" class="h-full bg-cyan-400 transition-all duration-1000" style="width: 50%"></div>
                    </div>
                </div>

                <div class="md:col-span-2 nexus-border bg-cyan-500/5 p-6 rounded-2xl relative">
                    <p class="text-[10px] text-gray-500 uppercase font-bold">Institutional Intelligence</p>
                    <div id="signal" class="text-2xl font-bold text-white mt-2">INITIALIZING...</div>
                    <div class="grid grid-cols-3 gap-4 mt-8">
                        <div><p class="text-[10px] opacity-40">ENTRY</p><p id="price" class="text-lg text-white">0.00</p></div>
                        <div><p class="text-[10px] text-green-500">TARGET</p><p id="tp" class="text-lg text-green-400">0.00</p></div>
                        <div><p class="text-[10px] text-red-500">PROTECTION</p><p id="sl" class="text-lg text-red-400">0.00</p></div>
                    </div>
                </div>
            </div>

            <div class="nexus-border bg-black/40 p-4 rounded-xl text-[10px] font-mono h-32 overflow-y-auto" id="logs">
                > GISP Nexus System Booted... <br>
                > Connecting to Binance WebSocket...
            </div>
        </div>

        <script>
            async function updateNexus() {
                try {
                    const res = await fetch('/api/data');
                    const data = await res.json();
                    
                    document.getElementById('signal').innerText = data.signal;
                    document.getElementById('imbalance').innerText = data.imbalance;
                    document.getElementById('price').innerText = '$' + data.price;
                    document.getElementById('tp').innerText = '$' + data.tp;
                    document.getElementById('sl').innerText = '$' + data.sl;
                    
                    const bar = document.getElementById('bar');
                    let width = Math.min(data.imbalance * 50, 100);
                    bar.style.width = width + '%';

                    const logs = document.getElementById('logs');
                    logs.innerHTML += `> [${data.time}] ${data.symbol} Analyze complete. Signal: ${data.signal}<br>`;
                    logs.scrollTop = logs.scrollHeight;
                } catch(e) {}
            }
            setInterval(updateNexus, 5000);
            updateNexus();
            setInterval(() => {
                document.getElementById('clock').innerText = 'UTC: ' + new Date().toUTCString().split(' ')[4];
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.get("/api/data")
def get_api_data():
    return engine.get_market_data("BTC/USDT")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
