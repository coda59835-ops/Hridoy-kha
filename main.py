import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def get_free_numbers():
    url = "https://receive-smss.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        numbers = []
        for a_tag in soup.find_all("a", href=True):
            if "/user/" in a_tag['href'] or "/phone/" in a_tag['href']:
                num = a_tag.text.strip()
                if num and num not in numbers:
                    numbers.append(num)
        return numbers[:5]
    except Exception:
        return []

def get_latest_otp(phone_number):
    clean_number = "".join(filter(str.isdigit, phone_number))
    url = f"https://receive-smss.com/sms/{clean_number}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        messages = []
        rows = soup.find_all("tr")
        for row in rows[1:6]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                sender = cols[0].text.strip()
                message_body = cols[1].text.strip()
                time_sent = cols[2].text.strip()
                messages.append(f"📩 From: {sender}\n💬 SMS: {message_body}\n⏱ Time: {time_sent}")
        return messages
    except Exception:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("স্বাগতম! ফ্রি নম্বর দেখতে /numbers লিখুন।")

async def show_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 নম্বর লোড হচ্ছে...")
    numbers = get_free_numbers()
    if numbers:
        num_list = "\n".join([f"📱 {num}" for num in numbers])
        reply = f"✅ নম্বরসমূহ:\n{num_list}\n\nOTP দেখতে লিখুন:\n/otp <নম্বর>"
    else:
        reply = "❌ নম্বর পাওয়া যায়নি।"
    await update.message.reply_text(reply)

async def show_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ উদাহরণ: /otp +12025550143")
        return
    phone_number = context.args[0]
    await update.message.reply_text("🔄 মেসেজ চেক করা হচ্ছে...")
    sms_list = get_latest_otp(phone_number)
    if sms_list:
        reply = "\n\n---\n\n".join(sms_list)
    else:
        reply = "❌ কোনো মেসেজ পাওয়া যায়নি।"
    await update.message.reply_text(reply)

if name == "main":
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # 8719156096:AAGIEvv9f4hh8Yw3-Rc8rJ1jicoh1SePnsY
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("numbers", show_numbers))
    app.add_handler(CommandHandler("otp", show_otp))
    app.run_polling()
