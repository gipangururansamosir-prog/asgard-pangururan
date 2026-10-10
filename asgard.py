import base64
import os
import urllib.parse
from datetime import datetime
import streamlit as st
from PIL import Image
from google import genai

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="ASGARD - GI 150kV Pangururan", 
    page_icon="⚡",
    layout="centered"
)

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "teks_laporan" not in st.session_state:
    st.session_state.teks_laporan = ""

if "auto_detected_leds" not in st.session_state:
    st.session_state.auto_detected_leds = []

def set_page(page_name):
    st.session_state.page = page_name

# ==============================================================================
# 2. INISIALISASI GEMINI CLIENT (AI AUTO READER)
# ==============================================================================
try:
    client = genai.Client(api_key="ISI_API_KEY_GEMINI_ANDA")
except Exception:
    client = None

def detect_led_from_image(image, daftar_led_ref):
    if not client:
        st.error("API Key Gemini belum dikonfigurasi.")
        return []
        
    prompt = (
        "Kamu adalah sistem AI insinyur proteksi Gardu Induk. "
        "Analisis foto panel relay Distance/Annunciator ini.\n"
        "Tugasmu: Identifikasi semua teks LED indikator yang sedang MENYALA / ACTIVE.\n"
        "PILIH HANYA dari daftar referensi LED resmi berikut ini:\n"
        + str(daftar_led_ref) + "\n"
        "Format Output: Keluarkan HASILNYA SAJA berupa teks dipisahkan koma. Contoh: TRIP, ZONE 1 OP\nJika tidak ada: NONE"
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt]
        )
        raw_text = response.text.strip()
        if "NONE" in raw_text or not raw_text:
            return []
        return [item.strip() for item in raw_text.split(",") if item.strip() in daftar_led_ref]
    except Exception as e:
        st.error(f"Gagal melakukan pembacaan AI: {e}")
        return []

# ==============================================================================
# 3. DAFTAR LED ANNUNCIATOR
# ==============================================================================
DAFTAR_LED = [
    "IN SERVICE", "TROUBLE", "TEST MODE", "TRIP", "ALARM", "PICKUP", 
    "VOLTAGE", "CURRENT", "FREQUENCY", "OTHER", "PHASE A", "PHASE B", "PHASE C", "NEUTRAL / GROUND",
    "CB CLOSE", "CB PHASE R OPEN", "CB PHASE S OPEN", "CB PHASE T OPEN", "POTT ECHO ON", "POWER SWING BLOCK", 
    "LINE PICKUP OP", "TRIP 1-POLE", "TRIP 3-POLE", "BREAKER FAIL", "MANUAL CLOSE", "DISTANCE OP", "ZONE 1 OP", 
    "ZONE 2 OP", "ZONE 3 OP", "ZONE 4 OP", "PUTT OP", "AIDED DEF OP", "CR SEND POTT ECHO", "CR SEND DIST", 
    "CR RECV DIST/POTT", "PLC ALARM/TROUBLE", "AR BLOCK", "AR ENABLED", "AR DISABLED", "CB AR LOCKOUT", 
    "AR LOCKOUT", "AR IN PROGRESS", "AR SUCCESS", "SYNCRON ON", "CR SEND DEF", "CR RECV DEF", "VT LINE FAIL", 
    "VT BUS FAIL", "AR NOT READY", "BACKUP PROT FAIL", "TCS 1 PHASE R FAIL", "TCS 1 PHASE S FAIL", 
    "TCS 1 PHASE T FAIL", "TCS 2 PHASE R FAIL", "TCS 2 PHASE S FAIL", "TCS 2 PHASE T FAIL", "PRI ETHERNET FAIL", 
    "SEC ETHERNET FAIL", "SNTP FAILURE"
]

# ==============================================================================
# 4. PENCARIAN OTOMATIS FILE LOGO / BACKGROUND
# ==============================================================================
logo_path = ""
extensions = ["png", "jpg", "jpeg", "webp"]

