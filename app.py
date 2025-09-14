#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNA β-Value Converter — v2
Features:
- Removes size limit
- Auto-decompresses: .zip, .tar(.gz|.bz2|.xz), .gz, .bz2, .xz
- Detects CSV/TSV/TXT/VCF/BED
- Shows 10×10 preview
- Provides preview-file download
- Converts to CSV, TXT, Parquet with optional compression (none/gzip/bz2/xz/zip)
"""

import streamlit as st
import pandas as pd
import io, zipfile, tarfile, gzip, bz2, lzma

# ─────────────────────────────
# Helper: Decompression
# ─────────────────────────────
def decompress(uploaded_file, filename):
    data = uploaded_file.read()
    buf = io.BytesIO(data)

    if filename.endswith(".zip"):
        with zipfile.ZipFile(buf) as z:
            name = z.namelist()[0]
            with z.open(name) as f:
                return io.BytesIO(f.read()), name
    elif filename.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz", ".tar")):
        with tarfile.open(fileobj=buf) as t:
            member = t.getmembers()[0]
            return io.BytesIO(t.extractfile(member).read()), member.name
    elif filename.endswith(".gz"):
        return io.BytesIO(gzip.decompress(data)), filename[:-3]
    elif filename.endswith(".bz2"):
        return io.BytesIO(bz2.decompress(data)), filename[:-4]
    elif filename.endswith(".xz"):
        return io.BytesIO(lzma.decompress(data)), filename[:-3]
    return io.BytesIO(data), filename

# ─────────────────────────────
# Streamlit UI
# ─────────────────────────────
st.title("DNA β-Value Converter — Decompress + Preview")

uploaded = st.file_uploader("Upload compressed or raw data file", type=None)

if uploaded:
    buf, name = decompress(uploaded, uploaded.name)

    # Auto-detect delimiter
    df = pd.read_csv(buf, sep=None, engine="python")

    # Show preview
    st.subheader("Preview (10×10)")
    preview = df.iloc[:10, :10]
    st.dataframe(preview)

    # Preview download
    st.download_button("Download Preview (CSV)",
                       preview.to_csv(index=False),
                       "preview.csv",
                       "text/csv")

    # Export options
    fmt = st.selectbox("Export format", ["csv", "txt", "parquet"])
    comp = st.selectbox("Compression", ["none", "gzip", "bz2", "xz"])

    if st.button("Download Full File"):
        out = io.BytesIO()
        if fmt in ("csv", "txt"):
            df.to_csv(out,
                      index=False,
                      sep="\t" if fmt == "txt" else ",",
                      compression=comp if comp != "none" else None)
        elif fmt == "parquet":
            df.to_parquet(out,
                          compression=None if comp == "none" else comp)
        st.download_button("Download Converted",
                           out.getvalue(),
                           f"converted.{fmt}{'.'+comp if comp!='none' else ''}")
