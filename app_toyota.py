# import streamlit as st
# import pandas as pd

# # ===============================
# # โหลดข้อมูลจากไฟล์ CSV ที่ scrap_toyota.py สร้างไว้
# # ===============================
# @st.cache_data
# def load_data():
#     try:
#         df = pd.read_csv("toyota_carsome.csv")
#     except FileNotFoundError:
#         st.error("ไม่พบไฟล์ toyota_carsome.csv กรุณารัน scrape_toyota.py ก่อน")
#         return pd.DataFrame()
#     return df

# df = load_data()

# st.title("🚗 ค้นหารถ Toyota")
# st.write("ใส่งบประมาณของคุณเพื่อดูว่ารถรุ่นใดสามารถซื้อได้")

# if not df.empty:
#     # สมมติว่ามีคอลัมน์: name, price, link
#     # แปลงราคาให้เป็นตัวเลข ('บาท' หรือ ',' )
#     df['price_clean'] = (
#         df['price']
#         .astype(str)
#         .str.replace(r"[^\d]", "", regex=True)
#         .astype(float)
#     )

#     with st.form(key='budget_form'):
#         budget = st.number_input('งบประมาณของคุณ (บาท)', min_value=0, value=1000000, step=50000)
#         submit_button = st.form_submit_button(label='ค้นหา')

#     if submit_button:
#         filtered = df[df['price_clean'] <= budget]

#         if not filtered.empty:
#             st.subheader("รถที่สามารถซื้อได้ตามงบของคุณ:")
#             st.dataframe(filtered.reset_index(drop=True))
#         else:
#             st.warning("ไม่มีรถที่ตรงกับงบและตัวกรองของคุณ")
# else:
#     st.stop()

import streamlit as st
import pandas as pd

# ===============================
# ฟังก์ชันโหลดข้อมูลจากไฟล์ CSV
# ===============================
@st.cache_data
def load_data():
    try:
        # พยายามอ่านไฟล์ข้อมูลรถที่ดึงมาจาก scrape_toyota.py
        df = pd.read_csv("toyota_carsome.csv")
    except FileNotFoundError:
        # ถ้าไม่มีไฟล์ → แจ้งเตือนผู้ใช้
        st.error("ไม่พบไฟล์ toyota_carsome.csv กรุณารัน scrape_toyota.py ก่อน")
        return pd.DataFrame()

    # ลบแถวที่ไม่มี year_brand หรือ price (ข้อมูลไม่สมบูรณ์)
    df = df.dropna(subset=["year_brand", "price"])

    # -------------------------------
    # clean คอลัมน์ราคา → ตัวเลข float
    # -------------------------------
    df["price_clean"] = (
        df["price"].astype(str)                 # แปลงเป็น string
        .str.replace(r"[^\d]", "", regex=True)  # เก็บเฉพาะตัวเลข
        .astype(float)                          # แปลงเป็น float
    )

    # -------------------------------
    # clean ค่าผ่อนต่อเดือน → float
    # -------------------------------
    df["monthly_clean"] = (
        df["monthly"].astype(str)
        .str.replace(r"[^\d]", "", regex=True)
        .astype(float)
    )

    # -------------------------------
    # clean เลขไมล์ (กิโลเมตร) → float
    # -------------------------------
    df["mileage_clean"] = (
        df["mileage"].astype(str)
        .str.replace(r"[^\d]", "", regex=True)  # เก็บเฉพาะตัวเลข
        .replace("", "0")                       # ถ้าว่างให้แทนเป็น 0
        .astype(float)
    )

    return df


# โหลดข้อมูลเข้ามาใช้งาน
df = load_data()

# -------------------------------
# ส่วน UI ของ Streamlit
# -------------------------------
st.title("🚗 ค้นหารถ Toyota")
st.write("ใส่งบประมาณของคุณและเลือกเกียร์เพื่อดูว่ารถรุ่นใดสามารถซื้อได้")

# -------------------------------
# ถ้ามีข้อมูล → แสดงฟอร์มให้ผู้ใช้กรอง
# -------------------------------
if not df.empty:
    with st.form(key='budget_form'):
        # รับงบประมาณจากผู้ใช้
        budget = st.number_input('งบประมาณของคุณ (บาท)', min_value=0, value=1000000, step=50000)

        # เลือกเกียร์
        transmission = st.selectbox(
            'เกียร์',
            ['ทั้งหมด', 'อัตโนมัติ', 'ธรรมดา']
        )

        # ปุ่มกดค้นหา
        submit_button = st.form_submit_button(label='ค้นหา')

    # -------------------------------
    # เมื่อกดปุ่มค้นหา → กรองข้อมูล
    # -------------------------------
    if submit_button:
        # กรองตามงบประมาณ
        filtered = df[df['price_clean'] <= budget]

        # กรองตามประเภทเกียร์
        if transmission != 'ทั้งหมด':
            if transmission == 'อัตโนมัติ':
                filtered = filtered[filtered['transmission'].str.contains("อัตโนมัต", case=False, na=False)]
            elif transmission == 'ธรรมดา':
                filtered = filtered[filtered['transmission'].str.contains("ธรรมดา", case=False, na=False)]

        # -------------------------------
        # แสดงผลลัพธ์
        # -------------------------------
        if not filtered.empty:
            st.subheader("รถที่สามารถซื้อได้ตามงบและตัวกรองของคุณ:")
            st.dataframe(
                filtered[["year_brand","model", "mileage", "transmission", "location", "price", "monthly", "link"]]
                .reset_index(drop=True)
            )
        else:
            st.warning("ไม่มีรถที่ตรงกับงบและตัวกรองของคุณ")
else:
    # ถ้าโหลดข้อมูลไม่สำเร็จ → หยุดโปรแกรม
    st.stop()

