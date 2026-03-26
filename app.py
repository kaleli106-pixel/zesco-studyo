import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter
import io

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Zesco Ürün Stüdyosu", layout="centered")
st.title("👟 Zesco Otomatik Ürün Fotoğrafı İşleme")
st.write("Ayakkabı fotoğraflarını yükle, arka planı silinsin, 1000x1000 beyaz fona gölgeli olarak yerleşsin.")

def process_shoe_image(upload):
    img = Image.open(upload)
    output_img = remove(img)
    bbox = output_img.getbbox()
    if bbox:
        output_img = output_img.crop(bbox)
        
    target_size = 1000
    padding = 150
    max_size = target_size - (padding * 2)
    output_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    final_image = Image.new("RGB", (target_size, target_size), (255, 255, 255))
    x = (target_size - output_img.width) // 2
    y = (target_size - output_img.height) // 2

    shadow = Image.new("RGBA", output_img.size, (0, 0, 0, 0))
    shadow_mask = output_img.split()[3]
    shadow.paste((0, 0, 0, 160), mask=shadow_mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    
    shadow_height = int(output_img.height * 0.15)
    shadow_resized = shadow.resize((output_img.width, shadow_height))
    shadow_y = y + output_img.height - int(shadow_height * 0.6)
    
    final_image.paste(shadow_resized, (x, shadow_y), shadow_resized)
    final_image.paste(output_img, (x, y), output_img)
    
    return final_image

uploaded_files = st.file_uploader("Ayakkabı fotoğraflarını seç (Çift ve Yan poz)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"**{len(uploaded_files)} fotoğraf işleniyor...** Lütfen bekleyin.")
    cols = st.columns(len(uploaded_files))
    for i, file in enumerate(uploaded_files):
        with st.spinner(f"{file.name} işleniyor..."):
            processed_img = process_shoe_image(file)
            with cols[i]:
                st.image(processed_img, caption=f"İşlendi: {file.name}", use_column_width=True)
                buf = io.BytesIO()
                processed_img.save(buf, format="JPEG", quality=95)
                byte_im = buf.getvalue()
                st.download_button(
                    label="⬇️ İndir (1000x1000)",
                    data=byte_im,
                    file_name=f"zesco_islenmis_{file.name}",
                    mime="image/jpeg"
                )
