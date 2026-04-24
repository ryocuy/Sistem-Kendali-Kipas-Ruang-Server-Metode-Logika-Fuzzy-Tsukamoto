import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# KONFIGURASI & CSS
# ==========================================
st.set_page_config(layout="wide", page_title="Fuzzy Fan Control")

st.markdown("""
<style>
@keyframes spin { 100% { transform: rotate(360deg); } }
.fan-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; margin-top: 20px;}
.metric-value { font-size: 2rem; font-weight: bold; color: #4CAF50;}

/* === SLIDER === */
[data-testid="stSlider"] label p { font-size: 1.2rem !important; font-weight: 600 !important; }
[data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"] { font-size: 1.1rem !important; font-weight: bold !important; }
[data-testid="stSlider"] div[class*="SliderThumb"] span, [data-testid="stSlider"] span { font-size: 1.1rem !important; }
[data-testid="stSlider"] input[type="range"] { height: 10px !important; }
[data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { font-size: 1.15rem !important; font-weight: 700 !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.title("Sistem Kendali Kipas Ruang Server")
st.write("Metode: Logika Fuzzy Tsukamoto")

# --- AREA INPUT ---
st.divider()
col_in1, col_in2 = st.columns(2)
with col_in1:
    suhu = st.slider("Suhu Ruangan (°C)", min_value=15.0, max_value=35.0, value=24.0, step=0.5)
with col_in2:
    lembab = st.slider("Kelembapan (%)", min_value=30.0, max_value=90.0, value=70.0, step=1.0)

# ==========================================
# START LOGIC
# ==========================================

# --- TAHAP 1: FUZZIFIKASI ---
# 1. Variabel Suhu
if suhu <= 21: miu_s1 = 1.0
elif suhu >= 23: miu_s1 = 0.0
else: miu_s1 = (23 - suhu) / 2

if suhu <= 21: miu_s2 = 0.0
elif suhu >= 23: miu_s2 = 1.0
else: miu_s2 = (suhu - 21) / 2

# 2. Variabel Kelembapan
if lembab <= 45: miu_l1 = 1.0
elif lembab >= 55: miu_l1 = 0.0
else: miu_l1 = (55 - lembab) / 10

if lembab <= 45 or lembab >= 65: miu_l2 = 0.0
elif lembab <= 55: miu_l2 = (lembab - 45) / 10
else: miu_l2 = (65 - lembab) / 10

if lembab <= 55: miu_l3 = 0.0
elif lembab >= 65: miu_l3 = 1.0
else: miu_l3 = (lembab - 55) / 10

# --- TAHAP 2: INFERENSI ---
miu1 = min(miu_s1, miu_l1); z1 = 2500 - (miu1 * 1500)
miu2 = min(miu_s1, miu_l2); z2 = 2500 - (miu2 * 1500)
miu3 = min(miu_s1, miu_l3); z3 = 1000 + (miu3 * 1500)
miu4 = min(miu_s2, miu_l1); z4 = 2500 - (miu4 * 1500)
miu5 = min(miu_s2, miu_l2); z5 = 1000 + (miu5 * 1500)
miu6 = min(miu_s2, miu_l3); z6 = 1000 + (miu6 * 1500)

# --- TAHAP 3: DEFUZZIFIKASI ---
pembilang = (miu1*z1) + (miu2*z2) + (miu3*z3) + (miu4*z4) + (miu5*z5) + (miu6*z6)
penyebut = miu1 + miu2 + miu3 + miu4 + miu5 + miu6
hasil_akhir = pembilang / penyebut if penyebut != 0 else 0

# ==========================================
# RENDER UI UTAMA
# ==========================================
col1, col2, col3 = st.columns([1.5, 1, 1.5])

with col1:
    st.subheader("Grafik Fuzzifikasi")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 5))
    x_s = np.arange(15, 36, 1); y_sd = [1 if x <= 21 else 0 if x >= 23 else (23-x)/2 for x in x_s]; y_sp = [0 if x <= 21 else 1 if x >= 23 else (x-21)/2 for x in x_s]
    ax1.plot(x_s, y_sd, label='Dingin', color='blue'); ax1.plot(x_s, y_sp, label='Panas', color='red'); ax1.axvline(x=suhu, color='black', linestyle='--'); ax1.legend(loc="right")
    x_l = np.arange(30, 91, 1); y_lk = [1 if x <= 45 else 0 if x >= 55 else (55-x)/10 for x in x_l]; y_ln = [0 if x <= 45 or x >= 65 else (x-45)/10 if x <= 55 else (65-x)/10 for x in x_l]; y_lb = [0 if x <= 55 else 1 if x >= 65 else (x-55)/10 for x in x_l]
    ax2.plot(x_l, y_lk, label='Kering', color='orange'); ax2.plot(x_l, y_ln, label='Normal', color='green'); ax2.plot(x_l, y_lb, label='Basah', color='purple'); ax2.axvline(x=lembab, color='black', linestyle='--'); ax2.legend(loc="right")
    plt.tight_layout(); st.pyplot(fig)

with col2:
    st.subheader("Target Speed")
    visual_dps = 60 + (hasil_akhir - 1000) / 1500 * 1020 if hasil_akhir > 0 else 0
    fan_component = f"""
    <style>body {{ margin:0; background:transparent; }} .fan-wrap {{ display:flex; flex-direction:column; align-items:center; padding-top:8px; }} .rpm-text {{ font-size:2rem; font-weight:bold; color:#4CAF50; margin-top:12px; font-family:sans-serif; }}</style>
    <div class="fan-wrap">
      <svg id="fan" width="280" height="280" viewBox="-105 -105 210 210" style="transform-origin:50% 50%; display:block;">
        <defs>
          <radialGradient id="bG" cx="35%" cy="25%" r="75%"><stop offset="0%" stop-color="#c8dcff"/><stop offset="45%" stop-color="#3a78c9"/><stop offset="100%" stop-color="#0d2248"/></radialGradient>
          <radialGradient id="hG" cx="38%" cy="32%" r="65%"><stop offset="0%" stop-color="#e0e8f8"/><stop offset="55%" stop-color="#5a6a80"/><stop offset="100%" stop-color="#151e2a"/></radialGradient>
          <filter id="sh"><feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="#001030" flood-opacity="0.5"/></filter>
        </defs>
        <g filter="url(#sh)">
          <g transform="rotate(0)"><path d="M -5,-14 C -18,-28 -28,-60 -18,-82 C -12,-92 2,-90 10,-80 C 22,-65 20,-32 8,-14 Z" fill="url(#bG)" opacity="0.95"/></g>
          <g transform="rotate(72)"><path d="M -5,-14 C -18,-28 -28,-60 -18,-82 C -12,-92 2,-90 10,-80 C 22,-65 20,-32 8,-14 Z" fill="url(#bG)" opacity="0.95"/></g>
          <g transform="rotate(144)"><path d="M -5,-14 C -18,-28 -28,-60 -18,-82 C -12,-92 2,-90 10,-80 C 22,-65 20,-32 8,-14 Z" fill="url(#bG)" opacity="0.95"/></g>
          <g transform="rotate(216)"><path d="M -5,-14 C -18,-28 -28,-60 -18,-82 C -12,-92 2,-90 10,-80 C 22,-65 20,-32 8,-14 Z" fill="url(#bG)" opacity="0.95"/></g>
          <g transform="rotate(288)"><path d="M -5,-14 C -18,-28 -28,-60 -18,-82 C -12,-92 2,-90 10,-80 C 22,-65 20,-32 8,-14 Z" fill="url(#bG)" opacity="0.95"/></g>
        </g>
        <circle r="18" fill="url(#hG)" stroke="#1a2a40" stroke-width="2"/><circle r="10" fill="#b8c8dc" stroke="#3a4a60" stroke-width="1.5"/><circle r="4" fill="#e8f0ff" stroke="#6a7a90" stroke-width="1"/>
      </svg>
      <div class="rpm-text">{hasil_akhir:.0f} RPM</div>
    </div>
    <script>
    (function() {{
      var dps = {visual_dps:.1f}, angle = parseFloat(sessionStorage.getItem('fanAngle') || '0'), lastTs = null, fan = document.getElementById('fan');
      fan.style.transform = 'rotate(' + angle + 'deg)';
      function frame(ts) {{ if (lastTs !== null) {{ var dt = (ts - lastTs) / 1000; angle = (angle + dps * dt) % 360; fan.style.transform = 'rotate(' + angle + 'deg)'; sessionStorage.setItem('fanAngle', angle); }} lastTs = ts; requestAnimationFrame(frame); }}
      if (dps > 0) requestAnimationFrame(frame);
    }})();
    </script>
    """
    components.html(fan_component, height=370)

with col3:
    st.subheader("Tsukamoto Rule Inference")
    all_rules = [
        {"n": "R1: Dingin & Kering -> Lambat", "m": miu1, "z": z1},
        {"n": "R2: Dingin & Normal -> Lambat", "m": miu2, "z": z2},
        {"n": "R3: Dingin & Basah -> Cepat",   "m": miu3, "z": z3},
        {"n": "R4: Panas & Kering -> Lambat",  "m": miu4, "z": z4},
        {"n": "R5: Panas & Normal -> Cepat",   "m": miu5, "z": z5},
        {"n": "R6: Panas & Basah -> Cepat",    "m": miu6, "z": z6}
    ]
    for r in all_rules:
        if r["m"] > 0: st.success(f"**{r['n']}** \nActive (α: {r['m']:.2f}) -> Z: {r['z']:.0f}")
        else: st.info(f"{r['n']}  \n*(Not Active)*")

# ==========================================
# AREA CHEAT SHEET (TAMPILAN MANUAL PAPAN TULIS)
# ==========================================
st.divider()
with st.expander("📝 Buka Lembar Perhitungan Matematis Manual"):
    st.markdown("Sub-sistem ini mengekstrak dan memvisualisasikan hitungan manual *step-by-step* dari parameter yang sedang aktif berdasarkan persamaan Logika Fuzzy Tsukamoto.")
    
    st.markdown("### 🔹 Tahap 1: Fuzzifikasi (Menghitung Derajat Keanggotaan)")
    st.write("Mengonversi nilai *crisp* menjadi nilai *fuzzy* ($\mu$) melalui kurva linier himpunan keanggotaan.")
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.markdown(f"**Variabel Suhu ($x = {suhu}$)**")
        # Formula Suhu Dingin
        if suhu <= 21: st.latex(rf"\mu_{{Dingin}}({suhu}) = 1")
        elif suhu >= 23: st.latex(rf"\mu_{{Dingin}}({suhu}) = 0")
        else: st.latex(rf"\mu_{{Dingin}}({suhu}) = \frac{{23 - {suhu}}}{{23 - 21}} = \frac{{{23-suhu:.2f}}}{{2}} = {miu_s1:.2f}")

        # Formula Suhu Panas
        if suhu <= 21: st.latex(rf"\mu_{{Panas}}({suhu}) = 0")
        elif suhu >= 23: st.latex(rf"\mu_{{Panas}}({suhu}) = 1")
        else: st.latex(rf"\mu_{{Panas}}({suhu}) = \frac{{{suhu} - 21}}{{23 - 21}} = \frac{{{suhu-21:.2f}}}{{2}} = {miu_s2:.2f}")
            
    with c_f2:
        st.markdown(f"**Variabel Kelembapan ($y = {lembab}$)**")
        # Formula Lembab Kering
        if lembab <= 45: st.latex(rf"\mu_{{Kering}}({lembab}) = 1")
        elif lembab >= 55: st.latex(rf"\mu_{{Kering}}({lembab}) = 0")
        else: st.latex(rf"\mu_{{Kering}}({lembab}) = \frac{{55 - {lembab}}}{{55 - 45}} = {miu_l1:.2f}")
        
        # Formula Lembab Normal
        if lembab <= 45 or lembab >= 65: st.latex(rf"\mu_{{Normal}}({lembab}) = 0")
        elif lembab <= 55: st.latex(rf"\mu_{{Normal}}({lembab}) = \frac{{{lembab} - 45}}{{55 - 45}} = {miu_l2:.2f}")
        else: st.latex(rf"\mu_{{Normal}}({lembab}) = \frac{{65 - {lembab}}}{{65 - 55}} = {miu_l2:.2f}")
        
        # Formula Lembab Basah
        if lembab <= 55: st.latex(rf"\mu_{{Basah}}({lembab}) = 0")
        elif lembab >= 65: st.latex(rf"\mu_{{Basah}}({lembab}) = 1")
        else: st.latex(rf"\mu_{{Basah}}({lembab}) = \frac{{{lembab} - 55}}{{65 - 55}} = {miu_l3:.2f}")

    st.markdown("### 🔹 Tahap 2: Inferensi (Aplikasi Fungsi Implikasi MIN)")
    st.write("Mencari nilai $\\alpha$-predicate dari aturan IF-THEN menggunakan logika AND (nilai Minimum), dilanjutkan mencari nilai output diskrit ($Z$) berdasarkan persamaan kurva turun (Lambat) atau kurva naik (Cepat).")
    
    # Membuat Header Tabel Markdown
    tabel_md = "| Status | Rule | Kondisi (Logika IF-THEN) | Nilai Predikat $\\alpha = \\min(...)$ | Kalkulasi Nilai $Z$ |\n"
    tabel_md += "|:---:|:---:|:---|:---|:---|\n"
    
    # Data Rules
    rule_data = [
        (1, "Dingin AND Kering $\\rightarrow$ Lambat", miu_s1, miu_l1, miu1, "2500 - (\\alpha \\times 1500)", z1),
        (2, "Dingin AND Normal $\\rightarrow$ Lambat", miu_s1, miu_l2, miu2, "2500 - (\\alpha \\times 1500)", z2),
        (3, "Dingin AND Basah $\\rightarrow$ Cepat", miu_s1, miu_l3, miu3, "1000 + (\\alpha \\times 1500)", z3),
        (4, "Panas AND Kering $\\rightarrow$ Lambat", miu_s2, miu_l1, miu4, "2500 - (\\alpha \\times 1500)", z4),
        (5, "Panas AND Normal $\\rightarrow$ Cepat", miu_s2, miu_l2, miu5, "1000 + (\\alpha \\times 1500)", z5),
        (6, "Panas AND Basah $\\rightarrow$ Cepat", miu_s2, miu_l3, miu6, "1000 + (\\alpha \\times 1500)", z6),
    ]
    
    # Render isi tabel secara dinamis mengikuti slider
    for i, teks, m1, m2, a, z_rumus, z_hasil in rule_data:
        status = "✅" if a > 0 else "❌"
        alpha_str = f"$\\min({m1:.2f}, {m2:.2f}) = {a:.2f}$"
        
        if a > 0:
            z_str = f"${z_rumus.replace('\\alpha', f'{a:.2f}')} = {z_hasil:.0f}$"
        else:
            z_str = "*(Diabaikan)*"
            
        tabel_md += f"| {status} | **R{i}** | {teks} | {alpha_str} | {z_str} |\n"

    # Tampilkan tabel ke layar
    st.markdown(tabel_md)

    st.markdown("### 🔹 Tahap 3: Defuzzifikasi (Metode Rata-rata Berbobot)")
    st.write("Menyatukan semua agregat rule yang menyala untuk menarik satu nilai ketegasan akhir (*Crisp Output*).")
    
    st.latex(r"Z_{akhir} = \frac{\sum_{i=1}^{n} (\alpha_i \times Z_i)}{\sum_{i=1}^{n} \alpha_i}")
    
    if penyebut == 0:
        st.error("Kalkulasi dibatalkan: Pembagi bernilai 0 (Tidak ada Rule yang terpenuhi).")
    else:
        # Mengambil rule yang aktif saja untuk dijabarkan di rumus
        alphas = [miu1, miu2, miu3, miu4, miu5, miu6]
        zs = [z1, z2, z3, z4, z5, z6]
        
        pembilang_str = r" + ".join([rf"({a:.2f} \times {z:.0f})" for a, z in zip(alphas, zs) if a > 0])
        penyebut_str = r" + ".join([rf"{a:.2f}" for a in alphas if a > 0])
        
        st.latex(rf"Z_{{akhir}} = \frac{{{pembilang_str}}}{{{penyebut_str}}}")
        st.latex(rf"Z_{{akhir}} = \frac{{{pembilang:.2f}}}{{{penyebut:.2f}}} = {hasil_akhir:.2f} \text{{ RPM}}")