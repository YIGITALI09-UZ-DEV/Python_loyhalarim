# it test bot tokioni ishlatilgan
# telgram_matka_bot.py
# Kerakli kutubxonani pip orqali o'rnating:
# pip install pyTelegramBotAPI

import telebot
import random
import time

TOKEN = "8048163046:AAHIVLcD1rIHBcYhPl7ip5nTXR5ik9CgkVs"  # <-- bu yerga o'z bot tokeningizni yozing
bot = telebot.TeleBot(TOKEN)

# Har bir foydalanuvchi uchun holat (in-memory). Deployda fayl yoki DB bilan almashtirish mumkin.
users = {}

# Yordamchi: yangi holat yaratish
def new_state(user_id):
    users[user_id] = {
        "stage": "start",            # qayerda ekanligi: start, choosing_time, choosing_count, testing, finished
        "category": None,            # "1-5", "5-11", "yuqori"
        "time_limit": None,          # soniya
        "count": None,               # misollar soni
        "questions": [],             # [{q: "1+1", a: 2, sent_at: timestamp, answered: False, correct: None}, ...]
        "index": 0,                  # hozirgi savol indeksi
        "correct": 0,
        "incorrect": 0
    }

# Savol generator: kategoriya va oddiy darajaga qarab savol beradi
def generate_question(category):
    if category == "1-5":
        # kichik sonlar, qo'shish/ayirish
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(["+", "-"])
        q = f"{a} {op} {b}"
        a_ans = eval(q)
        return q, a_ans
    elif category == "5-11":
        # ko'paytirish va bo'lish ham qo'shiladi
        op = random.choice(["+", "-", "*", "/"])
        if op == "*":
            a = random.randint(2, 12)
            b = random.randint(2, 12)
            q = f"{a} * {b}"
            a_ans = a * b
            return q, a_ans
        elif op == "/":
            b = random.randint(2, 12)
            ans = random.randint(1, 12)
            a = b * ans
            q = f"{a} / {b}"
            a_ans = ans
            return q, a_ans
        else:
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            q = f"{a} {op} {b}"
            a_ans = eval(q)
            return q, a_ans
    else:  # yuqori (maktabdan yuqori)
        # arifmetik va oddiy algebra shaklida (ikkita operandli)
        op = random.choice(["+", "-", "*", "/", "^"])
        if op == "^":
            a = random.randint(2, 6)
            b = random.randint(2, 3)
            q = f"{a}^{b}"
            a_ans = a ** b
            return q, a_ans
        elif op == "/":
            b = random.randint(2, 15)
            ans = random.randint(2, 15)
            a = b * ans
            q = f"{a} / {b}"
            a_ans = ans
            return q, a_ans
        else:
            a = random.randint(1, 200)
            b = random.randint(1, 200)
            q = f"{a} {op} {b}"
            # python uchun ^ emas, ^ yozilganida maxsus berilmagan, lekin biz ^ni yuqorida qaytardik
            if op == "+":
                a_ans = a + b
            elif op == "-":
                a_ans = a - b
            elif op == "*":
                a_ans = a * b
            return q, a_ans

# /start komandasi
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    new_state(user_id)
    users[user_id]["stage"] = "choosing_category"
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("1-5 sinf", "5-11 sinf")
    markup.row("Yuqori talabalar")
    bot.send_message(user_id, "Salom! 👋\nKategoriya tanlang:", reply_markup=markup)

# Matnli xabarlarni tutamiz (menyular va javoblar)
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text.strip()
    if user_id not in users:
        new_state(user_id)

    state = users[user_id]["stage"]

    # 1) Kategoriya tanlash
    if state == "choosing_category":
        if text in ["1-5 sinf", "5-11 sinf", "Yuqori talabalar"]:
            if text == "1-5 sinf":
                users[user_id]["category"] = "1-5"
            elif text == "5-11 sinf":
                users[user_id]["category"] = "5-11"
            else:
                users[user_id]["category"] = "yuqori"
            users[user_id]["stage"] = "choosing_time"
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.row("5 sekund", "10 sekund", "30 sekund")
            bot.send_message(user_id, "Har bir savolga nechchi sekund ajratilsin?", reply_markup=markup)
        else:
            bot.send_message(user_id, "Iltimos kategoriya tanlang: 1-5 sinf, 5-11 sinf yoki Yuqori talabalar.")

    # 2) Vaqt tanlash
    elif state == "choosing_time":
        if text in ["5 sekund", "10 sekund", "30 sekund"]:
            users[user_id]["time_limit"] = int(text.split()[0])
            users[user_id]["stage"] = "choosing_count"
            bot.send_message(user_id, "Nechta misol bo‘lishi kerak? (raqam kiriting, masalan: 5)")
        else:
            bot.send_message(user_id, "Iltimos 5, 10 yoki 30 sekunddan birini tanlang.")

    # 3) Nechta misol kiritish
    elif state == "choosing_count":
        if text.isdigit() and 1 <= int(text) <= 100:
            users[user_id]["count"] = int(text)
            users[user_id]["stage"] = "testing"
            # savollarni oldindan yaratamiz
            qlist = []
            for _ in range(users[user_id]["count"]):
                q, a = generate_question(users[user_id]["category"])
                qlist.append({"q": q, "a": a, "sent_at": None, "answered": False, "correct": None})
            users[user_id]["questions"] = qlist
            users[user_id]["index"] = 0
            users[user_id]["correct"] = 0
            users[user_id]["incorrect"] = 0
            bot.send_message(user_id, f"Test boshlanmoqda — {users[user_id]['count']} ta savol. Har bir savolga {users[user_id]['time_limit']} sekund. Javobni raqam yoki ifoda sifatida yozing.")
            send_next_question(user_id)
        else:
            bot.send_message(user_id, "Iltimos haqiqiy raqam kiriting (1 dan 100 gacha).")

    # 4) Test davomida — foydalanuvchi javob yozadi
    elif state == "testing":
        handle_answer(message)

    else:
        bot.send_message(user_id, "Boshlash uchun /start buyrug'ini bering.")

