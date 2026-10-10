import base64
import os
import urllib.parse
from datetime import datetime
import streamlit as st
from PIL import Image
from google import genai

# ==============================================================================
# 1. KONFIGURASI HALAMAN & STATE
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

# Mock parameter nilai kesehatan untuk simulasi Health Index
if "health_params" not in st.session_state:
    st.session_state.health_params = {
        "thermo_score": 92,
        "gangguan_score": 85,
        "anomali_score": 90,
        "k3_score": 95
    }

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==============================================================================
# 2. STYLING GLOBAL (CSS)
# ==============================================================================
st.markdown(
    '<style>'
    '.user-card { background: linear-gradient(135deg, rgba(0,82,204,0.95) 0%, rgba(0,51,128,0.95) 100%); border: 2px solid #ffc107; border-radius: 16px; padding: 16px; margin-bottom: 20px; color: white; }'
    '.health-card { background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(30,41,59,0.95) 100%); border: 2px solid #10b981; border-radius: 16px; padding: 16px; margin-bottom: 20px; color: white; }'
    '.status-badge { background-color: #ffc107; color: #000000; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 12px; float: right; }'
    '.health-badge { background-color: #10b981; color: #ffffff; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 12px; float: right; }'
    'div.stButton > button { border-radius: 12px !important; font-weight: bold !important; width: 100% !important; height: 55px !important; margin-bottom: 6px !important; background-color: rgba(15,23,42,0.85) !important; color: #ffffff !important; border: 1px solid #0052cc !important; }'
    'div.stButton > button:hover { border-color: #ffc107 !important; background-color: #0052cc !important; }'
    '</style>', 
    unsafe_allow_html=True
)

# ==============================================================================
# 3. MODUL HALAMAN (PENGISIAN MENU & HEALTH INDEX)
# ==============================================================================

def render_dashboard():
    # Hitung rata-rata Health Index dari berbagai parameter
    hp = st.session_state.health_params
    avg_health = int((hp["thermo_score"] + hp["gangguan_score"] + hp["anomali_score"] + hp["k3_score"]) / 4)

    # Card Health Index Score Utama
    st.markdown(
        f'<div class="health-card">'
        f'<span class="health-badge">Indeks: {avg_health}% (SEHAT)</span>'
        f'<div style="font-size: 18px; font-weight: bold;">🎯 Equipment Health Index Score</div>'
        f'<hr style="border-color: #10b981; margin: 10px 0;">'
        f'<div style="display: flex; justify-content: space-between; font-size: 13px;">'
        f'<div>🔥 Thermovisi: <b>{hp["thermo_score"]}%</b></div>'
        f'<div>🚨 Pelaporan: <b>{hp["gangguan_score"]}%</b></div>'
        f'<div>📊 Anomali: <b>{hp["anomali_score"]}%</b></div>'
        f'<div>🛡️ K3: <b>{hp["k3_score"]}%</b></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Header Card Status Gardu
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
        if st.button("🚨 Pelaporan Gangguan"):
            navigate_to("lapor_gangguan")
        if st.button("⚡ Status Gardu"):
            navigate_to("status_gardu")
        if st.button("📊 Data Anomali"):
            navigate_to("data_anomali")

    with col2:
        if st.button("🎯 Thermovisi"):
            navigate_to("thermovisi")
        if st.button("🛡️ K3 Score"):
            navigate_to("k3_score")
        if st.button("📹 CCTV K3"):
            navigate_to("cctv_k3")

    with col3:
        if st.button("🔀 Prosedur Manuver"):
            navigate_to("prosedur_manuver")
        if st.button("🔔 Notifikasi"):
            navigate_to("notifikasi")
        if st.button("🗄️ Database Peralatan"):
            navigate_to("database_peralatan")


def render_status_gardu():
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.title("⚡ Status Gardu Induk")
    st.info("Fitur pemantauan status trafo dan penghantar secara real-time.")


def render_thermovisi():
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.title("🎯 Data Thermovisi & Penyesuaian Score")
    st.info("Setiap input suhu termal baru akan otomatis memperbarui parameter Health Index di dashboard.")
    
    new_val = st.slider("Simulasi Skor Thermovisi", 0, 100, st.session_state.health_params["thermo_score"])
    if st.button("Simpan Skor Thermovisi"):
        st.session_state.health_params["thermo_score"] = new_val
        st.success("Skor berhasil diperbarui! Silakan kembali ke dashboard.")


# ==============================================================================
# 4. ROUTER UTAMA APLIKASI
# ==============================================================================
if st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "status_gardu":
    render_status_gardu()
elif st.session_state.page == "thermovisi":
    render_thermovisi()
elif st.session_state.page == "lapor_gangguan":
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.title("⚡ Form Pelaporan Gangguan GI PANGURURAN 150 kV")
    st.warning("Form Pelaporan Gangguan aktif.")
else:
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.info("Menu ini sedang dalam tahap pengembangan.")