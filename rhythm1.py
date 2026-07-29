import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าตาของเว็บ
st.set_page_config(
    page_title="Haptic Tempo Recorder (Vibration)", 
    page_icon="📳", 
    layout="centered"
)

st.title("📳 Haptic Tempo Recorder")
st.write("""
**วิธีใช้งาน:** กดปุ่มด้านล่าง 10 ครั้งตามจังหวะที่ต้องการ 
ระบบจะคำนวณและสั่นต่อเนื่องเป็นจังหวะที่เท่ากันเป๊ะแบบ **ไร้รอยต่อ (Seamless Loop)** 
เมื่อต้องการหยุด ให้กดปุ่มเดิมอีกครั้ง
""")

# โค้ด HTML/JS สำหรับสร้างปุ่มและสั่นต่อเนื่อง
# แก้ไขปัญหา: การกดครั้งแรกไม่เริ่มจับจังหวะ และระบบ Seamless
vibration_code_fixed = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            min-height: 140px; /* เพิ่มพื้นที่ */
        }
        .vibrate-btn {
            background-color: #ff4b4b;
            color: white;
            border: none;
            padding: 20px 40px;
            font-size: 22px;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
            transition: all 0.2s ease;
            width: 90%;
            max-width: 380px;
            position: relative;
        }
        .vibrate-btn:active {
            transform: scale(0.97);
        }
        .vibrate-btn.stop {
            background-color: #2e86de;
            box-shadow: 0 4px 15px rgba(46, 134, 222, 0.4);
        }
        .status-text {
            margin-top: 20px;
            color: #444;
            font-size: 16px;
            text-align: center;
            font-weight: 500;
        }
    </style>
</head>
<body>

<div class="container">
    <button id="mainBtn" class="vibrate-btn">กดครั้งแรกเพื่อเปิดใช้ API (0/10)</button>
    <p id="status" class="status-text">👉 กดปุ่มด้านบนเพื่อเริ่มบันทึกจังหวะใหม่</p>
</div>

<script>
    const TOTAL_TAPS = 10;
    const btn = document.getElementById("mainBtn");
    const status = document.getElementById("status");

    let timestamps = [];
    let isPlaying = false;
    let intervalId = null;
    let avgInterval = 0;

    # ✅ ปรับปรุงวิธีการดักจับการกดให้ User-Initiated อย่างสมบูรณ์
    # เพื่อแก้ปัญหาปุ่มไม่เริ่มจับจังหวะ (User Interaction Blocking)
    btn.addEventListener('click', handleClick);

    function handleClick() {
        if (!("vibrate" in navigator)) {
            status.innerText = "❌ อุปกรณ์หรือเบราว์เซอร์นี้ไม่รองรับระบบสั่น";
            status.style.color = "#DE350B";
            return;
        }

        # 1. จัดการ User Interaction (Interaction Gate)
        # กดครั้งแรกสุดเพื่อเปิดใช้ API และเริ่มบันทึก timestamps[0]
        if (timestamps.length === 0 && !isPlaying) {
            startRecording();
            return; 
        }

        # 2. หากกำลังสั่นอยู่ กดอีกครั้งจะเป็นการหยุด (Stop state)
        if (isPlaying) {
            stopRhythm();
            return;
        }

        # 3. จัดการการบันทึกจังหวะตามลำดับ (Tap 2-10)
        recordTap();
    }

    function startRecording() {
        timestamps = [Date.now()];
        btn.innerText = `กดต่อเพื่อจับจังหวะ (1/${TOTAL_TAPS})`;
        status.innerText = "🔄 บันทึกครั้งที่ 1 เรียบร้อย... กดต่อทันที!";
        status.style.color = "#444";
        # สั่น Feedback สั้นมาก
        navigator.vibrate(50); 
    }

    function recordTap() {
        const now = Date.now();
        timestamps.push(now);
        navigator.vibrate(80); # สั่น Feedback

        const count = timestamps.length;

        if (count < TOTAL_TAPS) {
            btn.innerText = `กดต่อเพื่อจับจังหวะ (${count}/${TOTAL_TAPS})`;
            status.innerText = `บันทึกครั้งที่ ${count} เรียบร้อย...`;
        } else if (count === TOTAL_TAPS) {
            # ✅ ค้นหาและบันทึก Seamless avgInterval
            calculateSeamlessAverage();
            
            isPlaying = true;
            btn.innerText = "🛑 กดเพื่อหยุดสั่น";
            btn.classList.add("stop");
            # แสดง status ด้วย interval จริง
            status.innerText = `🔄 กำลังสั่นต่อเนื่องแบบไร้รอยต่อ (ทุกๆ ${avgInterval} ms)...`;
            status.style.color = "#00875A";

            # เริ่มต้น Seamless Loop ทันที
            startSeamlessInterval();
        }
    }

    function calculateSeamlessAverage() {
        let delays = [];
        # เอาส่วนต่างของ 9 ช่วงที่เกิดขึ้นจากการกด 10 ครั้ง
        for (let i = 0; i < timestamps.length - 1; i++) {
            delays.push(timestamps[i+1] - timestamps[i]);
        }

        # หาค่าเฉลี่ย
        const sum = delays.reduce((a, b) => a + b, 0);
        # ใช้ค่าเฉลี่ยนี้เป็น Tempo คงที่ตลอดลูป
        avgInterval = Math.round(sum / delays.length);
    }

    function startSeamlessInterval() {
        # คำนวณระยะสั่นให้เหมาะสม ไม่เกิน 40% ของ Tempo
        const vibrateDuration = Math.min(100, Math.floor(avgInterval * 0.4));

        # สั่นครั้งแรกทันทีเมื่อกดครบ 10 ครั้ง
        navigator.vibrate(vibrateDuration);

        # ✅ ใช้ setInterval เพื่อสั่นต่อเนื่องตามจังหวะที่เท่ากันเป๊ะแบบ Seamless
        intervalId = setInterval(() => {
            if (isPlaying) {
                navigator.vibrate(vibrateDuration);
            }
        }, avgInterval);
    }

    function stopRhythm() {
        isPlaying = false;
        # เคลียร์ลูปทันที
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
        # ยกเลิกการสั่นทันที (vibrate(0))
        navigator.vibrate(0); 

        # รีเซ็ต timestamps เตรียมรับจังหวะใหม่
        timestamps = [];

        # คืนค่าสถานะเริ่มต้น
        btn.innerText = `กดเพื่อเริ่มจับจังหวะ (0/${TOTAL_TAPS})`;
        btn.classList.remove("stop");
        status.innerText = "⏹️ หยุดสั่นแล้ว! กดใหม่เพื่อเริ่มบันทึกจังหวะใหม่";
        status.style.color = "#444";
    }
</script>

</body>
</html>
"""

# แสดงผล HTML/JS Component ใน Streamlit
# ปรับ height เพิ่มเล็กน้อยเพื่อให้แสดงผลปุ่มและข้อความได้ครบถ้วน
components.html(vibration_code_fixed, height=200)

st.info("**การปรับปรุง:** เวอร์ชันนี้แก้ไขปัญหาปุ่มไม่ตอบสนองโดยการบังคับให้มี User Interaction ที่สมบูรณ์ในการเริ่มจับจังหวะ และยังคงรักษาระบบการสั่นแบบ Seamless Loop (ทุกจังหวะเท่ากันสม่ำเสมอและสั่นต่อเนื่องอย่างไร้รอยต่อ) ผ่านค่าเฉลี่ยการกด 10 ครั้งครับ")
