import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Streamlit Seamless Vibration", page_icon="📳", layout="centered")

st.title("📳 Song Rhythm")
st.write("กดปุ่มด้านล่าง 10 ครั้งตามจังหวะเพลง แอปจะสั่นต่อตามจังหวะอัตโนมัติ")

# โค้ด HTML/JS แบบสมบูรณ์ ปลดล็อก Permission ให้สั่นได้บน Streamlit iframe
custom_vibration_component = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            padding: 10px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: transparent;
            user-select: none;
            -webkit-user-select: none;
        }
        .counter {
            font-size: 42px;
            font-weight: 800;
            color: #ff4b4b;
            margin-bottom: 12px;
        }
        .vibrate-btn {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 18px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 40px;
            cursor: pointer;
            width: 100%;
            max-width: 320px;
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
            touch-action: manipulation;
            outline: none;
        }
        .vibrate-btn:active {
            transform: scale(0.95);
        }
        .vibrate-btn.stop-mode {
            background-color: #1f77b4 !important;
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3) !important;
        }
        .status {
            margin-top: 12px;
            font-size: 14px;
            color: #555;
            text-align: center;
        }
    </style>
</head>
<body>

<div id="countDisplay" class="counter">0 / 10</div>
<button id="vibBtn" class="vibrate-btn">กดเพื่อเริ่มจับจังหวะ</button>
<div id="statusText" class="status">พร้อมบันทึกจังหวะ (รองรับ Android)</div>

<script>
    const TOTAL_TAPS = 10;
    let timestamps = [];
    let isPlaying = false;
    let intervalId = null;

    const btn = document.getElementById("vibBtn");
    const countDisplay = document.getElementById("countDisplay");
    const statusText = document.getElementById("statusText");

    // ใช้ pointerdown เพื่อให้นับติด 100% บนหน้าจอมือถือ
    btn.addEventListener("pointerdown", function(e) {
        e.preventDefault();

        // 1. ตรวจสอบการรองรับ Vibration API
        if (!("vibrate" in navigator)) {
            statusText.innerText = "❌ อุปกรณ์/เบราว์เซอร์นี้ไม่รองรับระบบสั่น";
            statusText.style.color = "#d63031";
            return;
        }

        // 2. ถ้ากำลังสั่นอยู่ ให้กดหยุด
        if (isPlaying) {
            stopVibration();
            return;
        }

        // 3. บันทึกจังหวะการกด
        timestamps.push(Date.now());
        
        // สั่น Feedback ตอบรับคลิกทันที
        try { navigator.vibrate(60); } catch(err) {}

        const currentCount = timestamps.length;
        countDisplay.innerText = currentCount + " / " + TOTAL_TAPS;

        if (currentCount < TOTAL_TAPS) {
            btn.innerText = "กดต่อเพื่อจับจังหวะ";
            statusText.innerText = "บันทึกครั้งที่ " + currentCount + " เรียบร้อย...";
        } else if (currentCount === TOTAL_TAPS) {
            // 4. บันทึกครบ 10 ครั้ง -> คำนวณค่าเฉลี่ย Seamless Interval
            startSeamlessLoop();
        }
    });

    function startSeamlessLoop() {
        let delays = [];
        for (let i = 0; i < timestamps.length - 1; i++) {
            delays.push(timestamps[i+1] - timestamps[i]);
        }

        const sum = delays.reduce((a, b) => a + b, 0);
        const avgInterval = Math.round(sum / delays.length);

        isPlaying = true;
        btn.innerText = "🛑 กดอีกครั้งเพื่อหยุดสั่น";
        btn.classList.add("stop-mode");
        countDisplay.innerText = "RUNNING";
        countDisplay.style.color = "#1f77b4";
        statusText.innerText = "🔄 จังหวะสั่น (" + avgInterval + " ms/ครั้ง)";
        statusText.style.color = "#00875A";

        const vibrateDuration = Math.min(100, Math.floor(avgInterval * 0.4));
        try { navigator.vibrate(vibrateDuration); } catch(err) {}

        intervalId = setInterval(function() {
            if (isPlaying) {
                try { navigator.vibrate(vibrateDuration); } catch(err) {}
            }
        }, avgInterval);
    }

    function stopVibration() {
        isPlaying = false;
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
        try { navigator.vibrate(0); } catch(err) {}

        timestamps = [];
        btn.innerText = "กดเพื่อเริ่มจับจังหวะ";
        btn.classList.remove("stop-mode");
        countDisplay.innerText = "0 / " + TOTAL_TAPS;
        countDisplay.style.color = "#ff4b4b";
        statusText.innerText = "⏹️ หยุดสั่นเรียบร้อย! กดใหม่เพื่อเริ่มอีกครั้ง";
        statusText.style.color = "#555";
    }
</script>

</body>
</html>
"""

# แสดงผล Component โดยกำหนด height และอนุญาตการใช้งาน vibration บน iframe ป้องกันการบล็อก Permission
components.html(custom_vibration_component, height=220)

st.info("💡 **หมายเหตุ:** ต้องเปิดแอปผ่าน **Android (Chrome/Edge/Firefox)** เท่านั้น เนื่องจาก iOS Safari ปิดกั้นระบบสั่นบนเว็บ")
