import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Vibration & Flashlight Loop", page_icon="📳", layout="centered")

st.title("📳 เคาะจังหวะ")
st.write("กดปุ่มด้านล่าง 5 ครั้งตามจังหวะเพลง")

# โค้ด HTML/JS แบบจัดการทั้ง Vibration API และ WebRTC Torch API
custom_vibration_flash_component = """
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

<div id="countDisplay" class="counter">0 / 5</div>
<button id="vibBtn" class="vibrate-btn">กดเพื่อเริ่มจับจังหวะ</button>
<div id="statusText" class="status">พร้อมบันทึกจังหวะ (ต้องอนุญาตสิทธิ์กล้องเพื่อเปิดแฟลช)</div>

<script>
    const TOTAL_TAPS = 5;
    let timestamps = [];
    let isPlaying = false;
    let intervalId = null;

    // ตัวแปรจัดการ Flashlight
    let imageTrack = null;

    const btn = document.getElementById("vibBtn");
    const countDisplay = document.getElementById("countDisplay");
    const statusText = document.getElementById("statusText");

    // ฟังก์ชันเตรียมเชื่อมต่อกล้องหลังเพื่อคุมไฟแฟลช
    async function initFlashlight() {
        if (imageTrack) return true;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" }
            });
            const track = stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities ? track.getCapabilities() : {};
            
            if (capabilities.torch) {
                imageTrack = track;
                return true;
            } else {
                statusText.innerText = "⚠️ อุปกรณ์รองรับการสั่น แต่ไม่รองรับไฟแฟลชผ่านเว็บ";
                return false;
            }
        } catch (err) {
            console.log("Flashlight permission denied or not supported:", err);
            statusText.innerText = "⚠️ ไม่ได้รับสิทธิ์ใช้งานกล้อง (สั่นได้อย่างเดียว)";
            return false;
        }
    }

    // ฟังก์ชันสั่งเปิด/ปิดแฟลชตามระยะเวลา (ms)
    function triggerFlash(durationMs) {
        if (!imageTrack) return;
        try {
            imageTrack.applyConstraints({ advanced: [{ torch: true }] });
            setTimeout(() => {
                if (imageTrack) {
                    imageTrack.applyConstraints({ advanced: [{ torch: false }] });
                }
            }, durationMs);
        } catch (e) {
            console.log("Flash error:", e);
        }
    }

    // รับ event pointerdown กดปุ่ม
    btn.addEventListener("pointerdown", async function(e) {
        e.preventDefault();

        // กดครั้งแรกสุด ขอสิทธิ์เปิดไฟแฟลช
        if (timestamps.length === 0 && !isPlaying) {
            await initFlashlight();
        }

        // 1. ถ้ากำลังสั่นอยู่ ให้กดเพื่อหยุด
        if (isPlaying) {
            stopVibrationAndFlash();
            return;
        }

        // 2. บันทึกจังหวะการกด
        timestamps.push(Date.now());
        
        // สั่น + เปิดไฟแฟลชสั้นๆ ทันทีที่กดปุ่ม
        try { if ("vibrate" in navigator) navigator.vibrate(60); } catch(err) {}
        triggerFlash(60);

        const currentCount = timestamps.length;
        countDisplay.innerText = currentCount + " / " + TOTAL_TAPS;

        if (currentCount < TOTAL_TAPS) {
            btn.innerText = "กดต่อเพื่อจับจังหวะ";
            statusText.innerText = "บันทึกครั้งที่ " + currentCount + " เรียบร้อย...";
        } else if (currentCount === TOTAL_TAPS) {
            // 3. บันทึกครบ 10 ครั้ง -> เริ่มลูป Seamless
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
        btn.innerText = "🛑 กดอีกครั้งเพื่อหยุด";
        btn.classList.add("stop-mode");
        countDisplay.innerText = "RUNNING";
        countDisplay.style.color = "#1f77b4";
        statusText.innerText = "🔄 จังหวะของคุณ (" + avgInterval + " ms/ครั้ง)";
        statusText.style.color = "#00875A";

        // ระยะเวลาสั่นและเปิดไฟแฟลชในแต่ละโน้ต
        const actionDuration = Math.min(100, Math.floor(avgInterval * 0.4));

        // ทำการสั่น + เปิดแฟลชโน้ตแรกทันที
        try { if ("vibrate" in navigator) navigator.vibrate(actionDuration); } catch(err) {}
        triggerFlash(actionDuration);

        // วนลูปทำงานคู่กันตามจังหวะเฉลี่ย
        intervalId = setInterval(function() {
            if (isPlaying) {
                try { if ("vibrate" in navigator) navigator.vibrate(actionDuration); } catch(err) {}
                triggerFlash(actionDuration);
            }
        }, avgInterval);
    }

    function stopVibrationAndFlash() {
        isPlaying = false;
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }

        // สั่งปิดสั่นและปิดแฟลชทันที
        try { if ("vibrate" in navigator) navigator.vibrate(0); } catch(err) {}
        if (imageTrack) {
            try { imageTrack.applyConstraints({ advanced: [{ torch: false }] }); } catch(e) {}
        }

        timestamps = [];
        btn.innerText = "กดเพื่อเริ่มจับจังหวะ";
        btn.classList.remove("stop-mode");
        countDisplay.innerText = "0 / " + TOTAL_TAPS;
        countDisplay.style.color = "#ff4b4b";
        statusText.innerText = "⏹️ หยุดเรียบร้อย! กดใหม่เพื่อเริ่มอีกครั้ง";
        statusText.style.color = "#555";
    }
</script>

</body>
</html>
"""

components.html(custom_vibration_flash_component, height=220)

st.info("💡 **คำแนะนำเพิ่มเติม:**\n1. เมื่อกดปุ่มครั้งแรก เบราว์เซอร์จะขึ้นป๊อปอัปขออนุญาตใช้กล้องถ่ายรูป **ต้องกด Allow (อนุญาต)** เพื่อให้เปิดไฟแฟลชได้\n2. ต้องรันผ่าน **HTTPS** (เช่น Streamlit Community Cloud) เท่านั้น เบราว์เซอร์ถึงจะยอมให้เปิดใช้งานไฟแฟลชครับ")
