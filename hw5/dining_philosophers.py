import threading
import time
import random

NUM_PHILOSOPHERS = 5
EAT_TIMES = 3

forks = [threading.Lock() for _ in range(NUM_PHILOSOPHERS)]
# 用一個 Mutex 保護輸出，避免交錯
print_lock = threading.Lock()


def safe_print(msg):
    with print_lock:
        print(msg)


def philosopher(pid):
    left_fork = forks[pid]
    right_fork = forks[(pid + 1) % NUM_PHILOSOPHERS]

    # 解法：讓其中一位哲學家反過來拿叉子（左撇子解法）
    # 第 0 位哲學家先拿右邊再拿左邊，破壞循環等待
    if pid == 0:
        first_fork, second_fork = right_fork, left_fork
    else:
        first_fork, second_fork = left_fork, right_fork

    for round_num in range(1, EAT_TIMES + 1):
        safe_print(f"哲學家 {pid}: 思考中... (第 {round_num} 輪)")
        time.sleep(random.uniform(0.5, 1.5))

        first_fork.acquire()
        safe_print(f"哲學家 {pid}: 拿起了第一支叉子")
        second_fork.acquire()
        safe_print(f"哲學家 {pid}: 拿起了第二支叉子，開始用餐")

        time.sleep(random.uniform(0.5, 1.5))
        safe_print(f"哲學家 {pid}: 用餐完畢，放下叉子")

        second_fork.release()
        first_fork.release()
        safe_print(f"哲學家 {pid}: 已放下兩支叉子")

    safe_print(f"哲學家 {pid}: 吃飽了！")


def main():
    print("=" * 60)
    print("哲學家用餐問題模擬")
    print(f"哲學家數量: {NUM_PHILOSOPHERS}")
    print(f"每位哲學家用餐次數: {EAT_TIMES}")
    print("=" * 60)
    print("解法：讓第 0 位哲學家先拿右叉再拿左叉")
    print("破壞循環等待條件，避免 Deadlock")
    print("=" * 60)

    philosophers = [
        threading.Thread(target=philosopher, args=(i,))
        for i in range(NUM_PHILOSOPHERS)
    ]

    for t in philosophers:
        t.start()

    for t in philosophers:
        t.join()

    print()
    print("所有哲學家都吃飽了！沒有發生 Deadlock。")


if __name__ == "__main__":
    main()
