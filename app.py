import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Update Stok Shopee", layout="centered")
st.title("🛍️ Update Stok Otomatis untuk Shopee")

st.markdown("Upload file referensi **(CSV)** dan file mass update **Shopee (XLSX)**")

# Upload file referensi CSV
ref_file = st.file_uploader("📦 File Referensi Stok (.csv)", type=["csv"])

# Upload file mass update dari Shopee
mass_file = st.file_uploader("🛒 File Mass Update Shopee (.xlsx)", type=["xlsx"])


def read_reference(file):
    try:
        df = pd.read_csv(file, sep=None, engine="python")  # fleksibel terhadap delimiter
        df.columns = df.columns.str.strip()

        if not {'SKU', 'Stok'}.issubset(df.columns):
            st.error("❌ File referensi harus punya kolom 'SKU' dan 'Stok'")
            return None

        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file referensi: {e}")
        return None


def read_massupdate(file):
    try:
        with pd.ExcelFile(file, engine="openpyxl") as xls:
            df = pd.read_excel(xls, header=None, skiprows=6)  # sesuai template Shopee
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file mass update: {e}")
        return None


def update_stock(reference_df, mass_df):
    updated_df = mass_df.copy()
    for idx, row in updated_df.iterrows():
        sku = str(row[1]).strip()
        stok_baru = reference_df.loc[reference_df['SKU'].astype(str).str.strip() == sku, 'Stok']
        if not stok_baru.empty:
            updated_df.at[idx, 3] = stok_baru.values[0]
    return updated_df


def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False)
    output.seek(0)
    return output


if ref_file and mass_file:
    reference_df = read_reference(ref_file)
    mass_df = read_massupdate(mass_file)

    if reference_df is not None and mass_df is not None:
        st.success("✅ File berhasil dibaca. Sedang memperbarui stok...")
        updated_df = update_stock(reference_df, mass_df)

        st.dataframe(updated_df.head(10))

        # Download link
        output = convert_df_to_excel(updated_df)
        st.download_button(
            label="⬇️ Download File Mass Update yang Sudah Diperbarui",
            data=output,
            file_name="updated_mass_update.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )