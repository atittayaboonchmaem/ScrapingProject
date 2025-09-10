from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time

# -------------------------
# 1. เปิดเว็บด้วย Chrome
# -------------------------
driver = webdriver.Chrome()
driver.get("https://www.carsome.co.th/buy-car/toyota")
time.sleep(5)  # รอโหลด

data = []

# -------------------------
# 2. วนลูปดึงทุกหน้า
# -------------------------
while True:
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # เจาะการ์ดแต่ละอัน
    car_cards = soup.find_all("div", class_="list-card__item")

    for car in car_cards:
        # ลิงก์ + ชื่อ
        link_tag = car.find("a", class_="mod-b-card__title")
        link = "https://www.carsome.co.th" + link_tag['href'] if link_tag else ""
        title_texts = [p.get_text(strip=True) for p in link_tag.find_all("p")] if link_tag else []

        # แยกเป็น ปี+ยี่ห้อ และ รุ่น
        year_brand = title_texts[0] if len(title_texts) > 0 else ""
        model = title_texts[1] if len(title_texts) > 1 else ""

        # ✅ จัดให้ model เป็นบรรทัดเดียว
        model = " ".join(model.split())

        # เลขไมล์ / เกียร์ / จังหวัด
        other_info = car.find("div", class_="mod-b-card__car-other")
        if other_info:
            spans = [s.get_text(strip=True) for s in other_info.find_all("span")]
            mileage = spans[0] if len(spans) > 0 else ""
            transmission = spans[1] if len(spans) > 1 else ""
            location = spans[2] if len(spans) > 2 else ""
        else:
            mileage, transmission, location = "", "", ""

        # ราคา
        price_tag = car.find("div", class_="mod-card__price__total")
        price = price_tag.get_text(strip=True) if price_tag else ""

        # ผ่อนต่อเดือน
        monthly_tag = car.find("div", class_="mod-tooltipMonthPay")
        monthly = monthly_tag.get_text(strip=True) if monthly_tag else ""

        

        # เก็บข้อมูล
        data.append({
            "year_brand": year_brand,
            "model": model,
            "link": link,
            "mileage": mileage,
            "transmission": transmission,
            "location": location,
            "price": price,
            "monthly": monthly
        })

    # -------------------------
    # 3. เช็คปุ่ม next
    # -------------------------
    try:
        next_button = driver.find_element(By.XPATH, '//a[@rel="next"]')
        next_button.click()
        time.sleep(5)
    except NoSuchElementException:
        break  # ไม่มี next → ออกลูป

# -------------------------
# 4. บันทึก CSV
# -------------------------
df = pd.DataFrame(data)
df.to_csv("toyota_carsome.csv", index=False, encoding="utf-8-sig")
print(f"Saved CSV: {len(df)} cars found.")

driver.quit()
