import streamlit as st
import pandas as pd
import os

from utils.loader import load_document
from utils.extractor import extract_metadata

st.set_page_config(page_title="TPA AI Reviewer", layout="wide")

st.title("📄 TPA AI Contract Reviewer")

uploaded_file = st.file_uploader(
    "Upload TPA Agreement (PDF / DOCX)",
    type=["pdf", "docx"]
)

if uploaded_file:
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    file_path = f"data/uploads/{uploaded_file.name}"

    # Save uploaded file always
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Saved to data/uploads/{uploaded_file.name}")

    if st.button("🔍 Extract Metadata"):
        with st.spinner("Analyzing contract..."):
            documents = load_document(file_path)
            metadata = extract_metadata(documents)

            new_row = pd.DataFrame([metadata.model_dump()])

            output_path = "data/output/tpa_metadata.xlsx"

            if os.path.exists(output_path):
                existing_df = pd.read_excel(output_path)
                final_df = pd.concat([existing_df, new_row], ignore_index=True)
            else:
                final_df = new_row

            final_df.to_excel(output_path, index=False)

            st.subheader("📊 Latest Extracted Metadata")
            st.dataframe(new_row)

            st.download_button(
                "⬇ Download Full Excel",
                data=open(output_path, "rb"),
                file_name="tpa_metadata.xlsx"
            )