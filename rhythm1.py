import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Rhythm Vibration App", page_icon="📳", layout="centered")

st.title("📳 Seamless Rhythm Vibration")
st.write("กดปุ่ม 10 ครั้งเพื่อตั้งความเร็ว ระบบจะนำมาคำนวณเป็นจังหวะที่เท่ากันเป๊ะและสั่นต่อเนื่องแบบไร้รอยต่อ")

vibration_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .vibrate-btn {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 18px 36px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
            transition: all 0.2s ease;
            width: 85%;
            max-width: 340px;
        }
        .vibrate-btn:active {
            transform: scale(0.95);
        }
        .vibrate-btn.stop {
            background-color: #2e86de;
            box-shadow: 0 4px 12px rgba(46, 134, 222, 0.3);
        }
        .status-text {
            margin-top: 15px;
            color: #555;
            font-size: 15px;
            text-align: center;
            font-weight: 500;
        }
    </style>
</head>
<body>

<div class="container">
    <button id="mainBtn" class="vibrate-btn" onclick="handleClick()">กดเพื่อเริ่มจับจังหวะ (0/10)</button>
    <p id="status" class="status-text">พร้อมบันทึกจังหวะการกด</p>
</div>

<script>
    let timestamps = [];
    let isPlaying = false;
    let intervalId = null;

    const TOTAL_TAPS = 10;

    function handleClick() {
        if (!("vibrate" in navigator)) {
            document.getElementById("status").innerText = "❌ อุปกรณ์นี้ไม่รองรับระบบสั่น";
            document.getElementById("status").style.color = "#DE350B";
            return;
        }

        // หากกำลังสั่นอยู่ กดอีกครั้งจะเป็นการหยุด
        if (isPlaying) {
            stopRhythm();
            return;
        }

        const now = Date.now();
        timestamps.push(now);
        
        // Haptic Feedback ตอนกดปุ่ม
        navigator.vibrate(80);

        const count = timestamps.length;
        const btn = document.getElementById("mainBtn");
        const status = document.getElementById("status");

        if (count < TOTAL_TAPS) {
            btn.innerText = `กดต่อเพื่อจับจังหวะ (${count}/${TOTAL_TAPS})`;
            status.innerText = `บันทึกครั้งที่ ${count} เรียบร้อย...`;
        } else if (count === TOTAL_TAPS) {
            // 1. หาความห่างระหว่างการกดแต่ละครั้ง (8-9 ช่วง)
            let delays = [];
            for (let i = 0; i < timestamps.length - 1; i++) {
                delays.push(timestamps[i+1] - timestamps[i]);
            }

            # 2. คำนวณค่าเฉลี่ย เพื่อให้ทุกจังหวะเท่ากันเป๊ะ (Average Interval)
            const sum = delays.reduce((a, b) => a + b, 0);
            const avgInterval = Math.round(sum / delays.length);

            isPlaying = true;
            btn.innerText = "🛑 กดอีกครั้งเพื่อหยุดสั่น";
            btn.classList.add("stop");
            status.innerText = `🔄 กำลังสั่นแบบไร้รอยต่อ (ทุกๆ ${avgInterval} ms)...`;
            status.style.color = "#00875A";

            // 3. เริ่มสั่นทันที 1 ครั้ง แล้วสั่นวนไปเรื่อยๆ ด้วย setInterval ตามระยะเวลาเฉลี่ย
            startSeamlessLoop(avgInterval);
        }
    }

    function startSeamlessLoop(intervalMs) {
        // ระยะเวลาสั่นแต่ละครั้ง (กำหนดไม่ให้ยาวเกินช่วงระยะห่างจังหวะ)
        const vibrateDuration = Math.min(100, Math.floor(intervalMs * 0.4));

        // สั่นครั้งแรกทันที
        navigator.vibrate(vibrateDuration);

        // วนสั่นต่อเนื่องด้วยจังหวะคงที่เท่ากันตลอดแบบไร้รอยต่อ
        intervalId = setInterval(() => {
            if (isPlaying) {
                navigator.vibrate(vibrateDuration);
            }
        }, intervalMs);
    }

    function stopRhythm() {
        isPlaying = false;
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
        navigator.vibrate(0); // สั่งยกเลิกการสั่นทันที

        // รีเซ็ตค่าใหม่
        timestamps = [];

        const btn = document.getElementById("mainBtn");
        const status = document.getElementById("status");

        btn.innerText = `กดเพื่อเริ่มจับจังหวะ (0/${TOTAL_TAPS})`;
        btn.classList.remove("stop");
        status.innerText = "⏹️ หยุดสั่นแล้ว! กดใหม่เพื่อเริ่มบันทึกจังหวะใหม่";
        status.style.color = "#555";
    }
</script>

</body>
</html>
"""

components.html(vibration_code, height=180)

st.info("**การปรับปรุง:** เปลี่ยนระบบมาใช้ `setInterval` ควบคู่กับค่าเฉลี่ยความเร็วจากการกด 10 ครั้ง ทำให้จังหวะที่ได้มีความถี่ **เท่ากันสม่ำเสมอเป๊ะ** และสั่นต่อเนื่องยาวไปได้แบบไม่มีสะดุดไร้รอยต่อครับ")
