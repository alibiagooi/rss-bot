import requests
import xml.etree.ElementTree as ET
import telegram
import time
import os
from telegram import ParseMode

# تنظیمات اولیه
TOKEN = ""  # توکن باتت رو اینجا بذار
CHANNEL_ID = "@alkawtharrrrr"  # اسم کانالت رو اینجا بذار (با @)
RSS_URL = "https://www.alkawthartv.ir/rss/latest"  # آدرس فید RSS رو اینجا بذار
CHECK_INTERVAL = 15 * 60  # 15 دقیقه به ثانیه

# مسیر فایل برای ذخیره لینک‌های قبلی
SEEN_LINKS_FILE = "seen_links.txt"

# بات تلگرام رو راه‌اندازی کن
bot = telegram.Bot(token=TOKEN)

# خوندن لینک‌های قبلی از فایل
def load_seen_links():
    if os.path.exists(SEEN_LINKS_FILE):
        with open(SEEN_LINKS_FILE, "r") as file:
            return set(file.read().splitlines())
    return set()

# ذخیره لینک جدید توی فایل
def save_seen_link(link):
    with open(SEEN_LINKS_FILE, "a") as file:
        file.write(link + "\n")

# گرفتن و پردازش فید XML
def parse_rss_feed():
    try:
        response = requests.get(RSS_URL, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        items = []
        for item in root.findall(".//item"):
            entry = {
                "title": item.find("title").text if item.find("title") is not None else "",
                "link": item.find("link").text if item.find("link") is not None else "",
                "description": item.find("description").text if item.find("description") is not None else "",
                "image": item.find("image").text if item.find("image") is not None else ""
            }
            items.append(entry)
        return items
    except Exception as e:
        print(f"خطا در گرفتن فید: {e}")
        return []

# فرستادن پست به کانال
def send_post(entry):
    title = entry["title"]
    description = entry["description"]
    link = entry["link"]
    image = entry["image"]

    print(f"لینک عکس پیدا شده: {image}")

    # لینک اصلی بدون تغییر برای href
    message = (
        f"<b>🔶 {title}</b>\n\n"
        f"<blockquote>{description}</blockquote>\n\n"
        f"<a href='{link}'>🌐اضغط هنا لمشاهدة المزيد من هذا البرنامج</a>\n\n"
        f"@alkawthartv\n\n"
        f"🔶الكوثر\n\n"
        f"🔸معين لاينضب🔸\n\n"
    )

    if image and image.strip():
        try:
            # برای غیرفعال کردن پیش‌نمایش، یه پیام جدا با لینک خام می‌فرستیم و بعد حذف می‌کنیم
            bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=image,
                caption=message,
                parse_mode=ParseMode.HTML
            )
            print("پست با عکس ارسال شد.")
        except telegram.error.BadRequest as e:
            print(f"خطا در ارسال عکس: {e}")
            bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.HTML
            )
    else:
        bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )
        print("پست بدون عکس ارسال شد.")

# چک کردن فید و ارسال پست‌ها
def check_feed():
    seen_links = load_seen_links()
    entries = parse_rss_feed()

    if not entries:
        print("هیچ ورودی‌ای توی فید پیدا نشد.")
        return

    for entry in reversed(entries):
        link = entry["link"]
        if link not in seen_links:
            send_post(entry)
            save_seen_link(link)
            time.sleep(2)

# حلقه اصلی
def main():
    print("بات شروع به کار کرد...")
    while True:
        try:
            check_feed()
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"خطا: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