for ext in extensions:
    paths_to_check = [f"F:\\logo.{ext}", f"F:\\LOGO\\logo.{ext}", f"logo.{ext}"]
    for p in paths_to_check:
        if os.path.exists(p):
            logo_path = p
            break
    if logo_path:
        break

def get_b64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

img_b64 = get_b64(logo_path)

if img_b64:
    st.markdown(
        f'<style>'
        f'.stApp {{ background: linear-gradient(rgba(11,25,44,0.88), rgba(11,25,44,0.88)), url("data:image/png;base64,{img_b64}") no-repeat center center fixed !important; background-size: contain !important; color: #ffffff; }}'
        f'</style>',
        unsafe_allow_html=True
    )
else:
    st.markdown('<style>.stApp { background-color: #0b192c; color: #ffffff; }</style>', unsafe_allow_html=True)

st.markdown(
    '<style>'
    '.user-card { background: linear-gradient(135deg, rgba(0,82,204,0.95) 0%, rgba(0,51,128,0.95) 100%); border: 2px solid #ffc107; border-radius: 16px; padding: 16px; margin-bottom: 20px; }'
    '.status-badge { background-color: #ffc107; color: #000000; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 12px; float: right; }'
    'div.stButton > button { border-radius: 12px !important; font-weight: bold !important; width: 100% !important; height: 55px !important; margin-bottom: 6px !important; background-color: rgba(15,23,42,0.85) !important; color: #ffffff !important; border: 1px solid #0052cc !important; }'
    'div.stButton > button:hover { border-color: #ffc107 !important; background-color: #0052cc !important; }'
    '</style>', 
    unsafe_allow_html=True
)

# ==============================================================================
# HALAMAN 1: DASHBOARD UTAMA
# ==============================================================================
if st.session_state.page == "dashboard":
    if logo_path and os.path.exists(logo_path):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(logo_path, use_container_width=True)

    st.markdown(
        '<div class="user-card">'
        '<span class="status-badge">● Online</span>'
        '<div style="font-size: 18px; font-weight: bold;">Gardu Induk 150kV Pangururan</div>'
        '<hr style="border-color: #ffc107; margin: 10px 0;">'
        '<div style="display: flex; justify-content: space-between; font-size: 13px;">'
        '<div>⚡ <b>2 Line 150kV</b><br><small>PGRUN - TELE</small></div>'
        '<div>🔌 <b>Trafo 30 MVA</b><br><small>1 Incoming</small></div>'
        '<div>📡 <b>2 Feeder</b><br><small>DT 1 & DT 2</small></div>'
        '</div>'
        '</div>', 
        unsafe_allow_html=True
    )

    st.subheader("Menu Utama")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚨 Pelaporan Gangguan", key="btn_pht"):
            set_page("lapor_gangguan")
            st.rerun()
        if st.button("⚡ Status Gardu", key="btn_gardu"):
            st.info("Fitur Status Gardu")
        if st.button("📊 Data Anomali", key="btn_anomali"):
            st.info("Fitur Data Anomali")

    with col2:
        if st.button("🎯 Thermovisi", key="btn_thermo"):
            st.info("Fitur Thermovisi")
        if st.button("🛡️ K3 Score", key="btn_k3"):
            st.info("Fitur K3 Score")
        if st.button("📹 CCTV K3", key="btn_cctv"):
            st.info("Fitur CCTV K3")

    with col3:
        if st.button("🔀 Prosedur Manuver", key="btn_manuver"):
            st.info("Fitur Prosedur Manuver")
        if st.button("🔔 Notifikasi", key="btn_noti"):
            st.info("Fitur Notifikasi")
        if st.button("🗄️ Database Peralatan", key="btn_db"):
            st.info("Fitur Database Peralatan")

