import streamlit as st
import requests
import os
import io
try:
    from gtts import gTTS
    GTTS_OK = True
except Exception:
    GTTS_OK = False

# Baca API key: st.secrets (Streamlit Cloud) → .env (lokal)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
BASE_URL = "https://api.groq.com/openai/v1"

# Model fallback — urutan prioritas dari paling canggih ke paling ringan
# (llama3-8b-8192 dan llama3-70b-8192 sudah decommissioned per Groq)
MODEL_FALLBACK = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

@st.cache_data(ttl=300)
def ambil_model_aktif():
    """Ambil model Llama yang benar-benar aktif di Groq saat ini."""
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    try:
        r = requests.get(f"{BASE_URL}/models", headers=headers, timeout=10)
        if r.status_code == 200:
            ids = {m["id"] for m in r.json().get("data", [])}
            for m in MODEL_FALLBACK:
                if m in ids:
                    return m
    except Exception:
        pass
    return MODEL_FALLBACK[-1]  # fallback paling ringan

st.set_page_config(page_title="SosioSmart AI – Bimbel Sosiologi", page_icon="📚", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Login card */
.login-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 40px;
    max-width: 480px;
    margin: 60px auto;
}

.app-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.app-subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 30px;
}

/* Materi box */
.materi-box {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(167,139,250,0.3);
    border-left: 4px solid #a78bfa;
    border-radius: 14px;
    padding: 28px 32px;
    color: #e2e8f0;
    line-height: 1.9;
    font-size: 0.97rem;
    white-space: pre-wrap;
}

/* Soal box */
.soal-box {
    background: rgba(96,165,250,0.08);
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 14px;
    padding: 24px;
    color: #e2e8f0;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* Badge progress */
.badge {
    display: inline-block;
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    margin: 4px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Text inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e2e8f0 !important;
    border-radius: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #94a3b8;
    border-radius: 10px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #7c3aed, #2563eb) !important;
    color: white !important;
}

.info-chip {
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.4);
    color: #a78bfa;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.85rem;
    margin-bottom: 12px;
    display: inline-block;
}

/* ── Chat Room ── */
.chat-bubble-user {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 75%;
    margin-left: auto;
    font-size: 0.95rem;
    line-height: 1.6;
    word-wrap: break-word;
}
.chat-bubble-ai {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 78%;
    font-size: 0.95rem;
    line-height: 1.7;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.chat-meta-user {
    text-align: right;
    color: #94a3b8;
    font-size: 0.75rem;
    margin-bottom: 2px;
    padding-right: 4px;
}
.chat-meta-ai {
    color: #94a3b8;
    font-size: 0.75rem;
    margin-bottom: 2px;
    padding-left: 4px;
}
.chat-container {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    min-height: 300px;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 16px;
}
.chat-topic-btn {
    display: inline-block;
    background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.35);
    color: #c4b5fd;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    margin: 4px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ── Kurikulum Merdeka Belajar ──────────────────────────────────────────────
KURIKULUM = {
    "Kelas 10 – Fase E": {
        "Sosiologi sebagai Ilmu Pengetahuan": [
            "Hakikat dan Fungsi Sosiologi",
            "Metode Ilmiah dalam Sosiologi",
            "Tokoh-Tokoh Sosiologi Dunia"
        ],
        "Interaksi Sosial & Dinamika Masyarakat": [
            "Interaksi Sosial: Syarat dan Bentuknya",
            "Status dan Peran Sosial",
            "Nilai dan Norma Sosial"
        ],
        "Penelitian Sosial Dasar": [
            "Desain Penelitian Sosial",
            "Teknik Pengumpulan Data",
            "Analisis dan Interpretasi Data"
        ]
    },
    "Kelas 11 – Fase F": {
        "Kelompok & Organisasi Sosial": [
            "Kelompok Sosial: Jenis dan Fungsi",
            "Organisasi Sosial Formal & Informal",
            "Komunitas dan Asosiasi"
        ],
        "Konflik & Integrasi Sosial": [
            "Teori Konflik: Marx, Dahrendorf, Coser",
            "Penyebab dan Dampak Konflik Sosial",
            "Integrasi dan Disintegrasi Sosial"
        ],
        "Stratifikasi & Mobilitas Sosial": [
            "Sistem Stratifikasi Sosial",
            "Mobilitas Sosial: Vertikal & Horizontal",
            "Kesenjangan Sosial di Indonesia"
        ]
    },
    "Kelas 12 – Fase F": {
        "Perubahan Sosial & Modernisasi": [
            "Teori Perubahan Sosial (Evolusi, Siklus, Fungsional)",
            "Modernisasi dan Westernisasi",
            "Dampak Perubahan Sosial bagi Masyarakat"
        ],
        "Globalisasi & Transformasi Budaya": [
            "Globalisasi: Dimensi Ekonomi, Politik, Budaya",
            "Glocalization dan Identitas Lokal",
            "Media Sosial sebagai Agen Globalisasi"
        ],
        "Pemberdayaan Komunitas": [
            "Konsep Pemberdayaan Masyarakat",
            "Kearifan Lokal sebagai Modal Sosial",
            "Program Pemberdayaan & Studi Kasus Indonesia"
        ]
    }
}

def panggil_ai(prompt_sistem, prompt_user, temperature=0.4, max_tokens=1024):
    model = ambil_model_aktif()
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt_sistem},
            {"role": "user", "content": prompt_user}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        res = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        if res.status_code != 200:
            # Tampilkan pesan error yang informatif
            detail = res.json().get("error", {}).get("message", res.text)
            return f"[Error API {res.status_code}] {detail}\nModel dicoba: {model}"
        teks = res.json()['choices'][0]['message']['content']
        return teks.replace("**", "").replace("*", "")
    except Exception as e:
        return f"Gagal memuat konten. Error: {str(e)}"

