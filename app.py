import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter
import io

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Zesco Ürün Stüdyosu", layout="centered")
st.title("👟 Zesco Otomatik Ürün Fotoğrafı İşleme")
st.write("Ayakkabı fotoğraflarını yükle, arka planı silinsin, 1000x1000 beyaz fona gölgeli olarak yerleşsin.")

# İşlem fonksiyonu
def process_shoe_image(upload):
    # Görüntüyü oku
    img = Image.open(upload)
    
    # 1. Arka Planı Temizle (Rembg)
    output_img = remove(img)
    
    # 2. Görseldeki fazla boşlukları kırp (Sadece ayakkabı kalsın)
    bbox = output_img.getbbox()
    if bbox:
        output_img = output_img.crop(bbox)
        
    # 3. 1000x1000 Beyaz Fon ve Konumlandırma
    target_size = 1000
    padding = 150 # Kenarlardan ne kadar boşluk kalacağı
    max_size = target_size - (padding * 2)
    
    # Ayakkabıyı orantılı olarak küçült/büyült
    output_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Bembeyaz arka plan oluştur
    final_image = Image.new("RGB", (target_size, target_size), (255, 255, 255))
    
    # Ayakkabıyı tam merkeze oturtmak için X ve Y koordinatları
    x = (target_size - output_img.width) // 2
    y = (target_size - output_img.height) // 2

    # 4. Gölge (Drop Shadow / Contact Shadow) Ekleme
    # Ayakkabının şeklini alıp siyah bir gölge maskesi çıkarıyoruz
    shadow = Image.new("RGBA", output_img.size, (0, 0, 0, 0))
    shadow_mask = output_img.split()[3] # Sadece saydamlık (alpha) kanalını al
    shadow.paste((0, 0, 0, 160), mask=shadow_mask) # %60 Opaklıkta siyah yap
    
    # Gölgeyi yumuşat (Blur)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    
    # Gölgeyi biraz basık (perspektif) yap ve tabana indir
    shadow_height = int(output_img.height * 0.15)
    shadow_resized = shadow.resize((output_img.width, shadow_height))
    
    # Gölgenin Y eksenindeki yeri (ayakkabının tam altına)
    shadow_y = y + output_img.height - int(shadow_height * 0.6)
    
    # Katmanları Birleştir: Önce gölgeyi, sonra ayakkabıyı beyaz fona yapıştır
    final_image.paste(shadow_resized, (x, shadow_y), shadow_resized)
    final_image.paste(output_img, (x, y), output_img)
    
    return final_image

# --- DOSYA YÜKLEME ALANI ---
# 2 farklı poz ekleneceği için çoklu yüklemeye izin veriyoruz
uploaded_files = st.file_uploader("Ayakkabı fotoğraflarını seç (Çift ve Yan poz)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"**{len(uploaded_files)} fotoğraf işleniyor...** Lütfen bekleyin.")
    
    # İşlenen görselleri yan yana göstermek için kolonlar oluştur
    cols = st.columns(len(uploaded_files))
    
    for i, file in enumerate(uploaded_files):
        with st.spinner(f"{file.name} işleniyor..."):
