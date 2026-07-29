import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>10-Tap Seamless Vibration</title>
    <style>
        * { box-sizing: border-box; touch-action: manipulation; }
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background-color: #0f172a;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            user-select: none;
        }
        .card {
            background-color: #1e293b;
            padding: 30px 24px;
            border-radius: 24px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            text-align: center;
            width: 90%;
            max-width: 400px;
        }
        h2 { margin-top: 0; font-size: 22px; color: #38bdf8; }
        .counter-display {
            font-size: 48px;
            font-weight: 800;
            color: #f43f5e;
            margin: 15px 0;
            text-shadow: 0 0 10px rgba(244, 63, 94, 0.3);
        }
        .vibrate-btn {
            background-color: #ef4444;
            color: white;
            border: none;
            padding: 22px 30px;
            font-size: 20px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            width: 100%;
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
            transition: transform 0.05s ease, background-color 0.2s ease;
            outline: none;
        }
        .vibrate-btn:active {
            transform: scale(0.93);
            background-color: #dc2626;
        }
        .vibrate-btn.stop-mode {
            background-color: #0284c7 !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
        }
        .status-box {
            margin-top: 20px;
            font-size: 15px;
            font-weight: 500;
            color: #cbd5e1;
            min-height: 24px;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>📳 Seamless Vibration Loop</h2>
    
    <!-- ตัวเลขแสดงจำนวนครั้งการนับขนาดใหญ่ -->
    <div id="counter" class="counter-display">0 / 10</div>

    <button id="vibBtn" class="vibrate-btn">กดเพื่อเริ่มจับจังหวะ</button>
    <div id="statusBox" class="status-box">พร้อมจับจังหวะการกด</div>
</div>

<script>
    const TOTAL_TAPS = 10;
    window.tapTimestamps = [];
    window.isVibratingLoop = false;
    window.loopIntervalId = null;

    const btn = document.getElementById("vibBtn");
    const statusBox = document.getElementById("statusBox");
    const counterDisplay = document.getElementById("counter");

    // ฟังก์ชันประมวลผลเมื่อมีการกดปุ่ม
    function handleTap(e) {
        if (e) {
            e.preventDefault(); // ป้องกัน double click / zoom
        }

        // 1. ถ้าอยู่ในสถานะกำลังสั่นวนลูป -> กดเพื่อหยุด
        if (window.isVibratingLoop) {
            stopVibration();
            return;
        }

        // 2. บันทึก เวลา ณ ตอนที่กด
        const now = Date.now();
        window.tapTimestamps.push(now);

        // 3. สั่น Feedback สั้นๆ ตอบสนองการกดทุกครั้ง
        if ("vibrate" in navigator) {
            try { navigator.vibrate(50); } catch(err) {}
        }

        const currentCount = window.tapTimestamps.length;

        // 4. อัปเดตตัวเลขอ่านง่ายบนหน้าจอ
        counterDisplay.innerText = `${currentCount} / ${TOTAL_TAPS}`;

        if (currentCount < TOTAL_TAPS) {
            btn.innerText = `กดต่อเพื่อจับจังหวะ`;
            statusBox.innerText = `บันทึกจังหวะที่ ${currentCount} แล้ว...`;
            statusBox.style.color = "#cbd5e1";
        } 
        else if (currentCount === TOTAL_TAPS) {
            // 5. บันทึกครบ 10 ครั้ง -> คำนวณหาค่าเฉลี่ย
            startSeamlessProcess();
        }
    }

    function startSeamlessProcess() {
        let delays = [];
        for (let i = 0; i < window.tapTimestamps.length - 1; i++) {
            delays.push(window.tapTimestamps[i+1] - window.tapTimestamps[i]);
        }

        const sum = delays.reduce((a, b) => a + b, 0);
        const avgInterval = Math.round(sum / delays.length);

        window.isVibratingLoop = true;
        btn.innerText = "🛑 กดอีกครั้งเพื่อหยุดสั่น";
        btn.classList.add("stop-mode");
        counterDisplay.innerText = "RUNNING";
        counterDisplay.style.color = "#38bdf8";
        
        statusBox.innerText = `🔄 สั่นต่อเนื่องไร้รอยต่อ (จังหวะละ ${avgInterval} ms)`;
        statusBox.style.color = "#4ade80";

        // เริ่มสั่นวนลูป
        const vibrateDuration = Math.min(100, Math.floor(avgInterval * 0.4));
        if ("vibrate" in navigator) navigator.vibrate(vibrateDuration);

        window.loopIntervalId = setInterval(() => {
            if (window.isVibratingLoop && "vibrate" in navigator) {
                navigator.vibrate(vibrateDuration);
            }
        }, avgInterval);
    }

    function stopVibration() {
        window.isVibratingLoop = false;
        if (window.loopIntervalId) {
            clearInterval(window.loopIntervalId);
            window.loopIntervalId = null;
        }
        if ("vibrate" in navigator) navigator.vibrate(0);

        window.tapTimestamps = []; // ล้างค่าการนับ

        btn.innerText = "กดเพื่อเริ่มจับจังหวะ";
        btn.classList.remove("stop-mode");
        counterDisplay.innerText = `0 / ${TOTAL_TAPS}`;
        counterDisplay.style.color = "#f43f5e";
        
        statusBox.innerText = "⏹️ หยุดสั่นเรียบร้อย! กดใหม่เพื่อเริ่มนับอีกครั้ง";
        statusBox.style.color = "#cbd5e1";
    }

    // ผูก Event ทั้ง pointerdown และ click เพื่อให้รองรับทัชสกรีนมือถือทุกเบราว์เซอร์
    let isProcessing = false;
    function triggerEvent(e) {
        if (isProcessing) return;
        isProcessing = true;
        handleTap(e);
        setTimeout(() => { isProcessing = false; }, 50); // ป้องกันการนับซ้ำจากการรันพร้อมกัน
    }

    btn.addEventListener("pointerdown", triggerEvent);
</script>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_CONTENT

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