# ==============================================================================
# HALAMAN 2: FORM PELAPORAN GANGGUAN
# ==============================================================================
elif st.session_state.page == "lapor_gangguan":
    if st.button("← Kembali ke Dashboard", key="btn_back"):
        set_page("dashboard")
        st.rerun()
        
    st.title("⚡ Form Pelaporan Gangguan GI PANGURURAN 150 kV")
    st.caption("Isi form di bawah ini untuk mengenerate format laporan otomatis.")
    st.warning("⚠️ **PASTIKAN ANDA SUDAH FOTO RELAY TERLEBIH DAHULU**")

    st.subheader("📸 Auto Reader Foto Relay (Scan AI)")
    foto_upload = st.file_uploader("Upload Foto Relay", type=["jpg", "png", "jpeg"], key="upl_relay")
    foto_kamera = st.camera_input("Ambil Foto dari Kamera", key="cam_relay")
    
    foto_terpilih = foto_kamera if foto_kamera else foto_upload
    if foto_terpilih:
        img = Image.open(foto_terpilih)
        st.image(img, caption="Pratinjau Foto Relay", width=250)
        if st.button("🤖 Jalankan AI Scan LED", key="btn_ai"):
            with st.spinner("AI Menganalisis LED..."):
                detected = detect_led_from_image(img, DAFTAR_LED)
                st.session_state.auto_detected_leds = detected
                if detected:
                    st.success(f"✅ AI Mendeteksi LED: {', '.join(detected)}")
                else:
                    st.warning("⚠️ LED tidak terdeteksi.")

    st.divider()

    with st.form("form_gangguan", clear_on_submit=False):
        st.subheader("📌 Informasi Umum")
        col0, col1, col2 = st.columns(3)
        with col0:
            tanggal = st.date_input("Tanggal", value=datetime.now())
        with col1:
            jam = st.text_input("Jam (WIB)", value="", placeholder="Contoh: 20:35")
            gi = st.text_input("Gardu Induk (GI)", value="", placeholder="Contoh: Pangururan")
        with col2:
            bay_pht = st.selectbox("Bay Penghantar (PHT)", ["-- Pilih Bay PHT --", "PGRUN - TELE #1", "PGRUN - TELE #2"])
            kondisi = st.selectbox("Kondisi", ["-- Pilih Kondisi --", "AR SUCCES", "TRIP / UNSUCCESS", "MANUAL TRIP"])

        st.subheader("📋 Annunciator & Parameter Relay")
        led_terpilih = st.multiselect(
            "Pilih LED Annunciator yang Menyala / Active:",
            options=DAFTAR_LED,
            default=st.session_state.auto_detected_leds,
            placeholder="Ketik atau pilih LED..."
        )
        
        col3, col4, col5 = st.columns(3)
        with col3:
            zone = st.text_input("Zone", value="", placeholder="Contoh: 4")
        with col4:
            jarak = st.text_input("Jarak (KM)", value="", placeholder="Contoh: 66.7")
        with col5:
            cuaca = st.text_input("Cuaca", value="", placeholder="Contoh: HUJAN PETIR")

        st.subheader("⚡ Beban Sebelum Gangguan")
        col6, col7, col8, col9 = st.columns(4)
        with col6:
            mw = st.text_input("MW", value="")
        with col7:
            mvar = st.text_input("MVar", value="")
        with col8:
            i_amp = st.text_input("I (A)", value="")
        with col9:
            e_kv = st.text_input("E (kV)", value="")

        st.subheader("🔢 Counter Meter LA")
        col_la_seb_r, col_la_seb_s, col_la_seb_t = st.columns(3)
        with col_la_seb_r:
            la_seb_r = st.text_input("R (Sebelum)", value="")
        with col_la_seb_s:
            la_seb_s = st.text_input("S (Sebelum)", value="")
        with col_la_seb_t:
            la_seb_t = st.text_input("T (Sebelum)", value="")

        col_la_ses_r, col_la_ses_s, col_la_ses_t = st.columns(3)
        with col_la_ses_r:
            la_ses_r = st.text_input("R (Sesudah)", value="")
        with col_la_ses_s:
            la_ses_s = st.text_input("S (Sesudah)", value="")
        with col_la_ses_t:
            la_ses_t = st.text_input("T (Sesudah)", value="")

        st.subheader("🔢 Counter Meter PMT")
        col_pmt_seb_r, col_pmt_seb_s, col_pmt_seb_t = st.columns(3)
        with col_pmt_seb_r:
            pmt_seb_r = st.text_input("PMT R (Sebelum)", value="")
        with col_pmt_seb_s:
            pmt_seb_s = st.text_input("PMT S (Sebelum)", value="")
        with col_pmt_seb_t:
            pmt_seb_t = st.text_input("PMT T (Sebelum)", value="")

        col_pmt_ses_r, col_pmt_ses_s, col_pmt_ses_t = st.columns(3)
        with col_pmt_ses_r:
            pmt_ses_r = st.text_input("PMT R (Sesudah)", value="")
        with col_pmt_ses_s:
            pmt_ses_s = st.text_input("PMT S (Sesudah)", value="")
        with col_pmt_ses_t:
            pmt_ses_t = st.text_input("PMT T (Sesudah)", value="")

        st.subheader("👤 Petugas")
        col12, col13 = st.columns(2)
        with col12:
            operator = st.selectbox("Operator", ["-- Pilih Operator --", "DANI LUMBAN RAJA", "DARIMAN BOIMO SOLIN", "IMAM RIZKY SIREGAR", "LEO NAINGGOLAN"])
        with col13:
            upb = st.text_input("UPB", value="")

        submitted = st.form_submit_button("Generate Format Laporan", type="primary")

    if submitted:
        bay_pht_teks = "" if bay_pht == "-- Pilih Bay PHT --" else bay_pht
        kondisi_teks = "" if kondisi == "-- Pilih Kondisi --" else kondisi
        operator_teks = "" if operator == "-- Pilih Operator --" else operator
        tgl_formatted = tanggal.strftime("%d-%m-%Y")

        annunciator_formatted = "\n".join([f"- {led}" for led in led_terpilih]) if led_terpilih else "-"

        st.session_state.teks_laporan = (
            f"*INFO Gangguan bay PHT {bay_pht_teks.upper()}*\n\n"
            f"_Tanggal_ : *{tgl_formatted}*\n"
            f"_Jam_ :  *{jam}* _WIB_\n"
            f"GI : *{gi}*\n"
            f"Gangguan By PHT {bay_pht_teks.upper()}: \n"
            f"Kondisi : {kondisi_teks}\n"
            f"Annunciator\n{annunciator_formatted}\n"
            f"Zone : {zone}\n"
            f"Jarak : {jarak} KM\n"
            f"Cuaca = {cuaca.upper()}\n\n"
            f" Beban sebelum  : \n"
            f" Mw : {mw}\n"
            f" Mvar : {mvar}\n"
            f" I : {i_amp} A\n"
            f" E : {e_kv}\n \n"
            f"Counter LA sebelum : R={la_seb_r} | S={la_seb_s} | T={la_seb_t}\n"
            f"Counter LA sesudah : R={la_ses_r} | S={la_ses_s} | T={la_ses_t}\n\n"
            f"Counter PMT sebelum : R={pmt_seb_r} | S={pmt_seb_s} | T={pmt_seb_t}\n"
            f"Counter PMT sesudah   : R={pmt_ses_r} | S={pmt_ses_s} | T={pmt_ses_t}\n\n"
            f"Operator : {operator_teks.upper()}\n"
            f"Upb : {upb.upper()}\n\n"
            f"_Terimakasih_"
        )

    if st.session_state.teks_laporan:
        st.success("Laporan Berhasil Dibuat!")
        st.code(st.session_state.teks_laporan, language="markdown")
        teks_encoded = urllib.parse.quote(st.session_state.teks_laporan)
        url_wa = f"https://api.whatsapp.com/send?text={teks_encoded}"
        st.markdown(f'<a href="{url_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:8px;font-weight:bold;text-align:center;">📲 Kirim Langsung ke WhatsApp</div></a>', unsafe_allow_html=True)

else:
    set_page("dashboard")
    st.rerun()
