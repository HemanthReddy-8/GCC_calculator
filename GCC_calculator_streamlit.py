import streamlit as st
import numpy as np
from PIL import Image

def analyze_image(image):
    # Convert PIL to NumPy array
    img_arr = np.array(image.convert("RGB"))
    
    # 1. RGB and GCC Calculation
    # Using float to prevent integer overflow
    r = img_arr[:, :, 0].astype(float)
    g = img_arr[:, :, 1].astype(float)
    b = img_arr[:, :, 2].astype(float)
    
    avg_r, avg_g, avg_b = np.mean(r), np.mean(g), np.mean(b)
    
    rgb_sum = avg_r + avg_g + avg_b
    gcc_value = avg_g / rgb_sum if rgb_sum != 0 else 0
    
    # 2. HSV Masking for Pixel Counting
    hsv_image = image.convert("HSV")
    hsv_arr = np.array(hsv_image)
    h, s, v = hsv_arr[:, :, 0], hsv_arr[:, :, 1], hsv_arr[:, :, 2]

    # Vectorized logic (equivalent to your IF/ELIF structure)
    white_mask = (s < 30) & (v > 200)
    yellow_mask = (h >= 20) & (h <= 35) & (s >= 100) & (v >= 70)
    brown_mask = (h >= 10) & (h <= 25) & (s >= 100) & (v >= 20) & (v <= 180)
    green_mask = (h >= 40) & (h <= 80) & (s >= 60) & (v >= 70)

    total_w = np.sum(white_mask)
    total_y = np.sum(yellow_mask)
    total_br = np.sum(brown_mask)
    total_g = np.sum(green_mask)

    # 3. Ratio Calculation
    if total_g > 0:
        ratio_w = total_w / total_g
        ratio_br = total_br / total_g
        ratio_y = total_y / total_g
    else:
        ratio_w = ratio_br = ratio_y = 0

    return {
        "gcc": gcc_value,
        "counts": (total_w, total_br, total_y, total_g),
        "ratios": (ratio_w, ratio_br, ratio_y)
    }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Crop Health Analyzer", layout="wide")
st.title("🌿 Plant Disease & Health Ratio Analyzer")
st.markdown("Upload a leaf image to calculate GCC and SEP Ratios (White, Brown, Yellow vs Green).")

uploaded_file = st.file_uploader("Choose a leaf image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display Image
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input Image")
        st.image(image, use_container_width=True)
        
    with col2:
        st.subheader("Analysis Results")
        with st.spinner("Processing pixels..."):
            results = analyze_image(image)
            
            # Metrics
            st.metric("Green Chromatic Coordinate (GCC)", f"{results['gcc']:.4f}")
            
            st.write("---")
            
            # Ratios
            rw, rb, ry = results['ratios']
            m1, m2, m3 = st.columns(3)
            m1.metric("W/G Ratio", f"{rw:.4f}")
            m2.metric("BR/G Ratio", f"{rb:.4f}")
            m3.metric("Y/G Ratio", f"{ry:.4f}")

            # Raw Counts Table
            st.write("---")
            st.subheader("Pixel Counts")
            tw, tbr, ty, tg = results['counts']
            st.table({
                "Category": ["White", "Brown", "Yellow", "Green"],
                "Pixel Count": [tw, tbr, ty, tg]
            })

else:
    st.info("Please upload an image to start the analysis.")
