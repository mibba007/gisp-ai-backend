import os
import random
import uvicorn
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="GISP Enterprise Terminal")

# --- AI MODULLARI (LOGIC SIMULATION) ---

class GISP_AI_Suite:
    def get_market_regime(self):
        # MR-GNN: Market Regime Graph Neural Network simulyatsiyasi
        regimes = ["Risk-On", "Risk-Off", "Neutral", "High Volatility"]
        return random.choice(regimes)

    def get_nlp_sentiment(self):
        # FIN-LLaMA: NLP Sentiment simulyatsiyasi
        score = round(random.uniform(-1, 1), 2)
        impact = "Bullish" if score > 0.2 else "Bearish" if score < -0.2 else "Neutral"
        return {"score": score, "impact": impact}

    def get_ptx1_forecast(self, pair):
        # PTX-1: Price Transformer simulyatsiyasi
        trend = random.choice(["Upward", "Downward", "Sideways"])
        confidence = round(random.uniform(85, 99.5), 2)
        return {"trend": trend, "conf": confidence}

ai_engine = GISP_AI_Suite()

# --- WEB TERMINAL UI (HTML/JS) ---

@app.get("/", response_class=HTMLResponse)
async def terminal():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GISP | Global Intelligent Signal Platform</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- TradingView Chart Widget -->
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <style>
            body { background-color: #060709; color: #E1E1E1; font-family: 'Inter', sans-serif; }
            .terminal-border { border: 1px solid rgba(0, 209, 255, 0.2); }
            .glow-blue { box-shadow: 0 0 15px rgba(0, 209, 255, 0.1); }
            .bg-dark-panel { background-color: #0B0E14; }
            ::-webkit-scrollbar { width: 4px; }
            ::-webkit-scrollbar-thumb { background: #1E222D; }
        </style>
    </head>
    <body class="h-screen overflow-hidden flex flex-col">

        <!-- TOP NAVIGATION BAR -->
        <nav class="h-14 border-b border-gray-800 bg-dark-panel flex items-center justify-between px-6">
            <div class="flex items-center space-x-4">
                <span class="text-xl font-black tracking-tighter text-sky-400">GISP <span class="text-white text-xs font-light">v1.0.0 Enterprise</span></span>
            </div>
            <div class="flex space-x-6 text-xs font-mono">
                <div id="regime-tag" class="px-3 py-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">SYSTEM: ONLINE</div>
                <div class="text-gray-500">LATENCY: <span class="text-green-400">14ms</span></div>
                <div id="clock" class="text-gray-400">00:00:00</div>
            </div>
        </nav>

        <main class="flex-1 flex overflow-hidden">
            <!-- LEFT PANEL: ASSET LIST & SIGNALS -->
            <aside class="w-80 border-r border-gray-800 bg-dark-panel overflow-y-auto p-4 space-y-4">
                <h3 class="text-xs font-bold text-gray-500 uppercase tracking-widest">Live AI Signals</h3>
                <div id="signal-list" class="space-y-3">
                    <!-- Signals will be injected here -->
                </div>
            </aside>

            <!-- CENTER PANEL: CHART & SYSTEM LOGS -->
            <section class="flex-1 flex flex-col bg-black">
                <!-- CHART -->
                <div class="flex-1 relative">
                    <div id="tv_chart_container" class="absolute inset-0"></div>
                </div>
                
                <!-- SYSTEM LOGS (The "MIND" of AI) -->
                <div class="h-48 border-t border-gray-800 bg-dark-panel p-4 font-mono text-[10px] overflow-y-auto">
                    <h4 class="text-gray-500 mb-2 uppercase">AI Neural Engine Logs (PTX-1 & MR-GNN)</h4>
                    <div id="logs" class="space-y-1">
                        <p class="text-blue-400">[SYSTEM] Initializing GISP Neural Network...</p>
                    </div>
                </div>
            </section>

            <!-- RIGHT PANEL: ANALYSIS & SENTIMENT -->
            <aside class="w-72 border-l border-gray-800 bg-dark-panel p-4 space-y-6">
                <div>
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4">Market Regime</h3>
                    <div id="regime-display" class="h-20 rounded-xl border border-gray-800 flex items-center justify-center text-xl font-bold text-sky-400">---</div>
                </div>
                <div>
                    <h3 class="text-xs font-bold text-gray-500 uppercase mb-4">NLP Sentiment</h3>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between"><span>Impact:</span> <span id="nlp-impact" class="font-bold">Neutral</span></div>
                        <div class="w-full bg-gray-800 h-1 rounded-full overflow-hidden">
                            <div id="nlp-bar" class="bg-sky-400 h-full w-1/2"></div>
                        </div>
                    </div>
                </div>
                <div class="pt-4 border-t border-gray-800">
                    <button class="w-full py-3 bg-sky-600 hover:bg-sky-500 rounded font-bold text-xs transition">EXECUTE SMART ORDER</button>
                </div>
            </aside>
        </main>

        <script>
            // Initialize TradingView Chart
            new TradingView.widget({
                "autosize": true,
                "symbol": "BINANCE:BTCUSDT",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tv_chart_container"
            });

            function addLog(msg, color='text-gray-400') {
                const logs = document.getElementById('logs');
                const p = document.createElement('p');
                p.className = color;
                p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
                logs.prepend(p);
            }

            async function refreshAI() {
                const assets = ['BTC', 'ETH', 'XAU', 'EURUSD'];
                const signalList = document.getElementById('signal-list');
                signalList.innerHTML = '';

                for(let asset of assets) {
                    const res = await fetch(`/api/v1/full-analysis/${asset}`);
                    const data = await response = await res.json();
                    
                    // Update Signals
                    const card = document.createElement('div');
                    card.className = "p-3 rounded-lg border border-gray-800 bg-white/5";
                    const sigColor = data.ptx1.trend === 'Upward' ? 'text-green-400' : 'text-red-400';
                    card.innerHTML = `
                        <div class="flex justify-between font-bold text-sm"><span>${asset}/USD</span> <span class="${sigColor}">${data.ptx1.trend}</span></div>
                        <div class="flex justify-between text-[10px] text-gray-500 mt-1"><span>Conf: ${data.ptx1.conf}%</span> <span>NLP: ${data.nlp.impact}</span></div>
                    `;
                    signalList.appendChild(card);

                    if(asset === 'BTC') {
                        document.getElementById('regime-display').innerText = data.regime;
                        document.getElementById('nlp-impact').innerText = data.nlp.impact;
                        document.getElementById('nlp-bar').style.width = ((data.nlp.score + 1) * 50) + '%';
                        addLog(`PTX-1 processed ${asset} with ${data.ptx1.conf}% confidence.`, 'text-sky-400');
                        addLog(`MR-GNN detected ${data.regime} regime.`, 'text-purple-400');
                    }
                }
            }

            setInterval(() => {
                document.getElementById('clock').innerText = new Date().toLocaleTimeString();
            }, 1000);

            setInterval(refreshAI, 15000);
            refreshAI();
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/full-analysis/{asset}")
def get_full_analysis(asset: str):
    return {
        "asset": asset,
        "regime": ai_engine.get_market_regime(),
        "nlp": ai_engine.get_nlp_sentiment(),
        "ptx1": ai_engine.get_ptx1_forecast(asset),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