SISTEM_MATERI = """Anda adalah Dosen Sosiologi berpengalaman dengan latar belakang akademik S3 Sosiologi UI.
Tugas Anda menyusun materi ajar MENDALAM dan KREDIBEL untuk siswa SMA/Kurikulum Merdeka.

ATURAN FORMAT (WAJIB):
- DILARANG KERAS menggunakan simbol bintang (*) atau tanda pagar (#) untuk format.
- Gunakan HURUF KAPITAL untuk judul bagian.
- Gunakan angka (1, 2, 3) atau strip (-) untuk daftar.
- Gunakan tanda kurung siku untuk sub-judul, contoh: [A. DEFINISI]

ATURAN ISI:
- Sertakan minimal 2 TEORI dari sosiolog ternama (nama, tahun, konsep inti).
- Sertakan minimal 2 CONTOH NYATA dari konteks Indonesia.
- Gunakan terminologi akademik yang tepat namun mudah dipahami siswa SMA.
- Akhiri dengan REFLEKSI KRITIS: pertanyaan yang mendorong pemikiran kritis."""

SISTEM_KUIS = """Anda adalah penyusun soal Sosiologi berpengalaman, mengacu pada soal UTBK/SNBT dan UN.
ATURAN FORMAT (WAJIB):
- DILARANG KERAS menggunakan simbol bintang (*).
- Tulis soal dengan nomor: "SOAL 1:", "SOAL 2:", dst.
- Pilihan jawaban: A), B), C), D), E)
- Di baris paling bawah tulis: KUNCI: [nomor soal]-[huruf], [nomor]-[huruf]
- Sertakan PEMBAHASAN singkat setelah kunci."""

SISTEM_KONSELOR = """Anda adalah Kak Sosi, konselor dan mentor pendidikan yang hangat, empatik, dan bijaksana.
Anda mendampingi siswa SMA yang sedang belajar Sosiologi dan mungkin mengalami tekanan belajar.

PERANAN ANDA:
- Mendengarkan curahan hati siswa dengan penuh empati dan tanpa menghakimi.
- Memberikan semangat dan motivasi yang tulus dan personal.
- Membantu siswa memahami kesulitan belajar Sosiologi dengan cara yang ramah.
- Jika siswa bertanya soal materi, jawab dengan jelas namun tetap hangat.
- Jika siswa curhat tentang masalah pribadi/sosial, dengarkan dan beri perspektif sosiologis yang relevan.

GAYA BAHASA:
- Gunakan bahasa Indonesia yang santai namun tetap sopan (boleh pakai "kamu").
- DILARANG menggunakan bintang (*) atau simbol markdown.
- Gunakan emoji sesekali untuk membuat suasana hangat.
- Respons tidak perlu terlalu panjang, cukup 3-5 kalimat yang bermakna.
- Panggil siswa dengan nama mereka."""


def buat_audio(teks):
    if not GTTS_OK:
        return None
    try:
        tts = gTTS(text=teks[:600], lang='id')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except Exception:
        return None

