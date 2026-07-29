import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าตาของเว็บ
st.set_page_config(page_title="Vibration App", page_icon="📳", layout="centered")

st.title("📳 Haptic Feedback WebApp")
st.write("แอปพลิเคชันทดสอบระบบสั่นบนมือถือด้วย Streamlit")

# โค้ด HTML + JavaScript สำหรับสร้างปุ่มและเรียกใช้ Vibration API
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
            padding: 16px 32px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
            transition: all 0.2s ease;
            width: 80%;
            max-width: 300px;
        }
        .vibrate-btn:active {
            transform: scale(0.95);
            background-color: #e03e3e;
        }
        .status-text {
            margin-top: 15px;
            color: #555;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="container">
    <button class="vibrate-btn" onclick="triggerVibration()">กดเพื่อให้โทรศัพท์สั่น!</button>
    <p id="status" class="status-text"></p>
</div>

<script>
    function triggerVibration() {
        var statusElement = document.getElementById("status");
        
        // ตรวจสอบว่าเบราว์เซอร์รองรับ Vibration API หรือไม่
        if ("vibrate" in navigator) {
            // รูปแบบการสั่น: [สั่น 200ms, หยุด 100ms, สั่น 200ms]
            navigator.vibrate([200, 100, 200]);
            statusElement.innerText = "⚡ ส่งสัญญาณสั่นแล้ว!";
            statusElement.style.color = "#00875A";
        } else {
            statusElement.innerText = "❌ อุปกรณ์หรือเบราว์เซอร์นี้ไม่รองรับระบบสั่น";
            statusElement.style.color = "#DE350B";
        }
    }
</script>

</body>
</html>
"""

# แสดงผล HTML/JS Component บนหน้า Streamlit
components.html(vibration_code, height=160)

st.info("**หมายเหตุ:** ระบบสั่นรองรับการทำงานบน **Android** ผ่าน Chrome/Firefox/Edge เป็นหลัก (iOS/iPhone จะไม่รองรับเนื่องจากข้อจำกัดด้านความปลอดภัยของ Safari)")
