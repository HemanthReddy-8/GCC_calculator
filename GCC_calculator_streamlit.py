import streamlit as st
from PIL import Image
import numpy as np

def extract_rgb_values(image):
    # Convert PIL image to a NumPy array for speed
    img_array = np.array(image.convert("RGB"))
    
    # Calculate the mean across the width and height (axes 0 and 1)
    avg_colors = np.mean(img_array, axis=(0, 1))
    
    return int(avg_colors[0]), int(avg_colors[1]), int(avg_colors[2])

def calculate_gcc(avg_r, avg_g, avg_b):
    total = avg_r + avg_g + avg_b
    if total == 0:
        return 0.0
    return avg_g / total

# --- Streamlit UI ---
st.title("Green Chromatic Coordinate (GCC) Calculator")
st.write("Upload an image to calculate its average RGB values and GCC.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_container_width=True)
    
    # Run the calculations
    avg_r, avg_g, avg_b = extract_rgb_values(image)
    gcc_value = calculate_gcc(avg_r, avg_g, avg_b)
    
    # Display results in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average RGB")
        st.markdown(f"**Red:** {avg_r}")
        st.markdown(f"**Green:** {avg_g}")
        st.markdown(f"**Blue:** {avg_b}")
        
    with col2:
        st.subheader("GCC Analysis")
        st.metric(label="GCC Value", value=f"{gcc_value:.4f}")

    # Visual feedback: a small color box showing the average color
    st.write("Average Color Preview:")
    st.markdown(
        f'<div style="width:100%; height:50px; background-color:rgb({avg_r},{avg_g},{avg_b}); border-radius:10px; border: 1px solid #ddd;"></div>', 
        unsafe_allow_html=True
    )