# ── Session State Init ─────────────────────────────────────────────────────
for k, v in {
    "status": "login", "progres": [], "skor": 0,
    "total_kuis": 0, "teks_materi": None, "topik_aktif": None,
    "chat_history": []  # [{"role": "user/ai", "teks": "...", "waktu": "..."}]
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HALAMAN LOGIN ──────────────────────────────────────────────────────────
if st.session_state.status == "login":
    st.markdown('<div class="app-title">📚 SosioSmart AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Platform Bimbel Sosiologi berbasis Kecerdasan Buatan · Kurikulum Merdeka</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nama = st.text_input("👤 Nama Lengkap", placeholder="Masukkan nama Anda...")
        kelas = st.selectbox("🎓 Pilih Kelas", list(KURIKULUM.keys()))
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Mulai Belajar", use_container_width=True):
            if nama.strip():
                st.session_state.update({
                    "user": nama.strip(), "kelas": kelas,
                    "status": "belajar", "progres": [],
                    "skor": 0, "total_kuis": 0
                })
                st.rerun()
            else:
                st.error("Nama tidak boleh kosong.")

# ── HALAMAN UTAMA ──────────────────────────────────────────────────────────
else:
    kelas = st.session_state.kelas
    bab_list = KURIKULUM[kelas]

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.markdown(f"🎓 **{kelas}**")
        st.divider()

        akurasi = round((st.session_state.skor / st.session_state.total_kuis) * 100) if st.session_state.total_kuis > 0 else 0
        st.metric("✅ Skor Akumulatif", f"{st.session_state.skor} poin")
        st.metric("🎯 Akurasi Kuis", f"{akurasi}%")
        st.progress(akurasi / 100)
        st.divider()

        st.markdown("**📖 Bab Selesai:**")
        if st.session_state.progres:
            for p in st.session_state.progres:
                st.markdown(f'<span class="badge">✓ {p}</span>', unsafe_allow_html=True)
        else:
            st.caption("Belum ada bab selesai.")

        st.divider()
        if st.sidebar.button("🔓 Keluar"):
            for k in ["status", "user", "kelas", "teks_materi", "topik_aktif", "soal_kuis"]:
                st.session_state.pop(k, None)
            st.session_state.status = "login"
            st.rerun()

    st.markdown(f'<div class="info-chip">📚 Kurikulum Merdeka Belajar · {kelas}</div>', unsafe_allow_html=True)

    tab_materi, tab_kuis, tab_ringkasan, tab_chat = st.tabs([
        "📖 Materi Mendalam", "🧠 Kuis & Evaluasi", "📊 Ringkasan Belajar", "💬 Ruang Chat"
    ])

    # ── TAB MATERI ──────────────────────────────────────────────────────────
    with tab_materi:
        bab_pilih = st.selectbox("📂 Pilih Bab:", list(bab_list.keys()))
        topik_pilih = st.selectbox("📌 Pilih Topik:", bab_list[bab_pilih])

        col_a, col_b = st.columns([2, 1])
        with col_a:
            buka = st.button("📖 Buka Materi Lengkap", use_container_width=True)
        with col_b:
            audio_btn = st.button("🔊 Dengarkan Ringkasan", use_container_width=True)

        if buka:
            prompt = (
                f"Susun materi ajar MENDALAM tentang: '{topik_pilih}' (Bab: {bab_pilih}, {kelas}).\n\n"
                f"Struktur WAJIB:\n"
                f"[A. PENGERTIAN DAN RUANG LINGKUP]\n"
                f"Definisi dari minimal 2 ahli sosiologi (nama, tahun, kutipan konsep).\n\n"
                f"[B. LANDASAN TEORI]\n"
                f"Minimal 2 teori sosiologi yang relevan, jelaskan konsep inti dan tokohnya.\n\n"
                f"[C. KONSEP-KONSEP KUNCI]\n"
                f"Daftar dan penjelasan istilah/konsep penting.\n\n"
                f"[D. CONTOH DAN FENOMENA DI INDONESIA]\n"
                f"Minimal 2 contoh nyata dari konteks sosial Indonesia (bisa ekonomi, budaya, politik).\n\n"
                f"[E. KETERKAITAN DENGAN ISU KONTEMPORER]\n"
                f"Hubungkan topik ini dengan isu sosial yang relevan saat ini.\n\n"
                f"[F. REFLEKSI KRITIS]\n"
                f"2-3 pertanyaan kritis untuk merangsang pemikiran mendalam siswa."
            )
            with st.spinner("🤖 AI sedang menyusun materi akademik mendalam..."):
                hasil = panggil_ai(SISTEM_MATERI, prompt, max_tokens=2000)
                st.session_state.teks_materi = hasil
                st.session_state.topik_aktif = topik_pilih

        if st.session_state.teks_materi:
            st.markdown(f'<div class="materi-box">{st.session_state.teks_materi}</div>', unsafe_allow_html=True)

        if audio_btn and st.session_state.teks_materi:
            with st.spinner("🔊 Membuat audio..."):
                audio = buat_audio(st.session_state.teks_materi)
                if audio:
                    st.audio(audio, format="audio/mp3")

    # ── TAB KUIS ────────────────────────────────────────────────────────────
    with tab_kuis:
        if not st.session_state.teks_materi:
            st.info("💡 Buka materi terlebih dahulu di tab **Materi Mendalam**.")
        else:
            st.markdown(f"**Topik Kuis:** {st.session_state.topik_aktif}")
            tingkat = st.radio("Tingkat Kesulitan:", ["Dasar (C1-C2)", "Menengah (C3-C4)", "UTBK/HOTS (C5-C6)"], horizontal=True)
            jumlah = st.slider("Jumlah Soal:", 3, 10, 5)

            if st.button("🎯 Buat Soal Kuis", use_container_width=True):
                prompt_kuis = (
                    f"Buat {jumlah} soal pilihan ganda tentang: '{st.session_state.topik_aktif}'\n"
                    f"Tingkat: {tingkat}\n"
                    f"Konteks materi:\n{st.session_state.teks_materi[:1200]}\n\n"
                    f"Soal harus menguji pemahaman KONSEP, bukan sekadar hafalan."
                )
                with st.spinner("🤖 Menyusun soal..."):
                    soal = panggil_ai(SISTEM_KUIS, prompt_kuis, max_tokens=1500)
                    st.session_state.soal_kuis = soal
                    st.session_state.total_kuis += jumlah

            if "soal_kuis" in st.session_state and st.session_state.soal_kuis:
                bagian = st.session_state.soal_kuis.split("KUNCI:")
                soal_teks = bagian[0]
                kunci_teks = bagian[1].strip() if len(bagian) > 1 else ""

                st.markdown(f'<div class="soal-box">{soal_teks}</div>', unsafe_allow_html=True)

                jawaban = st.text_input("✏️ Jawaban Anda (contoh: 1-A, 2-C, 3-B):", placeholder="1-A, 2-C, 3-B ...")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Kirim Jawaban"):
                        if jawaban.strip():
                            poin = sum(1 for j in jawaban.upper().split(",") if j.strip() in kunci_teks.upper())
                            st.session_state.skor += poin
                            if poin == jumlah:
                                st.success(f"🏆 Sempurna! Semua {jumlah} jawaban benar! +{poin} poin")
                            elif poin > 0:
                                st.warning(f"👍 {poin} dari {jumlah} benar. +{poin} poin")
                            else:
                                st.error("❌ Belum ada yang benar. Pelajari kembali materinya.")

                            if st.session_state.topik_aktif not in st.session_state.progres:
                                st.session_state.progres.append(st.session_state.topik_aktif)

                with col2:
                    if st.button("👁️ Lihat Kunci & Pembahasan"):
                        st.info(f"**Kunci Jawaban:**\n{kunci_teks}")

    # ── TAB RINGKASAN ────────────────────────────────────────────────────────
    with tab_ringkasan:
        if not st.session_state.teks_materi:
            st.info("Buka materi terlebih dahulu untuk membuat ringkasan.")
        else:
            if st.button("📝 Buat Ringkasan Otomatis", use_container_width=True):
                prompt_ringkasan = (
                    f"Buat ringkasan AKADEMIS dan PADAT dari materi berikut:\n"
                    f"{st.session_state.teks_materi[:2000]}\n\n"
                    f"Format: poin-poin utama, istilah kunci, dan 1 kesimpulan analitis. "
                    f"Maksimal 350 kata. DILARANG gunakan bintang (*)."
                )
                with st.spinner("🤖 Menyusun ringkasan..."):
                    ringkasan = panggil_ai(SISTEM_MATERI, prompt_ringkasan, max_tokens=600)
                    st.session_state.ringkasan = ringkasan

            if "ringkasan" in st.session_state:
                st.markdown(f'<div class="materi-box">{st.session_state.ringkasan}</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 Statistik Belajar")
        col1, col2, col3 = st.columns(3)
        col1.metric("Topik Dipelajari", len(st.session_state.progres))
        col2.metric("Total Poin", st.session_state.skor)
        col3.metric("Soal Dikerjakan", st.session_state.total_kuis)

    # ── TAB CHAT ─────────────────────────────────────────────────────────────
    with tab_chat:
        from datetime import datetime

        st.markdown("### 💬 Ruang Chat — Curhat & Konsultasi")
        st.caption("Tempat aman untuk bertanya, curhat, dan mendapat semangat dari Kak Sosi 🌟")

        # Starter topic chips
        st.markdown("**Mulai dengan topik:**")
        chip_cols = st.columns(4)
        topik_cepat = [
            "😰 Susah fokus belajar",
            "📚 Minta rangkuman materi",
            "😔 Stres menghadapi ujian",
            "🤔 Tanya soal Sosiologi"
        ]
        for i, topik in enumerate(topik_cepat):
            with chip_cols[i]:
                if st.button(topik, key=f"chip_{i}", use_container_width=True):
                    st.session_state.chat_history.append({
                        "role": "user",
                        "teks": topik,
                        "waktu": datetime.now().strftime("%H:%M")
                    })
                    nama_siswa = st.session_state.get("user", "kamu")
                    prompt_konselor = (
                        f"Nama siswa: {nama_siswa}. Kelas: {kelas}.\n"
                        f"Pesan siswa: {topik}"
                    )
                    with st.spinner("Kak Sosi sedang mengetik..."):
                        balas = panggil_ai(SISTEM_KONSELOR, prompt_konselor, temperature=0.7, max_tokens=400)
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "teks": balas.replace("**", "").replace("*", ""),
                        "waktu": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

        st.markdown("---")

        # Render riwayat chat
        if st.session_state.chat_history:
            chat_html = '<div class="chat-container">'
            for pesan in st.session_state.chat_history:
                if pesan["role"] == "user":
                    chat_html += f'<div class="chat-meta-user">{st.session_state.user} · {pesan["waktu"]}</div>'
                    chat_html += f'<div class="chat-bubble-user">{pesan["teks"]}</div>'
                else:
                    chat_html += f'<div class="chat-meta-ai">🌟 Kak Sosi · {pesan["waktu"]}</div>'
                    chat_html += f'<div class="chat-bubble-ai">{pesan["teks"]}</div>'
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="chat-container" style="display:flex;align-items:center;justify-content:center;">'
                '<p style="color:#64748b;text-align:center;">'
                '🌸 Halo! Aku Kak Sosi.<br>Cerita apa saja boleh — tentang pelajaran, perasaan, atau apapun yang kamu mau.'
                '</p></div>',
                unsafe_allow_html=True
            )

        # Input pesan
        with st.form(key="form_chat", clear_on_submit=True):
            col_input, col_send = st.columns([5, 1])
            with col_input:
                pesan_user = st.text_input(
                    "Ketik pesanmu...",
                    placeholder="Contoh: Kak, aku susah ngerti konsep stratifikasi sosial...",
                    label_visibility="collapsed"
                )
            with col_send:
                kirim = st.form_submit_button("Kirim 📤", use_container_width=True)

        if kirim and pesan_user.strip():
            st.session_state.chat_history.append({
                "role": "user",
                "teks": pesan_user.strip(),
                "waktu": datetime.now().strftime("%H:%M")
            })

            # Kirim seluruh konteks percakapan ke AI
            nama_siswa = st.session_state.get("user", "kamu")
            riwayat_teks = "\n".join(
                f"{'Siswa' if p['role']=='user' else 'Kak Sosi'}: {p['teks']}"
                for p in st.session_state.chat_history[-8:]  # max 8 pesan terakhir
            )
            prompt_konselor = (
                f"Nama siswa: {nama_siswa}. Kelas: {kelas}.\n"
                f"Riwayat percakapan:\n{riwayat_teks}\n\n"
                f"Balas pesan terakhir siswa dengan hangat dan relevan."
            )
            with st.spinner("Kak Sosi sedang mengetik... 💬"):
                balas = panggil_ai(SISTEM_KONSELOR, prompt_konselor, temperature=0.7, max_tokens=400)

            st.session_state.chat_history.append({
                "role": "ai",
                "teks": balas.replace("**", "").replace("*", ""),
                "waktu": datetime.now().strftime("%H:%M")
            })
            st.rerun()

        # Tombol hapus riwayat
        if st.session_state.chat_history:
            if st.button("🗑️ Hapus Riwayat Chat", type="secondary"):
                st.session_state.chat_history = []
                st.rerun()