# Savol yuborish funktsiyasi
def send_next_question(user_id):
    st = users[user_id]
    idx = st["index"]
    if idx >= st["count"]:
        finish_test(user_id)
        return

    qobj = st["questions"][idx]
    q_text = qobj["q"]
    bot.send_message(user_id, f"✅ Savol {idx+1}/{st['count']}:\n{q_text}\n(Iltimos javobni yozing.)")
    # yuborilgan vaqtni saqlaymiz
    st["questions"][idx]["sent_at"] = time.time()
    # savol hali javobsiz
    st["questions"][idx]["answered"] = False

# Javobni qabul qilish va tekshirish
def handle_answer(message):
    user_id = message.from_user.id
    text = message.text.strip()
    st = users[user_id]
    idx = st["index"]
    if idx >= st["count"]:
        finish_test(user_id)
        return

    qobj = st["questions"][idx]
    # vaqtni tekshirish
    now = time.time()
    sent_at = qobj.get("sent_at") or now
    allowed = st["time_limit"]
    time_passed = now - sent_at

    # agar allaqachon javob berilgan bo'lsa, ogohlantiramiz
    if qobj["answered"]:
        bot.send_message(user_id, "Bu savolga allaqachon javob berdingiz. Keyingisiga o‘tamiz.")
        return

    # Agar vaqt tugagan bo'lsa — noto'g'ri hisoblaymiz
    if time_passed > allowed:
        qobj["answered"] = True
        qobj["correct"] = False
        st["incorrect"] += 1
        bot.send_message(user_id, f"⏱ Vaqt tugadi! Bu savol noto'g'ri hisoblandi.\nTo‘g‘ri javob: {qobj['a']}")
        st["index"] += 1
        send_next_question(user_id)
        return

    # endi foydalanuvchi javobini tekshiramiz
    # raqam bilan yoki oddiy ifoda bilan kiritilishi mumkin
    user_ans = None
    try:
        # avval butun yoki onlik son sifatida
        if "/" in text:
            # misol: "6/2" yoki "3/2"
            parts = text.split("/")
            user_ans = float(parts[0]) / float(parts[1])
        else:
            # sinab ko'ramiz — agar butun yoki onlik bo'lsa
            user_ans = float(text)
    except Exception:
        # agar ifoda kiritilgan bo'lsa (masalan "2+3"), eval qilish xavfsiz emas,
        # lekin oddiy arithmeticni qo'llab ko'rish uchun cheklangan eval qilamiz.
        try:
            # faqat raqam va +-*/ va bo'shliq belgilariga ruxsat beramiz
            allowed_chars = "0123456789+-*/. ()"
            if all(ch in allowed_chars for ch in text):
                user_ans = eval(text)
            else:
                user_ans = None
        except Exception:
            user_ans = None

    correct_ans = qobj["a"]
    correct_flag = False
    if user_ans is not None:
        # butun va float solishtirishda kichik farqga ruxsat beramiz
        try:
            if abs(float(user_ans) - float(correct_ans)) < 1e-6:
                correct_flag = True
        except Exception:
            correct_flag = False

    qobj["answered"] = True
    qobj["correct"] = bool(correct_flag)
    if correct_flag:
        st["correct"] += 1
        bot.send_message(user_id, "✔️ To‘g‘ri!")
    else:
        st["incorrect"] += 1
        bot.send_message(user_id, f"❌ Noto‘g‘ri. To‘g‘ri javob: {correct_ans}")

    st["index"] += 1
    # keyingi savolni yuboramiz
    # kichik kutishdan so'ng — bevosita yuborish ham mumkin
    send_next_question(user_id)

# Test yakunlanishi
def finish_test(user_id):
    st = users[user_id]
    total = st["count"]
    correct = st["correct"]
    incorrect = st["incorrect"]
    bot.send_message(user_id, f"🎉 Test yakunlandi!\nSiz {total} ta savoldan:\n✔️ To‘g‘ri: {correct}\n❌ Noto‘g‘ri: {incorrect}")
    # holatni qayta boshlash uchun /start ni takrorlashni so'raymiz
    users[user_id]["stage"] = "finished"
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.row("/start")
    bot.send_message(user_id, "Yana o‘ynash uchun /start bosing.", reply_markup=markup)

# Botni polling rejimida ishga tushuramiz
if __name__ == "__main__":
    print("Bot ishga tushmoqda...")
    bot.infinity_polling()