#!/usr/bin/env python3
"""
Run this script ONCE on any machine with internet (not blocked).
It downloads aframe + AR.js and builds a single self-contained HTML file
with both libraries inlined — no CDN needed at runtime.

Usage:
    python3 build.py
Output:
    sibirius-quest-FINAL.html   ← send THIS to your phone/server
"""

import urllib.request, base64, sys, os

AFRAME_URL = "https://aframe.io/releases/1.6.0/aframe.min.js"
ARJS_URL   = "https://cdn.jsdelivr.net/gh/AR-js-org/AR.js@3.4.7/aframe/build/aframe-ar.min.js"

def fetch(url, label):
    print(f"  Downloading {label}...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        print(f"OK ({len(data)//1024}KB)")
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

print("Building self-contained Sibirius Quest AR...")
aframe_js = fetch(AFRAME_URL, "A-Frame 1.6.0")
arjs_js   = fetch(ARJS_URL,   "AR.js 3.4.7")

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Сибириус Квест AR</title>
    <!-- A-Frame 1.6.0 — inlined, no CDN needed -->
    <script>{aframe_js}</script>
    <!-- AR.js 3.4.7 — inlined, no CDN needed -->
    <script>{arjs_js}</script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .a-enter-vr, .a-loader-title, .a-orientation-modal {{ display: none !important; }}

        #geo-screen {{
            position: fixed; inset: 0;
            background: #121212;
            z-index: 9999;
            display: flex; justify-content: center; align-items: center;
            padding: 28px;
        }}
        #final-screen {{
            position: fixed; inset: 0;
            background: #121212;
            z-index: 9999;
            display: none;
            justify-content: center; align-items: center;
            padding: 28px;
        }}
        #game-screen {{
            position: fixed;
            bottom: 32px; left: 50%; transform: translateX(-50%);
            width: 90%; max-width: 420px;
            background: rgba(15,15,15,0.88);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 20px 22px 18px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
            text-align: center;
            z-index: 9998;
            display: none;
            pointer-events: none;
        }}
        #game-screen > * {{ pointer-events: auto; }}
        .container {{ width: 100%; max-width: 380px; text-align: center; }}
        h2 {{ color: #00FF88; font-size: 24px; font-weight: 700; margin: 0 0 10px; }}
        h3 {{ color: #00FF88; font-size: 17px; font-weight: 600; margin: 0 0 6px; }}
        p  {{ color: #D0D0D0; font-size: 14px; line-height: 1.55; margin: 4px 0; }}
        .progress {{ font-size: 11px; color: #00FF88; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; }}
        .hint {{ color: #00CC66; font-size: 13px; font-weight: 600; margin-top: 10px; }}
        .btn {{
            display: block; width: 100%; padding: 15px;
            background: #00FF88; color: #0a0a0a;
            border: none; border-radius: 12px;
            font-size: 16px; font-weight: 700; cursor: pointer;
            margin-top: 18px; transition: opacity .15s;
            pointer-events: auto;
        }}
        .btn:disabled {{ background: #2a2a2a; color: #555; cursor: not-allowed; }}
        .btn:not(:disabled):active {{ opacity: .75; }}
        #toast {{
            position: fixed;
            top: 36px; left: 50%; transform: translateX(-50%);
            background: #00FF88; color: #0a0a0a;
            padding: 13px 24px; border-radius: 40px;
            font-size: 14px; font-weight: 700;
            z-index: 99999; pointer-events: none;
            box-shadow: 0 4px 20px rgba(0,255,136,.35);
            opacity: 0; transition: opacity .25s;
            white-space: nowrap; max-width: 88vw; text-align: center;
        }}
        #toast.show {{ opacity: 1; }}
        #marker-hint {{
            position: fixed;
            top: 12px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.7);
            color: #fff; font-size: 12px; font-weight: 600;
            padding: 6px 14px; border-radius: 20px;
            z-index: 9997; display: none;
            pointer-events: none;
        }}
    </style>
</head>
<body style="margin: 0; overflow: hidden;">

<div id="geo-screen">
    <div class="container">
        <h2>🗺️ Сибириус Квест</h2>
        <p id="status-text" style="margin-bottom:4px;">Синхронизация с GPS…</p>
        <p style="font-size:12px;color:#555;">Разреши доступ к камере и геолокации</p>
        <button id="start-btn" class="btn" disabled>Начать квест</button>
    </div>
</div>

<div id="game-screen">
    <div class="progress">Задание <span id="score">1</span> / 4</div>
    <h3 id="quest-title"></h3>
    <p id="quest-text"></p>
    <p class="hint">📸 Наведи камеру на маркер</p>
</div>

<div id="marker-hint"></div>

<!-- FIX step 4: was checking display === 'block' but final-screen uses 'flex'.
     Now game-screen always uses display:block, final-screen always uses display:flex.
     The gameActive flag is the single source of truth. -->
<div id="final-screen">
    <div class="container">
        <h2>Квест пройден! 🎉</h2>
        <p style="margin-top:10px;">Ты отыскал все AR-метки Сибириуса. Красавчик!</p>
    </div>
</div>

<div id="toast"></div>

<a-scene
    vr-mode-ui="enabled: false"
    arjs="sourceType: webcam; debugUIEnabled: false; detectionMode: mono_and_matrix; matrixCodeType: 3x3;"
    loading-screen="enabled: false"
    renderer="logarithmicDepthBuffer: true; precision: medium; antialias: false;"
>
    <a-marker preset="hiro" id="m1">
        <a-sphere color="#00FF88" radius="0.4" position="0 0.4 0"
            animation="property: rotation; to: 0 360 0; loop: true; dur: 3000">
        </a-sphere>
        <a-ring color="#00FF88" radius-inner="0.5" radius-outer="0.6"
            rotation="-90 0 0" position="0 0.05 0">
        </a-ring>
    </a-marker>

    <a-marker preset="kanji" id="m2">
        <a-box color="#FF6B35" width="0.6" height="0.6" depth="0.6" position="0 0.3 0"
            animation="property: rotation; to: 360 360 0; loop: true; dur: 3000">
        </a-box>
    </a-marker>

    <a-marker type="barcode" value="1" id="m3">
        <a-cone color="#9B59B6" radius-bottom="0.4" radius-top="0" height="0.8"
            position="0 0.4 0"
            animation="property: rotation; to: 0 360 0; loop: true; dur: 2500">
        </a-cone>
    </a-marker>

    <a-marker type="barcode" value="2" id="m4">
        <a-torus color="#F1C40F" radius="0.3" radius-tubular="0.05"
            position="0 0.3 0"
            animation="property: rotation; to: 0 360 360; loop: true; dur: 2000">
        </a-torus>
    </a-marker>

    <a-entity camera></a-entity>
</a-scene>

<script>
const DEBUG_MODE   = true;
const SIBIRIUS_LAT = 61.001272;
const SIBIRIUS_LON = 68.994418;
const GEO_RADIUS_KM = 0.1;

const steps = [
    {{ title: "Шаг 1: Велопарковка",      text: "Найди маркер HIRO около велопарковки.",           hint: "Маркер: HIRO",              markerId: "m1", toast: "Велопарковка! 🔥 Идём ко входу." }},
    {{ title: "Шаг 2: Главный вход",       text: "Найди маркер KANJI у главного входа.",             hint: "Маркер: KANJI",             markerId: "m2", toast: "Главный вход! 🚀 Заходим внутрь." }},
    {{ title: "Шаг 3: Кофемашина",         text: "Найди маркер «1» у кофемашины в холле.",           hint: "Маркер: штрихкод №1",       markerId: "m3", toast: "Кофемашина! ⚡ Последний шаг." }},
    {{ title: "Шаг 4: Коворкинг",          text: "Поднимись на 2-й этаж. Найди маркер «2».",         hint: "Маркер: штрихкод №2",       markerId: "m4", toast: "КВЕСТ ПРОЙДЕН! ТЫ КРАСАВЧИК! 🎉" }}
];

let currentStep = 0;
let locked = false;
// FIX: single flag instead of checking display string (was breaking step 4)
let gameActive = false;

let toastTimer;
function showToast(msg, ms) {{
    ms = ms || 2800;
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() {{ el.classList.remove('show'); }}, ms);
}}

function dist(la1,lo1,la2,lo2) {{
    var R=6371, dL=(la2-la1)*Math.PI/180, dO=(lo2-lo1)*Math.PI/180;
    var a=Math.sin(dL/2)*Math.sin(dL/2)+Math.cos(la1*Math.PI/180)*Math.cos(la2*Math.PI/180)*Math.sin(dO/2)*Math.sin(dO/2);
    return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}}

if (DEBUG_MODE) {{
    document.getElementById('status-text').textContent = 'Режим теста — локация OK ✅';
    document.getElementById('start-btn').disabled = false;
}} else {{
    navigator.geolocation.getCurrentPosition(
        function(pos) {{
            var d = dist(pos.coords.latitude, pos.coords.longitude, SIBIRIUS_LAT, SIBIRIUS_LON);
            if (d <= GEO_RADIUS_KM) {{
                document.getElementById('status-text').textContent = 'Ты в Сибириусе! ✅';
                document.getElementById('start-btn').disabled = false;
            }} else {{
                document.getElementById('status-text').textContent = 'До Сибириуса: ' + d.toFixed(2) + ' км';
            }}
        }},
        function() {{ document.getElementById('status-text').textContent = 'Ошибка GPS — разреши доступ в браузере'; }},
        {{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }}
    );
}}

document.getElementById('start-btn').addEventListener('click', function() {{
    document.getElementById('geo-screen').style.display = 'none';
    document.getElementById('game-screen').style.display = 'block';
    document.getElementById('marker-hint').style.display = 'block';
    gameActive = true;
    showStep();
}});

function showStep() {{
    var s = steps[currentStep];
    document.getElementById('score').textContent       = currentStep + 1;
    document.getElementById('quest-title').textContent = s.title;
    document.getElementById('quest-text').textContent  = s.text;
    document.getElementById('marker-hint').textContent = s.hint;
}}

function advance() {{
    locked = true;
    showToast(steps[currentStep].toast);
    currentStep++;
    setTimeout(function() {{
        locked = false;
        if (currentStep < steps.length) {{
            showStep();
        }} else {{
            // FIX: set gameActive false FIRST, then swap screens
            gameActive = false;
            document.getElementById('game-screen').style.display  = 'none';
            document.getElementById('marker-hint').style.display  = 'none';
            document.getElementById('final-screen').style.display = 'flex';
        }}
    }}, 3000);
}}

setInterval(function() {{
    if (!gameActive) return;
    if (locked) return;
    var s = steps[currentStep];
    if (!s) return;
    var m = document.getElementById(s.markerId);
    if (m && m.object3D && m.object3D.visible) advance();
}}, 500);
</script>
</body>
</html>"""

out = "sibirius-quest-FINAL.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(out) // 1024
print(f"\nDone! Output: {out} ({size_kb}KB)")
print("This file has ZERO external dependencies — works fully offline.")
