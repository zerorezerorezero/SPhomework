import threading
import time

INITIAL_BALANCE = 0
DEPOSIT_COUNT = 100000
WITHDRAW_COUNT = 100000

bank_balance = INITIAL_BALANCE
lock = threading.Lock()


def deposit(amount):
    global bank_balance
    for _ in range(DEPOSIT_COUNT):
        bank_balance += amount


def withdraw(amount):
    global bank_balance
    for _ in range(WITHDRAW_COUNT):
        bank_balance -= amount


def deposit_safe(amount):
    global bank_balance
    for _ in range(DEPOSIT_COUNT):
        with lock:
            bank_balance += amount


def withdraw_safe(amount):
    global bank_balance
    for _ in range(WITHDRAW_COUNT):
        with lock:
            bank_balance -= amount


def run_without_mutex():
    global bank_balance
    bank_balance = INITIAL_BALANCE
    print("=" * 60)
    print("[實驗 1] 不使用 Mutex — 預期會發生 Race Condition")
    print(f"存款 {DEPOSIT_COUNT} 次, 提款 {WITHDRAW_COUNT} 次")
    print(f"預期最終餘額: {INITIAL_BALANCE}")
    print("-" * 60)

    t1 = threading.Thread(target=deposit, args=(1,))
    t2 = threading.Thread(target=withdraw, args=(1,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"實際最終餘額: {bank_balance}")
    if bank_balance != INITIAL_BALANCE:
        print("=> 發生 Race Condition！結果不正確！")
    else:
        print("=> 結果正確（但這是運氣好）")
    print()


def run_with_mutex():
    global bank_balance
    bank_balance = INITIAL_BALANCE
    print("=" * 60)
    print("[實驗 2] 使用 Mutex — 保證資料正確")
    print(f"存款 {DEPOSIT_COUNT} 次, 提款 {WITHDRAW_COUNT} 次")
    print(f"預期最終餘額: {INITIAL_BALANCE}")
    print("-" * 60)

    t1 = threading.Thread(target=deposit_safe, args=(1,))
    t2 = threading.Thread(target=withdraw_safe, args=(1,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"實際最終餘額: {bank_balance}")
    if bank_balance == INITIAL_BALANCE:
        print("=> 正確！Mutex 保證了資料一致性！")
    else:
        print("=> 錯誤！")
    print()


if __name__ == "__main__":
    run_without_mutex()
    run_with_mutex()
