import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Rhythm Vibration App", page_icon="📳", layout="centered")

st.title("📳 10-Tap Rhythm Vibration Loop")
st.write("กดปุ่มให้ครบ 10 ครั้งตามจังหวะที่ต้องการ ระบบจะสั่นวนลูปตามจังหวะนั้นจนกว่าจะสั่งหยุด")

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
    let delays = [];
    let isPlaying = false;
    let loopTimeout = null;
    let activeTimeouts = [];

    const TOTAL_TAPS = 10; // กำหนดจำนวนครั้งที่ต้องกดเป็น 10 ครั้ง

    function handleClick() {
        if (!("vibrate" in navigator)) {
            document.getElementById("status").innerText = "❌ อุปกรณ์นี้ไม่รองรับระบบสั่น";
            document.getElementById("status").style.color = "#DE350B";
            return;
        }

        // หากกำลังเล่นลูปอยู่ การกดปุ่มจะเป็นการสั่งหยุด
        if (isPlaying) {
            stopRhythm();
            return;
        }

        const now = Date.now();
        timestamps.push(now);
        
        // สั่นสั้นๆ 50ms ทุกครั้งที่กด เพื่อส่ง Haptic Feedback บอกว่ารับค่าแล้ว
        navigator.vibrate(50);

        const count = timestamps.length;
        const btn = document.getElementById("mainBtn");
        const status = document.getElementById("status");

        if (count < TOTAL_TAPS) {
            btn.innerText = `กดต่อเพื่อจับจังหวะ (${count}/${TOTAL_TAPS})`;
            status.innerText = `บันทึกครั้งที่ ${count} เรียบร้อย...`;
        } else if (count === TOTAL_TAPS) {
            // คำนวณช่วงเวลาห่าง (Delays) ระหว่างการกดแต่ละครั้ง (ทั้งหมด 9 ช่วง)
            delays = [];
            for (let i = 0; i < timestamps.length - 1; i++) {
                delays.push(timestamps[i+1] - timestamps[i]);
            }

            isPlaying = true;
            btn.innerText = "🛑 กดอีกครั้งเพื่อหยุดสั่น";
            btn.classList.add("stop");
            status.innerText = "🔄 กำลังสั่นวนลูปตามจังหวะ 10 ครั้งของคุณ...";
            status.style.color = "#00875A";

            // เริ่มเล่นลูปสั่นตามจังหวะ
            playRhythmSequence();
        }
    }

    function playRhythmSequence() {
        if (!isPlaying) return;

        // ล้าง Timeout เดิมที่อาจค้างอยู่
        clearScheduledTimeouts();

        // สั่นครั้งที่ 1 ทันที
        navigator.vibrate(50);

        // ตั้งเวลาสั่นตามระยะห่างของอีก 9 คลิปที่บันทึกไว้
        let cumulativeTime = 0;
        for (let i = 0; i < delays.length; i++) {
            cumulativeTime += delays[i];
            let t = setTimeout(() => {
                if (isPlaying) {
                    navigator.vibrate(50); // สั่นยาว 50ms ทุกโน้ต
                }
            }, cumulativeTime);
            activeTimeouts.push(t);
        }

        // เมื่อจบครบรอบ 10 ครั้ง ให้เริ่มรอบใหม่ (บวกเว้นระยะท้ายลูปเล็กน้อย 950ms)
        loopTimeout = setTimeout(() => {
            if (isPlaying) {
                playRhythmSequence();
            }
        }, cumulativeTime + 950);
        activeTimeouts.push(loopTimeout);
    }

    function clearScheduledTimeouts() {
        activeTimeouts.forEach(t => clearTimeout(t));
        activeTimeouts = [];
    }

    function stopRhythm() {
        isPlaying = false;
        clearScheduledTimeouts();
        navigator.vibrate(0); // สั่งยกเลิกการสั่นทันที

        // รีเซ็ตค่าเพื่อเตรียมจับจังหวะใหม่
        timestamps = [];
        delays = [];

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

st.info("**จุดแก้ไข:** เพิ่มจำนวนการบันทึกจังหวะเป็น 10 ครั้ง และปรับปรุงการจัดการ Timeout ให้มีความแม่นยำ ปราศจากการสะสมจังหวะตกค้างเมื่อสั่งหยุดครับ")
