import time
import os
import sys

for j in range(3):  # 3 marta takrorlanadi
    for i in range(5):  # 0 dan 5 gacha — 6 marta bosqich
        # har safar eski qatordan tozalaydi va yangisini qayta yozadi
        sys.stdout.write("\r" + " " * 30 + "\r")  
        sys.stdout.write("Yuklanmoqda" + "." * i)  
        sys.stdout.flush()
        time.sleep(0.4)
    time.sleep(0.5)

# qatordan tozalab, yakuniy xabarni chiqaradi
sys.stdout.write("\r" + " " * 30 + "\r")
print("✅ Yuklash tugadi! Fayl ishga tushdi 🚀")

time.sleep(1)
os.system("python Download/menki.py")