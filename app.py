import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Stok Updater", layout="wide")
st.title("📦 Shopee Mass Update - Penyesuaian Stok Berdasarkan Copybar")

copybar_file = st.file_uploader("📤 Upload file referensi (copybar) [.xls, .xlsx, .csv]", type=["xls", "xlsx", "csv"])
massupdate_file = st.file_uploader("📤 Upload file Shopee Mass Update [.xlsx]", type=["xlsx"])

def read_copybar(file):
    try:
        if file.name.endswith(".csv"):
            return pd.read_csv(file, header=None)
        elif file.name.endswith(".xls"):
            return pd.read_excel(file, header=None, engine='xlrd')
        elif file.name.endswith(".xlsx"):
            return pd.read_excel(file, header=None, engine='openpyxl')
        else:
            raise ValueError("Format file tidak didukung")
    except Exception as e:
        st.error(f"❌ Gagal membaca file referensi: {e}")
        return None

def read_massupdate(file):
    try:
        # Baca tanpa parsing view settings untuk menghindari 'activePane' error
        df = pd.read_excel(file, header=None, skiprows=6, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file mass update: {e}")
        return None

if copybar_file and massupdate_file:
    df_ref = read_copybar(copybar_file)
    df_update = read_massupdate(massupdate_file)

    if df_ref is not None and df_update is not None:
        try:
            # Ambil kolom SKU (A) dan stok (C) dari baris kedua dan set nama kolom
            df_ref = df_ref.iloc[1:, [0, 2]]
            df_ref.columns = ["SKU", "Stok"]
            df_ref.dropna(subset=["SKU"], inplace=True)
            df_ref["SKU"] = df_ref["SKU"].astype(str).str.strip()

            # Ambil SKU dari kolom E (index 4) dan update kolom H (index 7)
            df_update["SKU"] = df_update.iloc[:, 4].astype(str).str.strip()
            df_update["stok_baru"] = df_update["SKU"].map(dict(zip(df_ref["SKU"], df_ref["Stok"])))

            df_update.iloc[:, 7] = df_update["stok_baru"]
            df_update.iloc[:, 7].fillna("SKU tidak ditemukan", inplace=True)

            st.success("✅ Proses berhasil. Data siap diunduh.")
            st.dataframe(df_update.iloc[:, [4, 7]])

            output = BytesIO()
            df_update.to_excel(output, index=False, header=False, engine='openpyxl')
            st.download_button("⬇️ Unduh hasil update", data=output.getvalue(), file_name="hasil_update.xlsx")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat memproses file: {e}")
else:
    st.info("📁 Silakan unggah kedua file untuk mulai memproses.")
