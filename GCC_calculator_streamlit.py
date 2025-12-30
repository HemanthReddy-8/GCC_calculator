import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

def analyze_image(image):
    """Performs pixel analysis for GCC and disease ratios."""
    # Convert PIL to NumPy array
    img_arr = np.array(image.convert("RGB"))
    
    # 1. RGB and GCC Calculation
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

    # Vectorized logic for color masks
    white_mask = (s < 30) & (v > 200)
    yellow_mask = (h >= 20) & (h <= 35) & (s >= 100) & (v >= 70)
    brown_mask = (h >= 10) & (h <= 25) & (s >= 100) & (v >= 20) & (v <= 180)
    green_mask = (h >= 40) & (h <= 80) & (s >= 60) & (v >= 70)
    blue_mask = (h >= 90) & (h <= 130) & (s >= 60) & (v >= 70)
    red_mask = ((h >= 0) & (h <= 10) | (h >= 160) & (h <= 180)) & (s >= 100) & (v >= 70)

    total_w = np.sum(white_mask)
    total_y = np.sum(yellow_mask)
    total_br = np.sum(brown_mask)
    total_g = np.sum(green_mask)
    total_r = np.sum(red_mask)
    total_b = np.sum(blue_mask)

    # 3. Ratio Calculation
    if total_g > 0:
        ratio_w = total_w / total_g
        ratio_br = total_br / total_g
        ratio_y = total_y / total_g
    else:
        ratio_w = ratio_br = ratio_y = 0

    return {
        "gcc": gcc_value,
        "counts": (total_w, total_br, total_y, total_g, total_r, total_b),
        "ratios": (ratio_w, ratio_br, ratio_y)
    }

# --- STREAMLIT UI ---
st.set_page_config(page_title="Batch Crop Health Analyzer", layout="wide")
st.title("🌿 Batch Plant Disease & Ratio Analyzer")
st.markdown("Upload multiple leaf images to compare health metrics and disease ratios.")

# Enable Batch Mode by setting accept_multiple_files=True
uploaded_files = st.file_uploader("Choose leaf images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    summary_data = []

    # Loop through all uploaded files
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        
        with st.expander(f"🔍 Detailed Analysis: {uploaded_file.name}", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, use_container_width=True, caption=f"Original: {uploaded_file.name}")
                
            with col2:
                results = analyze_image(image)
                
                # Metrics
                st.metric("Green Chromatic Coordinate (GCC)", f"{results['gcc']:.4f}")
                
                rw, rb, ry = results['ratios']
                m1, m2, m3 = st.columns(3)
                m1.metric("W/G Ratio", f"{rw:.4f}")
                m2.metric("BR/G Ratio", f"{rb:.4f}")
                m3.metric("Y/G Ratio", f"{ry:.4f}")
                
                tw, tbr, ty, tg, tr, tb = results['counts']
                st.table({
                    "Category": ["White", "Brown", "Yellow", "Green"," Red", "Blue"],
                    "Pixel Count": [tw, tbr, ty, tg, tr, tb]
                })

        # Append data for the final summary table
        summary_data.append({
            "File Name": uploaded_file.name,
            "GCC": round(results['gcc'], 4),
            "W/G Ratio": round(rw, 4),
            "BR/G Ratio": round(rb, 4),
            "Y/G Ratio": round(ry, 4),
            "Green Pixels": tg,
            "Red Pixels": tr,
            "Blue Pixels": tb,
            "Disease Pixels (W+BR+Y)": tw + tbr + ty
        })

    # --- SUMMARY TABLE ---
    st.divider()
    st.header("📊 Batch Summary Table")
    df_summary = pd.DataFrame(summary_data)
    
    # Highlight highest and lowest GCC values for better insight
    st.dataframe(df_summary, use_container_width=True)

    # Allow downloading the summary as CSV
    csv = df_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Summary as CSV",
        data=csv,
        file_name="leaf_health_summary.csv",
        mime="text/csv",
    )

else:
    st.info("Please upload one or more images to start the batch analysis.")
