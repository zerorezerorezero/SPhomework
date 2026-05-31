import threading
import queue
import time
import random

BUFFER_SIZE = 5
PRODUCE_COUNT = 10
CONSUMER_COUNT = 2
PRODUCER_COUNT = 2

q = queue.Queue(BUFFER_SIZE)
produced_count = 0
consumed_count = 0
produced_lock = threading.Lock()
consumed_lock = threading.Lock()
done = False


def producer(pid):
    global produced_count, done
    while True:
        with produced_lock:
            if produced_count >= PRODUCE_COUNT:
                done = True
                break
            item = produced_count
            produced_count += 1

        q.put(item)
        print(f"生產者 {pid}: 生產了商品 {item}  (緩衝區大小: {q.qsize()})")
        time.sleep(random.uniform(0.1, 0.5))

    print(f"生產者 {pid}: 結束生產")


def consumer(cid):
    global consumed_count
    while True:
        try:
            item = q.get(timeout=2)
            print(f"消費者 {cid}: 消費了商品 {item}  (緩衝區大小: {q.qsize()})")
            with consumed_lock:
                consumed_count += 1
            q.task_done()
            time.sleep(random.uniform(0.3, 0.7))
        except queue.Empty:
            with produced_lock:
                if produced_count >= PRODUCE_COUNT and q.empty():
                    break

    print(f"消費者 {cid}: 結束消費")


def main():
    print("=" * 60)
    print("生產者-消費者問題模擬")
    print(f"緩衝區大小: {BUFFER_SIZE}")
    print(f"生產者數量: {PRODUCER_COUNT}, 消費者數量: {CONSUMER_COUNT}")
    print(f"總生產數量: {PRODUCE_COUNT}")
    print("=" * 60)

    producers = [
        threading.Thread(target=producer, args=(i,))
        for i in range(PRODUCER_COUNT)
    ]
    consumers = [
        threading.Thread(target=consumer, args=(i,))
        for i in range(CONSUMER_COUNT)
    ]

    for t in producers + consumers:
        t.start()

    for t in producers:
        t.join()

    q.join()

    for t in consumers:
        t.join()

    print()
    print(f"總生產數: {produced_count}, 總消費數: {consumed_count}")
    if produced_count == consumed_count:
        print("結果正確！生產數量等於消費數量。")
    else:
        print("結果錯誤！")


if __name__ == "__main__":
    main()
