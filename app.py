import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🔁 Update Stok Shopee dari File Copybar")

# Fungsi baca file mass update Shopee
def read_mass_update(file):
    try:
        # Langsung baca semua sheet tanpa header biar gak ngacau
        df = pd.read_excel(file, header=None, dtype=str)

        # Potong dataframe dari baris ke-7 ke bawah (index 6)
        df = df.iloc[6:, :].reset_index(drop=True)

        # Ambil kolom E dan F (kolom ke-4 dan ke-5, karena index mulai dari 0)
        sku_col_e = df.iloc[:, 4]
        sku_col_f = df.iloc[:, 5]

        # Tentukan SKU-nya sesuai prioritas
        def resolve_sku(e, f):
            if pd.isna(e) and pd.isna(f):
                return 'no sku'
            elif pd.notna(e) and str(e).strip() != '':
                return str(e).split('.')[0].zfill(7).strip()
            elif pd.notna(f) and str(f).strip() != '':
                return str(f).split('.')[0].zfill(7).strip()
            else:
                return 'no sku'

        df['SKU'] = [resolve_sku(e, f) for e, f in zip(sku_col_e, sku_col_f)]

        return df[['SKU']]
    except Exception as e:
        st.error(f"❌ Gagal membaca file mass update: {e}")
        return None

# Fungsi baca file copybar yang dikonversi CSV
def read_reference(file):
    try:
        try:
            df_raw = pd.read_csv(file, header=None, dtype=str)
        except pd.errors.ParserError:
            file.seek(0)
            df_raw = pd.read_csv(file, header=None, delimiter=';', dtype=str)

        # Ambil mulai baris kedua (index 1), kolom A (0) dan C (2)
        df = df_raw.iloc[1:, [0, 2]]
        df.columns = ["SKU", "Stok"]
        df["SKU"] = df["SKU"].astype(str).str.zfill(7).str.strip()
        df["Stok"] = df["Stok"].astype(str).str.strip()
        df.dropna(subset=["SKU", "Stok"], inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file referensi: {e}")
        return None

# Fungsi pencocokan
def match_stok(mass_update_df, reference_df):
    result = mass_update_df.copy()
    stok_dict = dict(zip(reference_df["SKU"], reference_df["Stok"]))
    result["Stok"] = result["SKU"].apply(lambda sku: stok_dict.get(sku, "SKU tidak ditemukan"))
    return result

# Upload file mass update
mass_file = st.file_uploader("📤 Upload file mass update Shopee (.xlsx)", type=["xlsx"])
# Upload file copybar
ref_file = st.file_uploader("📤 Upload file copybar hasil convert CSV", type=["csv"])

if mass_file and ref_file:
    with st.spinner("🔍 File berhasil dibaca. Mencocokkan SKU..."):
        df_mass = read_mass_update(mass_file)
        df_ref = read_reference(ref_file)

        if df_mass is not None and df_ref is not None:
            result_df = match_stok(df_mass, df_ref)

            st.subheader("🔍 Hasil Pencocokan:")
            st.dataframe(result_df)

            # Convert ke Excel dan download
            output = BytesIO()
            result_df.to_excel(output, index=False)
            st.download_button(
                label="📥 Download Hasil SKU & Stok",
                data=output.getvalue(),
                file_name="hasil_stok_shopee.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
