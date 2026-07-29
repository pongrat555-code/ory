import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Rhythm Vibration App", page_icon="📳", layout="centered")

st.title("📳 Rhythm Vibration Loop")
st.write("กดปุ่มให้ครบ 5 ครั้งตามจังหวะที่ต้องการ ระบบจะสั่นวนลูปตามจังหวะนั้นจนกว่าจะสั่งหยุด")

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
            max-width: 320px;
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
        .progress {
            margin-top: 8px;
            font-size: 13px;
            color: #888;
        }
    </style>
</head>
<body>

<div class="container">
    <button id="mainBtn" class="vibrate-btn" onclick="handleClick()">กดเพื่อเริ่มจับจังหวะ (0/5)</button>
    <p id="status" class="status-text">พร้อมบันทึกจังหวะการกด</p>
</div>

<script>
    let timestamps = [];
    let delays = [];
    let isPlaying = false;
    let loopTimeout = null;
    let currentStep = 0;

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
        
        // สั่นสั้นๆ 100ms ทุกครั้งที่กด เพื่อส่ง Haptic Feedback บอกว่ารับค่าแล้ว
        navigator.vibrate(100);

        const count = timestamps.length;
        const btn = document.getElementById("mainBtn");
        const status = document.getElementById("status");

        if (count < 5) {
            btn.innerText = `กดต่อเพื่อจับจังหวะ (${count}/5)`;
            status.innerText = `บันทึกครั้งที่ ${count} เรียบร้อย...`;
        } else if (count === 5) {
            // คำนวณช่วงเวลาห่าง (Delays) ระหว่างการกดแต่ละครั้ง
            delays = [];
            for (let i = 0; i < timestamps.length - 1; i++) {
                delays.push(timestamps[i+1] - timestamps[i]);
            }

            // คำนวณเวลารวมของ 1 ลูป (สำหรับเว้นระยะก่อนเริ่มลูปใหม่)
            // กำหนดให้ช่วงเว้นระหว่างรอบเท่ากับระยะเวลารวม หรือขั้นต่ำ 1000ms
            const totalCycleTime = Math.max(
                delays.reduce((a, b) => a + b, 0), 
                1000
            );

            isPlaying = true;
            btn.innerText = "🛑 กดอีกครั้งเพื่อหยุดสั่น";
            btn.classList.add("stop");
            status.innerText = "🔄 กำลังสั่นวนลูปตามจังหวะของคุณ...";
            status.style.color = "#00875A";

            // เริ่มเล่นลูปสั่นตามจังหวะ
            playRhythmSequence(totalCycleTime);
        }
    }

    function playRhythmSequence(totalCycleTime) {
        if (!isPlaying) return;

        // สั่นครั้งแรกทันที
        navigator.vibrate(120);

        // ตั้งเวลาสั่นตามระยะห่างของแต่ละคลิกที่บันทึกไว้
        let cumulativeTime = 0;
        for (let i = 0; i < delays.length; i++) {
            cumulativeTime += delays[i];
            setTimeout(() => {
                if (isPlaying) {
                    navigator.vibrate(120); // สั่นยาว 120ms ทุกโน้ต
                }
            }, cumulativeTime);
        }

        // เมื่อจบ 1 รอบ ให้เริ่มรอบใหม่ตามเวลา totalCycleTime
        loopTimeout = setTimeout(() => {
            if (isPlaying) {
                playRhythmSequence(totalCycleTime);
            }
        }, cumulativeTime + 800); // แถมระยะเว้นท้ายลูป 0.8 วินาทีให้จังหวะไม่อึดอัด
    }

    function stopRhythm() {
        isPlaying = false;
        clearTimeout(loopTimeout);
        navigator.vibrate(0); // สั่งยกเลิกการสั่นทันที

        // รีเซ็ตค่าเพื่อเตรียมจับจังหวะใหม่
        timestamps = [];
        delays = [];

        const btn = document.getElementById("mainBtn");
        const status = document.getElementById("status");

        btn.innerText = "กดเพื่อเริ่มจับจังหวะ (0/5)";
        btn.classList.remove("stop");
        status.innerText = "⏹️ หยุดสั่นแล้ว! กดใหม่เพื่อเริ่มบันทึกจังหวะใหม่";
        status.style.color = "#555";
    }
</script>

</body>
</html>
"""

components.html(vibration_code, height=180)

st.info("**การทำงาน:** ระบบจะบันทึก Timestamp จากการกด 5 ครั้ง นำมาลบกันเพื่อหาค่า Delay ระหว่างคลิก จากนั้นใช้ Recursive Timeout เล่นการสั่นซ้ำวนไปเรื่อยๆ จนกว่าผู้ใช้จะกดปุ่มเพื่อหยุดครับ")
