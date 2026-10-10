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
# 3. MODUL HALAMAN (DASHBOARD & MENU LENGKAP)
# ==============================================================================

def render_dashboard():
    hp = st.session_state.health_params
    avg_health = int((hp["thermo_score"] + hp["gangguan_score"] + hp["anomali_score"] + hp["k3_score"]) / 4)

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


def render_lapor_gangguan():
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    
    st.title("⚡ Form Pelaporan Gangguan Penghantar GI PANGURURAN 150 kV")
    st.write("Silakan masukkan data log gangguan, investigasi relay, dan status pemulihan sistem di bawah ini.")
    
    with st.form("form_laporan_lengkap_gi"):
        st.subheader("1. Waktu & Petugas Piket")
        c1, c2 = st.columns(2)
        with c1:
            tanggal = st.date_input("Tanggal Kejadian Gangguan")
        with c2:
            jam = st.time_input("Jam / Waktu Trip / Indikasi")
        
        operator = st.text_input("Nama Operator / Petugas Bertugas", placeholder="Masukkan nama lengkap operator piket")
        
        st.subheader("2. Klasifikasi & Peralatan Terganggu")
        bay_terganggu = st.selectbox(
            "Pilih Bay / Penghantar / Trafo yang Gangguan",
            [
                "Line 150kV Pangururan - Tele (Line 1)",
                "Line 150kV Pangururan - Tele (Line 2)",
                "Trafo Daya 1 (30 MVA)",
                "Feeder DT 1 (Dusun 1)",
                "Feeder DT 2 (Dusun 2)",
                "Busbar 150kV Utama",
                "PMT Bay Interbus / Copler"
            ]
        )
        
        jenis_gangguan = st.selectbox(
            "Jenis Indikasi Kerja Proteksi",
            [
                "Trip Sempurna (Gangguan Permanen)",
                "Reclose Masuk (Gangguan Temporer / Sambaran Petir)",
                "Trip Relay Distance (Zone 1 / 2 / 3)",
                "Trip OCR / GFR (Over Current / Ground Fault)",
                "Anomali Thermal / Suhu Konektor Tinggi",
                "Gangguan Internal Trafo (Buchholz / Overheat)",
                "Lainnya"
            ]
        )
        
        st.subheader("3. Data Arus Gangguan & Target Relay")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            arus_r = st.text_input("Arus Phasa R (A)", placeholder="Contoh: 320 A")
        with col_r2:
            arus_s = st.text_input("Arus Phasa S (A)", placeholder="Contoh: 315 A")
        with col_r3:
            arus_t = st.text_input("Arus Phasa T (A)", placeholder="Contoh: 325 A")
            
        jarak_ganggu = st.text_input("Estimasi Jarak Gangguan (km - khusus Saluran Transmisi)", placeholder="Contoh: 12.4 km dari GI Pangururan")
        
        st.subheader("4. Kronologi, Tindakan & Catatan Operasional")
        kronologi = st.text_area(
            "Kronologi Singkat & Tindakan Pengamanan", 
            placeholder="Contoh: Terjadi gangguan pada penghantar Tele, PMT trip secara otomatis, relay distance bekerja pada zone 1, dilakukan koordinasi dengan dispatcher UCC..."
        )
        
        status_pemulihan = st.selectbox(
            "Status Akhir Peralatan",
            [
                "Peralatan Normal / Telah Disetting Masuk Kembali",
                "Dalam Investigasi & Penanganan Tim Pemeliharaan",
                "Peralatan Isolasi / Pemeliharaan Darurat"
            ]
        )
        
        submitted = st.form_submit_button("Simpan & Kirim Laporan Gangguan")
        if submitted:
            if not operator:
                st.warning("Mohon isi Nama Operator terlebih dahulu sebelum mengirim laporan.")
            else:
                st.success(f"Laporan gangguan untuk {bay_terganggu} berhasil direkam ke sistem operasional GI Pangururan!")
                st.balloons()


def render_status_gardu():
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.title("⚡ Status Gardu Induk")
    st.info("Sistem pemantauan status peralatan secara real-time aktif.")


def render_thermovisi():
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.title("🎯 Data Thermovisi & Penyesuaian Score")
    new_val = st.slider("Simulasi Skor Thermovisi", 0, 100, st.session_state.health_params["thermo_score"])
    if st.button("Simpan Skor Thermovisi"):
        st.session_state.health_params["thermo_score"] = new_val
        st.success("Skor thermovisi berhasil diperbarui!")


# ==============================================================================
# 4. ROUTER UTAMA APLIKASI
# ==============================================================================
if st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "lapor_gangguan":
    render_lapor_gangguan()
elif st.session_state.page == "status_gardu":
    render_status_gardu()
elif st.session_state.page == "thermovisi":
    render_thermovisi()
else:
    if st.button("← Kembali ke Dashboard"):
        navigate_to("dashboard")
    st.info("Modul menu ini sedang dalam tahap pengembangan.")
