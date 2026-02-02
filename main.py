import os
import random
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    # Bu qism ilovaning dizayni (HTML/CSS/JS)
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GISP | Intelligent Terminal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #0B0E11; color: white; }
            .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
            .neon-blue { color: #00D1FF; text-shadow: 0 0 10px #00D1FF; }
            .neon-green { color: #00FFA3; text-shadow: 0 0 10px #00FFA3; }
        </style>
    </head>
    <body class="flex items-center justify-center min-h-screen p-4">
        <div class="max-w-md w-full glass rounded-[2rem] p-8 shadow-2xl border-t border-white/20">
            <!-- Header -->
            <div class="flex justify-between items-center mb-10">
                <div>
                    <h1 class="text-2xl font-extrabold tracking-tighter neon-blue">GISP.AI</h1>
                    <p class="text-xs text-gray-400">Global Intelligent Signal Platform</p>
                </div>
                <div class="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
            </div>

            <!-- Signal Card -->
            <div class="text-center py-10 rounded-3xl bg-white/5 border border-white/10 mb-8">
                <p class="text-sm text-gray-400 uppercase tracking-[0.2em] mb-2">Current AI Signal</p>
                <h2 id="signal" class="text-6xl font-black neon-green mb-4">---</h2>
                <div class="flex justify-center space-x-4">
                    <div class="text-center">
                        <p class="text-[10px] text-gray-500 uppercase">Confidence</p>
                        <p id="confidence" class="text-xl font-bold">--%</p>
                    </div>
                </div>
            </div>

            <!-- Analysis Section -->
            <div class="space-y-4">
                <h3 class="text-sm font-semibold text-gray-300">Market Intelligence Analysis:</h3>
                <p id="analysis" class="text-sm text-gray-400 leading-relaxed italic">
                    Initializing GNN & PTX-1 Models...
                </p>
            </div>

            <!-- Footer Buttons -->
            <div class="mt-12 grid grid-cols-2 gap-4">
                <button onclick="updateData()" class="py-4 rounded-2xl bg-white/10 hover:bg-white/20 transition font-bold text-sm">REFRESH</button>
                <button class="py-4 rounded-2xl bg-sky-500 hover:bg-sky-600 transition font-bold text-sm">EXECUTE</button>
            </div>
        </div>

        <script>
            async function updateData() {
                const pairs = ['BTC', 'ETH', 'XAU', 'EURUSD'];
                const randomPair = pairs[Math.floor(Math.random() * pairs.length)];
                
                // API-dan ma'lumot olish
                const response = await fetch(`/api/v1/signal/${randomPair}`);
                const data = await response.json();

                // Ekranni yangilash
                document.getElementById('signal').innerText = data.signal;
                document.getElementById('confidence').innerText = data.confidence;
                document.getElementById('analysis').innerText = data.analysis + " Focused on: " + data.asset;
                
                // Rangni o'zgartirish
                const sigEl = document.getElementById('signal');
                if(data.signal.includes('BUY')) {
                    sigEl.className = 'text-6xl font-black neon-green mb-4';
                } else {
                    sigEl.className = 'text-6xl font-black text-red-500 mb-4 shadow-red-500';
                }
            }
            
            // Avtomatik yangilash
            updateData();
            setInterval(updateData, 10000);
        </script>
    </body>
    </html>
    """

@app.get("/api/v1/signal/{pair}")
def get_signal(pair: str):
    confidence = round(random.uniform(91.2, 99.8), 2)
    actions = ["STRONG BUY", "BUY", "SELL", "STRONG SELL"]
    
    return {
        "asset": pair.upper(),
        "signal": random.choice(actions),
        "confidence": f"{confidence}%",
        "analysis": "AI Engine detects a high-probability volatility expansion."
    }
