import random
import os
g = int(input("1 to‘g‘ri javobga nechi baldan 1 / 5 / 10\n"))
n = 0
os.system('cls' if os.name == 'nt' else 'clear')  # eski ekranni tozalaydi

while True:

    a = random.randint(10, 100)
    b = random.randint(10,30)
    c = a + b
    if n < 0:
        print("O‘yin Tugadi siz (-) ga o‘tib ketingiz 😓\n\n")
        break
        
    print(f"{a} + {b} Nechi bo‘ladi ?")
    y = int(input("Javob ->> "))
    if c == y:
        print(f"Javob to‘g‘ri ✔️️ {c} ")
        n += g
        print(f"Sizdagi bal {n}")
    elif c != y:
        n -= g
        print(f"Javob xato  ❌\n To‘g‘ri Javob {c}\n Sizda qolgan BAL > {n}")