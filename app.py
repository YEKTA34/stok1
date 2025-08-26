import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FLO Stok Dashboard", layout="wide")

# ---------------- Kullanıcı Bilgileri ----------------
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "kullanici": {"password": "1234", "role": "kullanici"}  # Viewer artık "kullanici"
}

# ---------------- Session State ----------------
if 'login_status' not in st.session_state:
    st.session_state.login_status = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

# ---------------- CSS ile logo, animasyon, gradient ve buton hover ----------------
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
    <style>
    body { background-color: black; }
    .flo-logo {
        font-family: 'Anton', sans-serif;
        font-size: 120px;
        text-align: center;
        background: linear-gradient(270deg, #FF6600, #FFAA33, #FF6600);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientMove 4s ease infinite, pulse 2s infinite;
        margin-bottom: 20px;
    }
    @keyframes pulse {
        0% {transform: scale(1);}
        50% {transform: scale(1.05);}
        100% {transform: scale(1);}
    }
    @keyframes gradientMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .login-container { text-align: center; margin-top: 20px; }
    .stButton>button {
        background-color: #FF6600; color: black; font-weight: bold;
        width: 200px; height: 50px; font-size: 18px; border-radius: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #FFAA33; color: black; transform: scale(1.05);}
    </style>
""", unsafe_allow_html=True)

# ---------------- Giriş Ekranı ----------------
def login_screen():
    st.markdown('<div class="flo-logo">FLO</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    login_clicked = st.button("Giriş Yap")
    if login_clicked:
        if username in USERS and password == USERS[username]["password"]:
            st.session_state.login_status = True
            st.session_state.user_role = USERS[username]["role"]
            st.session_state.username = username
        else:
            st.error("Kullanıcı adı veya şifre yanlış!")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Dashboard ----------------
def dashboard():
    # Dashboard üstünde logo hep görünür
    st.markdown('<div class="flo-logo">FLO</div>', unsafe_allow_html=True)
    
    st.sidebar.success(f"Giriş yapıldı: {st.session_state.username} ({st.session_state.user_role})")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state.login_status = False
        st.experimental_rerun()

    st.title("📦 FLO Stok Takip Dashboard")

    # ---------------- Session State ile veri saklama ----------------
    if 'df' not in st.session_state:
        data = {
            "Ürün": ["Spor Ayakkabı", "Çanta", "Tişört", "Bot", "Cüzdan"],
            "Kategori": ["Ayakkabı", "Aksesuar", "Giyim", "Ayakkabı", "Aksesuar"],
            "Stok": [50, 10, 30, 5, 100]
        }
        st.session_state.df = pd.DataFrame(data)

    if 'gecmis_satis' not in st.session_state:
        st.session_state.gecmis_satis = {
            "Spor Ayakkabı": [5,7,6,8,7],
            "Çanta": [1,2,1,1,2],
            "Tişört": [3,4,3,3,4],
            "Bot": [0,1,1,0,1],
            "Cüzdan": [10,9,11,10,12]
        }

    # ---------------- Sidebar Filtre ----------------
    st.sidebar.subheader("Filtreleme")
    kategori_sec = st.sidebar.multiselect(
        "Kategori Seç", 
        options=st.session_state.df["Kategori"].unique(), 
        default=st.session_state.df["Kategori"].unique()
    )

    # ---------------- Yeni Ürün Ekleme (Sadece Admin) ----------------
    if st.session_state.user_role == "admin":
        st.sidebar.subheader("Yeni Ürün Ekle")
        yeni_urun = st.sidebar.text_input("Ürün Adı")
        kategori = st.sidebar.selectbox("Kategori", ["Ayakkabı", "Giyim", "Aksesuar"])
        stok_miktari = st.sidebar.number_input("Stok Miktarı", min_value=0, step=1)
        tahmini_gunluk_satis = st.sidebar.number_input("Tahmini Günlük Satış", min_value=0.1, step=0.1, value=1.0)

        if st.sidebar.button("Ekle"):
            if yeni_urun.strip() != "":
                st.session_state.df.loc[len(st.session_state.df)] = [yeni_urun, kategori, stok_miktari]
                st.session_state.gecmis_satis[yeni_urun] = [tahmini_gunluk_satis]*5
                st.success(f"{yeni_urun} başarıyla eklendi! Tablolar ve grafikler güncellendi.")
            else:
                st.error("Lütfen geçerli bir ürün adı girin.")

    # ---------------- Filtreli Dataframe ----------------
    df_filtreli = st.session_state.df[st.session_state.df["Kategori"].isin(kategori_sec)]

    # ---------------- Mevcut Stok Tablosu ----------------
    st.subheader("Mevcut Stok Listesi")
    st.dataframe(df_filtreli)

    # Azalan stoklar
    st.subheader("⚠️ Azalan Stoklar (20'nin Altı)")
    azalan = df_filtreli[df_filtreli["Stok"] < 20]
    if not azalan.empty:
        st.table(azalan.style.applymap(lambda x: 'background-color: red', subset=["Stok"]))
    else:
        st.write("Tüm ürünlerin stoku yeterli.")

    # ---------------- Stok Grafiği ----------------
    st.subheader("📊 Stok Dağılımı")
    fig = px.bar(df_filtreli, x="Ürün", y="Stok", color="Kategori", 
                title="Ürün Bazlı Stok Seviyeleri",
                hover_data=["Ürün", "Stok", "Kategori"])
    st.plotly_chart(fig)

    # ---------------- Tahmini Satış ve Tükenme ----------------
    kritik_gun = 5
    stok_esigi = 10
    tahmini_satis_dict = {}
    tukenme_suresi_dict = {}

    for index, row in df_filtreli.iterrows():
        urun = row["Ürün"]
        satis = st.session_state.gecmis_satis.get(urun, [1]*5)
        ortalama_satis = sum(satis)/len(satis)
        kalan_stok = row["Stok"]
        tahmini_gun = kalan_stok / ortalama_satis if ortalama_satis != 0 else 0
        
        tahmini_satis_dict[urun] = round(ortalama_satis,1)
        tukenme_suresi_dict[urun] = round(tahmini_gun,1)

    # Tahmini Satış Tablosu
    st.subheader("📈 Tahmini Günlük Satış (adet)")
    df_satis = pd.DataFrame(list(tahmini_satis_dict.items()), columns=["Ürün","Tahmini Günlük Satış"])
    st.table(df_satis)

    # Tükenme Süresi Tablosu
    st.subheader("⏳ Tükenme Süresi (gün)")
    df_tukenme = pd.DataFrame(list(tukenme_suresi_dict.items()), columns=["Ürün","Tükenme Süresi"])
    st.table(df_tukenme)

    # Grafikler
    st.subheader("📊 Grafikler")
    col1, col2 = st.columns(2)

    with col1:
        fig_satis = px.bar(df_satis, x="Ürün", y="Tahmini Günlük Satış", color="Ürün",
                        title="Tahmini Günlük Satış Grafiği",
                        hover_data=["Tahmini Günlük Satış"])
        st.plotly_chart(fig_satis)

    with col2:
        renkler = ['red' if x < kritik_gun else 'green' for x in df_tukenme["Tükenme Süresi"]]
        fig_tukenme = px.bar(df_tukenme, x="Ürün", y="Tükenme Süresi", color=df_tukenme["Ürün"],
                            title="Tükenme Süresi Grafiği",
                            hover_data=["Tükenme Süresi"],
                            color_discrete_sequence=renkler)
        st.plotly_chart(fig_tukenme)

    # Kritik Stok Uyarısı
    st.subheader("⚠️ Kritik Stok Uyarısı")
    for urun, gun in tukenme_suresi_dict.items():
        if gun < kritik_gun:
            st.warning(f"{urun} {kritik_gun} gün içinde tükenebilir!")

    # Stok Azalma Otomatik Uyarısı
    st.subheader("🛎️ Stok Uyarıları")
    for index, row in df_filtreli.iterrows():
        if row["Stok"] < stok_esigi:
            st.error(f"{row['Ürün']} stok miktarı kritik seviyeye düştü! ({row['Stok']} adet kaldı)")

# ---------------- Ana Kontrol ----------------
if not st.session_state.login_status:
    login_screen()
else:
    dashboard()
