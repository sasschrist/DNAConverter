# app.py
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="DNA β-Value Converter", layout="wide")

st.title("🧬 DNA β-Value Converter")
st.write("Upload DNA/genomics files (.idat, .tz, .vcf, .bed, .csv, etc.) to extract β-values and download as TXT/CSV.")

uploaded_file = st.file_uploader("Upload your file", type=None)

def parse_file(file, filename):
    # ⚠️ Demo parser — only supports CSV/TSV for now
    if filename.endswith(".csv") or filename.endswith(".tsv"):
        df = pd.read_csv(file, sep="," if filename.endswith(".csv") else "\t")
    else:
        raise ValueError("Unsupported format in demo (only CSV/TSV supported yet).")
    return df

if uploaded_file:
    try:
        df = parse_file(uploaded_file, uploaded_file.name)
        st.success(f"✅ File loaded: {uploaded_file.name}")
        st.write("Preview of extracted values:")
        st.dataframe(df.head(20))

        export_as = st.radio("Export as:", ["TXT", "CSV"])
        if st.button("Download"):
            output = io.BytesIO()
            if export_as == "CSV":
                df.to_csv(output, index=False)
                mime = "text/csv"
                fname = "beta_values.csv"
            else:
                df.to_csv(output, index=False, sep="\t")
                mime = "text/plain"
                fname = "beta_values.txt"
            st.download_button("📥 Save File", data=output.getvalue(), file_name=fname, mime=mime)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
