# 從基礎開始講解 Linux 的系統運作

> 本書以繁體中文撰寫，適合 Linux 初學者與想深入理解系統底層的開發者。
> 每個章節皆包含觀念圖解 + 實戰演練 + 輸出欄位物理意義解析。

---

## 目錄

1. [Linux 是什麼？](#1-linux-是什麼)
2. [Linux 開機流程 —— 從電源到 Shell](#2-linux-開機流程--從電源到-shell)
3. [核心與系統呼叫](#3-核心與系統呼叫)
4. [行程管理 (Process)](#4-行程管理-process)
5. [記憶體管理與分頁](#5-記憶體管理與分頁)
6. [檔案系統與 VFS](#6-檔案系統與-vfs)
7. [I/O 與資料流向 —— Pipe、重導向、標準串流](#7-io-與資料流向--pipe重導向標準串流)
8. [Linux 權限模型](#8-linux-權限模型)
9. [網路堆疊 —— 封包如何進出](#9-網路堆疊--封包如何進出)
10. [系統呼叫追蹤實戰 —— strace](#10-系統呼叫追蹤實戰--strace)
11. [系統監控 —— top、ps、free 底層意義](#11-系統監控--toppsfree-底層意義)

---

## 1. Linux 是什麼？

Linux 嚴格來說是**核心 (Kernel)**，不是完整的作業系統。一個完整的「Linux 發行版」= Linux 核心 + GNU 工具 + 套件管理員 + 應用程式。

```
┌──────────────────────────────────────┐
│           使用者應用程式               │  ← Chrome, VSCode, 你的 C 程式
├──────────────────────────────────────┤
│           系統程式 / Shell            │  ← bash, systemd, 核心工具
├──────────────────────────────────────┤
│         Linux Kernel (核心)          │  ← 行程、記憶體、檔案、網路、驅動
├──────────────────────────────────────┤
│           硬體 (CPU, RAM, Disk)      │
└──────────────────────────────────────┘
```

**關鍵概念**：使用者模式 (User Mode) vs 核心模式 (Kernel Mode)

```
應用程式空間 (User Space)
   ┌─────────┐  ┌─────────┐
   │  App A  │  │  App B  │  ← 彼此隔離，不能亂踩別人記憶體
   └────┬────┘  └────┬────┘
        │ 系統呼叫    │  (system call, 如 open, read, write)
        ▼            ▼
核心空間 (Kernel Space)
   ┌─────────────────────────────┐
   │     Linux Kernel            │  ← 獨占地操控硬體
   └─────────────────────────────┘
                │
                ▼
             硬體 (Hardware)
```

---

## 2. Linux 開機流程 —— 從電源到 Shell

### 2.1 流程圖

```
[按下電源]
    │
    ▼
[BIOS / UEFI] ──→ 載入開機順序中的第一個裝置
    │
    ▼
[Bootloader] (GRUB2)
    │  讀取 /boot/grub/grub.cfg
    │  載入 vmlinuz (核心映像檔)
    ▼
[Linux Kernel] 解壓縮 + 初始化
    │  ─── init_task (PID 0, idle process)
    │  ─── 記憶體管理初始化 (mm_init)
    │  ─── 中斷描述符表 (IDT)
    │  ─── 排程器初始化 (sched_init)
    ▼
[initrd / initramfs] ──→ 載入必要驅動模組
    │                      (檔案系統 driver, 磁碟 driver)
    ▼
[根檔案系統掛載]  ──→ switch_root 到真正的 rootfs (/)
    │
    ▼
[init/systemd] (PID 1) ──→ 執行所有系統服務
    │
    ▼
[getty / login] ──→ 登入提示
    │
    ▼
[Shell (bash)] ──→ 你看到命令提示字元了！
```

### 2.2 實戰演練：查看開機訊息

Linux 核心會將開機過程的日誌寫入 kernel ring buffer，可用 `dmesg` 查詢。

```bash
# 查看開機訊息中關於 CPU 的部份
dmesg | grep -i cpu | head -20
```

**預期輸出（範例）**：

```
[    0.000000] CPU: 16 total cores
[    0.000000] CPU: 8 performance cores (CPUs 0-7)
[    0.000000] CPU: 8 efficiency cores (CPUs 8-15)
[    0.058317] smpboot: CPU0: Intel(R) Core(TM) Ultra 9 285K (family: 0x6, model: 0xc6, stepping: 0x1)
[    0.109478] Performance Events: PEBS fmt4+-, full-width counters, 64-deep LBR, Intel PMU driver.
[    0.109480] ... version:                5
[    0.109481] ... bit width:              48
[    0.109482] ... generic registers:      8
[    0.109483] ... value mask:             0000ffffffffffff
[    0.109483] ... max period:             0000ffffffffffff
[    0.109484] ... fixed-purpose events:   4
[    0.109485] ... event mask:             0000000f000000ff
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `[ 0.000000]` | 從開機以來的**秒數**（核心啟動後經過的秒數，精確到微秒） |
| `CPU: 16 total cores` | 實體 CPU 核心總數（實體核心，不含超執行緒） |
| `smpboot: CPU0:` | SMP（對稱多處理）初始化時偵測到的 CPU #0 |
| `family: 0x6` | CPU 家族編號（0x6 = Intel 6th 架構之後的現代 CPU） |
| `model: 0xc6` | CPU 型號代碼（可用於查詢微架構） |
| `stepping: 0x1` | CPU 步進版本（修訂號，同型號的不同修訂） |
| `Performance Events` | 效能監控單元（PMU），用於 perf 工具的硬體計數器 |
| `bit width: 48` | PMU 計數器的位元寬度（48-bit，決定最大可計數值） |
| `generic registers: 8` | 通用效能計數器數量（可自訂監控事件） |
| `fixed-purpose events: 4` | 固定功能計數器（固定計數特定事件，如指令數） |

```bash
# 查看記憶體資訊
dmesg | grep -i "memory\|memblock" | head -10
```

**預期輸出（範例）**：

```
[    0.000000] BIOS-provided physical RAM map:
[    0.000000] BIOS-e820: [mem 0x0000000000000000-0x000000000009ffff] usable
[    0.000000] BIOS-e820: [mem 0x0000000000100000-0x00000000bfffffff] usable
[    0.000000] BIOS-e820: [mem 0x0000000100000000-0x00000004ffffffff] usable
[    0.000000] memory: 131834620K/137438048K available (14336K kernel code, 2472K rwdata, 6088K rodata, 2340K init, 5104K bss, 5603428K reserved, 0K cma-reserved)
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `BIOS-e820` | BIOS 提供的實體記憶體地圖（e820 是標準介面） |
| `[mem 0x...-0x...]` | 實體記憶體位址範圍（十六進制，單位 byte） |
| `usable` | 該記憶體區段可供 OS 使用 |
| `reserved` | 保留給硬體（如 ACPI、IOMMU）的記憶體，OS 不能動 |
| `available` | OS 實際可用的記憶體量（131 GB） |
| `kernel code` | 核心本身佔用的程式碼大小（14 MB） |
| `init` | 初始化程式碼（開機後可釋放，約 2.3 MB） |
| `bss` | 未初始化全域變數區（核心啟動時歸零） |

---

## 3. 核心與系統呼叫

### 3.1 什麼是系統呼叫？

使用者程式不能直接存取硬體或核心資料結構。必須透過**系統呼叫 (system call)** 請求核心代為操作。

```
使用者程式 (User Space)
   printf("Hello\n")
      │
      │  glibc 包裝
      ▼
   write(1, "Hello\n", 6)   ← 標準 C 函式庫包裝後的介面
      │
      │  syscall 指令 (x86-64: syscall; ARM: svc)
      ▼
────────────────── 切換至核心模式 ──────────────────
      │
      ▼
   sys_write()              ← 核心中的實際實作
      │
      │  查找檔案描述符 1 (stdout) 的檔案結構
      ▼
   終端機驅動程式 → 螢幕輸出
```

### 3.2 系統呼叫流程 (x86-64 架構)

```
應用程式呼叫 write()
       │
       │   將參數放入暫存器：
       │   RAX = 1        (系統呼叫編號：SYS_write)
       │   RDI = 1        (第一個參數：fd = stdout)
       │   RSI = buf      (第二個參數：緩衝區位址)
       │   RDX = 6        (第三個參數：長度)
       │
       ▼
   執行 syscall 指令
       │
       │   硬體自動做：
       │   1. 將 RIP 存入 RCX (返回位址)
       │   2. 將 RFLAGS 存入 R11
       │   3. 切換到核心態 (Ring 0)
       │   4. 跳轉到 MSR_LSTAR 指定的 entry 位址
       ▼
   核心進入點 entry_SYSCALL_64
       │
       │   儲存使用者暫存器 (pt_regs)
       │   檢查系統呼叫編號是否合法
       ▼
   查詢 sys_call_table[1] → 找到 sys_write
       │
       ▼
   執行真正的核心邏輯
       │
       ▼
   返回使用者空間 (sysretq)
```

### 3.3 實戰演練：strace 追蹤系統呼叫

```bash
# 追蹤 ls 指令的系統呼叫
strace -c ls
```

**預期輸出（範例）**：

```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 27.50    0.000412          45         9           newfstatat
 18.56    0.000278          27        10           getdents64
 14.16    0.000212          17        12           close
 13.22    0.000198          24         8           openat
 12.28    0.000184          20         9           write
  8.01    0.000120          17         7           mmap
  2.94    0.000044          22         2           read
  1.34    0.000020          20         1           execve
  1.27    0.000019          19         1           arch_prctl
  0.73    0.000011          11         1           munmap
------ ----------- ----------- --------- --------- ----------------
100.00    0.001498                    67           total
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `% time` | 該系統呼叫消耗的時間佔總時間百分比 |
| `seconds` | 該系統呼叫累計消耗的 CPU 時間（秒） |
| `usecs/call` | 每次呼叫平均花費的微秒數 (1µs = 10⁻⁶ 秒) |
| `calls` | 該系統呼叫被呼叫的次數 |
| `errors` | 該系統呼叫回傳錯誤的次數 |
| `newfstatat` | 讀取檔案中繼資料（inode 資訊），ls 用來檢查每個檔案的類型/權限 |
| `getdents64` | **讀取目錄條目**——這是 ls 的核心操作，從目錄讀取檔名列表 |
| `openat` | 開啟檔案（回傳檔案描述符） |
| `mmap` | 將檔案或裝置對應到記憶體（加速讀取） |
| `write` | 寫資料到 stdout（實際輸出到螢幕） |
| `execve` | 執行新程式（ls 本身也是從 bash fork+exec 出來的） |

**追蹤詳細呼叫流程**：

```bash
# 只看 openat 相關的系統呼叫
strace -e openat ls 2>&1 | head -10
```

**預期輸出（範例）**：

```
openat(AT_FDCWD, ".", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 3
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libselinux.so.1", O_RDONLY|O_CLOEXEC) = 3
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
```

**欄位物理意義**：

| 參數 | 意義 |
|------|------|
| `AT_FDCWD` | 使用行程的「目前工作目錄」作為相對路徑基準 |
| `O_RDONLY` | 以唯讀模式開啟 |
| `O_NONBLOCK` | 非阻塞模式（如果檔案不可立即讀取，直接回傳錯誤而不是等待） |
| `O_CLOEXEC` | 執行 exec 時自動關閉此檔案描述符（防止洩漏給子行程） |
| `O_DIRECTORY` | 要求開啟的必須是目錄（如果不是目錄則回傳錯誤） |
| `= 3` | 回傳的檔案描述符編號（0=stdin, 1=stdout, 2=stderr，所以新開的是 3） |

---

## 4. 行程管理 (Process)

### 4.1 行程的生命週期

```
          fork() / execve()
                │
                ▼
          ┌──────────┐
   ┌─────│   就緒    │←──────┐
   │     │  (Ready)  │       │
   │     └─────┬─────┘       │
   │           │ 排程器選中    │
   │           ▼              │
   │     ┌──────────┐        │
   │     │  執行中   │────────┤ 時間片用完 (preempt)
   │     │ (Running) │        │
   │     └─────┬─────┘        │
   │           │              │
   │     等待 I/O 或事件      │
   │           ▼              │
   │     ┌──────────┐        │
   │     │  休眠中   │────────┘  I/O 完成 / 事件到達
   │     │ (Sleep)  │
   │     └──────────┘
   │           │
   │       收到 SIGKILL
   │           │
   │           ▼
   │     ┌──────────┐
   └─────│  殭屍    │  ← 子行程已結束，但父行程尚未呼叫 wait()
         │ (Zombie) │
         └──────────┘
                │
           父行程呼叫 wait()
                ▼
              終止
```

### 4.2 Linux 行程描述符 —— task_struct

每個行程在核心中用 `task_struct` 表示，這是一個巨大的結構體（數千位元組）。

```
task_struct {
    ┌─────────────────────────────────┐
    │  state          (行程狀態)       │
    │  pid            (行程 ID)        │
    │  tgid           (執行緒群組 ID)  │
    │  parent / children (父子關係)    │
    │  mm             (記憶體描述符)    │  ← 指向 mm_struct
    │  fs             (檔案系統資訊)    │
    │  files          (已開啟檔案表)    │  ← fdtable
    │  signal         (訊號處理)       │
    │  sched_info     (排程資訊)       │  ← 優先權、時間片
    │  stack          (核心堆疊)       │
    │  cred           (憑證/權限)      │  ← uid, gid, capabilities
    └─────────────────────────────────┘
```

### 4.3 實戰演練：行程觀察

```bash
# 觀察行程樹狀結構
ps -ef --forest | head -20
```

**預期輸出（範例）**：

```
UID          PID    PPID  C STIME TTY          TIME CMD
root           1       0  0 09:15 ?        00:00:02 /sbin/init splash
root         372       1  0 09:15 ?        00:00:01  \_ /lib/systemd/systemd-journald
root         400       1  0 09:15 ?        00:00:00  \_ /lib/systemd/systemd-udevd
systemd+     622       1  0 09:15 ?        00:00:00  \_ /lib/systemd/systemd-resolved
systemd+     623       1  0 09:15 ?        00:00:00  \_ /lib/systemd/systemd-timesyncd
root         635       1  0 09:15 ?        00:00:01  \_ /lib/systemd/systemd-logind
user        1234     635  0 09:16 ?        00:00:02  \_ /lib/systemd/systemd --user
user        1300    1234  0 09:16 ?        00:00:00      \_ (sd-pam)
user        2456    1300  0 09:20 pts/0    00:00:00      \_ -bash
user        2789    2456  0 09:25 pts/0    00:00:00          \_ ps -ef --forest
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `UID` | 啟動此行程的使用者（有效使用者 ID 對應的名稱） |
| `PID` | 行程 ID——Linux 核心分配的唯一整數，每個新行程遞增（但會循環使用） |
| `PPID` | 父行程 ID——誰 fork 出這個行程的 |
| `C` | CPU 使用率百分比（整數，現代 Linux 通常是 0，因為時間片極短） |
| `STIME` | 行程開始時間（系統啟動後的時間或絕對時間） |
| `TTY` | 控制終端機；`?` 表示背景服務（daemon），無關聯終端 |
| `TIME` | 行程累計消耗的 CPU 時間 (mm:ss)，不是實際經過時間 |
| `CMD` | 執行的命令（包含參數）；`\_` 表示父子關係的樹狀結構 |

**PID 1 的重要性**：
- PID 1 是 systemd（或 init）
- 它是核心啟動後第一個使用者行程
- 負責收養所有孤兒行程（沒有父行程的子行程會自動被 PID 1 收養）
- 如果 PID 1 掛了，整個系統會 panic

### 4.4 實戰演練：fork 與行程狀態

```bash
# 使用 /proc 檔案系統查看行程資訊
cat /proc/$$/status | head -20
```

**預期輸出（範例）**：

```
Name:   bash
Umask:  0022
State:  S (sleeping)
Tgid:   2456
Ngid:   0
Pid:    2456
PPid:   1300
TracerPid:      0
Uid:    1000    1000    1000    1000
Gid:    1000    1000    1000    1000
FDSize: 256
Groups: 4 20 24 25 27 29 30 44 46 100 118
NStgid: 2456
NSpid:  2456
NSpgid: 2456
NSsid:  2456
VmPeak:    52100 kB
VmSize:    52088 kB
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `Name` | 行程的名稱（來自 `comm` 欄位，通常是執行檔名，限 15 字元） |
| `State: S` | 行程狀態：`R`(執行/就緒)、`S`(可中斷睡眠)、`D`(不可中斷睡眠)、`Z`(殭屍)、`T`(停止) |
| `Tgid` | 執行緒群組 ID——相當於主行程的 PID；執行緒共用同一個 Tgid |
| `Pid` | 行程 ID（在 /proc/[pid]/ 中，`$$` 是 shell 變數，代表目前 shell 的 PID） |
| `PPid` | 父行程 ID |
| `TracerPid` | 追蹤此行程的行程 ID（0 表示未被追蹤；strace 追蹤時會顯示其 PID） |
| `Uid: 1000 1000 1000 1000` | 四個 UID：實效(real)、有效(effective)、已儲存(saved)、檔案系統(fs) |
| `FDSize: 256` | 檔案描述符表的大小（不是目前開啟數，是分配的大小） |
| `VmPeak` | 此行程「曾達到」的最大虛擬記憶體用量（歷史上最高值） |
| `VmSize` | 此行程「目前」的虛擬記憶體總用量 |

```bash
# 觀察殭屍行程
# 先開一個子行程讓它變成殭屍
bash -c 'sleep 1 & exec sleep 10' &
sleep 2
ps aux | grep 'Z'
```

**關於 `State: D`（不可中斷睡眠）的說明**：

```
State: D (Uninterruptible Sleep)
    │
    ▼
用途：行程正在等待 I/O 完成（如讀取磁碟）
    │
    │  為什麼不可中斷？
    │  因為中斷可能導致 I/O 資料損毀
    │  例如：核心正在寫入磁碟 cache，你不能 SIGKILL 掉它
    │
    ▼
這通常出現在：
  1. NFS 連線中斷時
  2. 慢速磁碟 I/O
  3. 核心驅動程式 bug
```

---

## 5. 記憶體管理與分頁

### 5.1 虛擬記憶體 vs 實體記憶體

每個行程以為自己擁有完整的定址空間 (0x00000000 ~ 0x7FFFFFFFF)，但實際上核心在背後做轉換。

```
行程 A 的虛擬空間         行程 B 的虛擬空間
┌──────────────┐         ┌──────────────┐
│  0x7fff....  │         │  0x7fff....  │
│  (堆疊 Stack)│         │  (堆疊 Stack)│
├──────────────┤         ├──────────────┤
│              │         │              │
│  (堆積 Heap) │         │  (堆積 Heap) │
├──────────────┤         ├──────────────┤
│  .data .bss  │         │  .data .bss  │
├──────────────┤         ├──────────────┤
│  .text (程式碼)│        │  .text (程式碼)│
│  0x400000    │         │  0x400000    │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │    MMU (記憶體管理單元)  │
       │    + 頁表 (Page Table) │
       ▼                        ▼
┌──────────────────────────────────────┐
│         實體記憶體 (Physical RAM)     │
│  ┌──────┬──────┬──────┬──────┬──────┐ │
│  │頁框0 │頁框1 │頁框2 │頁框3 │頁框4 │ │
│  ├──────┼──────┼──────┼──────┼──────┤ │
│  │A的堆疊│B的程式│空閒  │A的程式│B的堆疊│ │ ← 散亂分佈！
│  └──────┴──────┴──────┴──────┴──────┘ │
└──────────────────────────────────────┘
```

### 5.2 分頁機制 (Paging)

x86-64 使用 4 層頁表：

```
虛擬位址 (48-bit)
┌────────┬────────┬────────┬────────┬────────────┐
│  PML4  │  PDPT  │   PD   │   PT   │  Offset    │
│ (9 bit)│ (9 bit)│ (9 bit)│ (9 bit)│  (12 bit)  │
└───┬────┴───┬────┴───┬────┴───┬────┴──────┬─────┘
    │        │        │        │           │
    ▼        ▼        ▼        ▼           ▼
  ┌────┐  ┌────┐  ┌────┐  ┌────┐       ┌───────┐
  │PML4│→ │PDPT│→ │ PD │→ │ PT │→ 實體 │頁框   │
  │    │  │    │  │    │  │    │  位址 │4KB    │
  └────┘  └────┘  └────┘  └────┘       └───────┘
  每個entry: 8 bytes, 512 entries/頁
  512^4 × 4KB = 256TB 虛擬空間
```

**轉換範例**：

```
虛擬位址: 0x7f3a4b5c6d00

轉換成二進位 (48-bit):
0111 1111 0011 1010 0100 1011 0101 1100 0110 1101 0000 0000
│←── PML4 ─→│←── PDPT ─→│←── PD ──→│←── PT ──→│← Offset→│
  0x1FC        0x1D2        0x16E       0x1A3       0xD00

實體位址 = PT[0x1A3] 中記錄的頁框基底 + 0xD00
```

### 5.3 實戰演練：查看行程記憶體映射

```bash
# 查看目前 shell 的記憶體佈局
cat /proc/$$/maps | head -15
```

**預期輸出（範例）**：

```
556677889000-55667788a000 r--p 00000000 08:01 1234567  /usr/bin/bash
55667788a000-5566778b2000 r-xp 00012000 08:01 1234567  /usr/bin/bash
5566778b2000-5566778bc000 r--p 0003a000 08:01 1234567  /usr/bin/bash
5566778bc000-5566778be000 rw-p 00044000 08:01 1234567  /usr/bin/bash
5566778be000-5566778c4000 rw-p 00000000 00:00 0        [heap]
7f3a4b400000-7f3a4b428000 r-xp 00000000 08:01 7654321  /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f3a4b428000-7f3a4b432000 r--p 00027000 08:01 7654321  /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f3a4b432000-7f3a4b434000 rw-p 00031000 08:01 7654321  /lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
7f3a4b435000-7f3a4b436000 rw-p 00000000 00:00 0
7f3a4b600000-7f3a4b783000 r-xp 00000000 08:01 7654322  /lib/x86_64-linux-gnu/libc.so.6
7f3a4b783000-7f3a4b7d2000 r--p 00183000 08:01 7654322  /lib/x86_64-linux-gnu/libc.so.6
7f3a4b7d2000-7f3a4b7d6000 rw-p 001d2000 08:01 7654322  /lib/x86_64-linux-gnu/libc.so.6
7f3a4b7d6000-7f3a4b7dd000 rw-p 00000000 00:00 0
7ffe0b7f0000-7ffe0b811000 rw-p 00000000 00:00 0        [stack]
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `556677889000-55667788a000` | 虛擬記憶體區段範圍（起始-結束，十六進制位址） |
| `r--p` | 權限：`r`(讀)、`w`(寫)、`x`(執行)、`p`(私有，copy-on-write) 或 `s`(共用) |
| `00000000` | 檔案偏移量——這個區段對應到檔案的哪個位置（bytes） |
| `08:01` | 裝置號碼 (major:minor)——檔案所在的磁碟分割區 |
| `1234567` | inode 編號——檔案的索引節點（硬碟上的唯一識別） |
| `/usr/bin/bash` | 對應的檔案路徑；`[heap]`、`[stack]` 是特殊的匿名映射 |
| `[heap]` | 堆積區——malloc() 配置的記憶體從這裡分配 |
| `[stack]` | 堆疊區——區域變數、函數呼叫返回位址 |

**區段 (Segment) 類型說明**：

```
ELF 檔案載入到記憶體的配置：
┌───────────────────┐
│ .text (程式碼)     │ r-x  ← 可讀、可執行（但不可寫，防止修改程式碼）
├───────────────────┤
│ .rodata (常數)     │ r--  ← 唯讀（字串常數、switch jump table）
├───────────────────┤
│ .data (已初始化)    │ rw-  ← 可讀寫（全域變數 int x = 5;）
├───────────────────┤
│ .bss (未初始化)     │ rw-  ← 可讀寫，頁面在存取時才真正配置
│   (BSS = Block    │       （全域變數 int y; 預設為 0）
│    Started by     │
│    Symbol)        │
├───────────────────┤
│ heap (堆積)        │ rw-  ← brk/sbrk/mmap 管理，向上增長
├───────────────────┤
│ stack (堆疊)       │ rw-  ← 自動變數，向下增長（高位址往低位址）
└───────────────────┘
```

### 5.4 分頁錯誤 (Page Fault) 流程

```
行程存取虛擬位址 A
       │
       ▼
MMU 查頁表
       │
       ├── 頁表項目存在 (Present=1) ──→ MMU 直接轉換成實體位址 → 存取成功
       │
       └── 頁表項目不存在 (Present=0) ──→ 觸發 Page Fault 例外
                    │
                    ▼
           核心 page fault handler
                    │
                    ├── 非法存取（如唯讀頁面嘗試寫入）
                    │   → SIGSEGV (Segmentation Fault)
                    │
                    ├── 匿名頁面（如 heap、bss）首次存取
                    │   → 配置一個新的實體頁框
                    │   → 填入 0
                    │   → 更新頁表，設定 Present=1
                    │   → 回到使用者行程重新執行指令
                    │
                    └── 檔案對應頁面（如載入中但尚未讀入的 .text）
                        → 從磁碟讀取該頁面內容到 page cache
                        → 更新頁表
                        → 回到使用者行程重新執行指令
```

### 5.5 實戰演練：觀察頁面錯誤

```bash
# 使用 ps 查看行程的 page fault 統計
ps -o pid,minflt,majflt,cmd -p $$
```

**預期輸出（範例）**：

```
  PID  MINFL  MAJFL CMD
 2456   8734      3 bash
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `MINFL` (minor faults) | 輕微頁面錯誤——頁面已在記憶體中，但頁表項目還沒建立（例如剛從 heap 配置新頁面）。成本極低（只需更新頁表） |
| `MAJFL` (major faults) | 重大頁面錯誤——頁面不在記憶體中，需要從磁碟讀取。成本極高（磁碟 I/O 是 nanoseconds vs milliseconds 的差距） |

```bash
# 用 time 命令觀察 page fault
/usr/bin/time -v ls 2>&1 | grep -i "page\|fault\|swap"
```

---

## 6. 檔案系統與 VFS

### 6.1 VFS —— 虛擬檔案系統

Linux 使用 VFS (Virtual File System) 抽象層，讓所有檔案系統（ext4、XFS、NTFS、tmpfs）以統一介面呈現。

```
使用者呼叫：
  open("/home/user/file.txt", O_RDONLY)
       │
       ▼
┌──────────────────────────────────────────┐
│            VFS (Virtual File System)      │
│  sys_open() → 透過路徑尋找 dentry & inode │
│  統一的檔案操作介面：                       │
│  struct file_operations {                 │
│      .open = ext4_open,                   │
│      .read = ext4_read,                   │
│      .write = ext4_write,                 │
│      .release = ext4_release              │
│  }                                        │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│     ext4         │  │      XFS         │  │     NTFS         │
│ (Linux 標準)     │  │ (高效能日誌)      │  │ (Windows)        │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                     │
         ▼                     ▼                     ▼
    ┌──────────────────────────────────────────────────┐
    │           通用區塊層 (Generic Block Layer)        │
    │    struct bio → 處理 I/O 請求合併、排序           │
    └──────────────────────┬───────────────────────────┘
                           │
                           ▼
              ┌──────────────────────┐
              │   I/O 排程器          │
              │  (CFQ, deadline, noop)│
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   區塊裝置驅動程式     │
              │   (如 NVMe, AHCI)    │
              └──────────────────────┘
```

### 6.2 inode 與 dentry

```
目錄結構：                         底層儲存：
/home/user/file.txt
         │                        inode table (inode 編號為索引)
         │                        ┌────────────┐
         ├── dentry 快取          │ inode #42  │ ← file.txt 的中繼資料
         │   (路徑→inode對應)      │  type: REG │
         │                        │  perm: 644 │
         ▼                        │  size: 1234│
  找到 inode #42                  │  blocks: 8 │
                                  │  ctime: ...│
                                  │  data: ────│────┐
                                  └────────────┘    │
                                                    ▼
                                            ┌──────────────┐
                                            │  data block   │
                                            │ #1024, #1025  │
                                            │ ...           │
                                            └──────────────┘
```

### 6.3 實戰演練：觀察 inode

```bash
# 查看檔案的 inode 資訊
stat /etc/passwd
```

**預期輸出（範例）**：

```
  File: /etc/passwd
  Size: 2844       Blocks: 8          IO Block: 4096   regular file
Device: 08:01     Inode: 1310745     Links: 1
Access: (0644/-rw-r--r--)  Uid: (    0/    root)   Gid: (    0/    root)
Access: 2026-05-30 10:00:00.000000000 +0800
Modify: 2026-03-15 14:22:30.123456789 +0800
Change: 2026-03-15 14:22:30.234567890 +0800
 Birth: 2025-10-01 09:00:00.000000000 +0800
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `Size: 2844` | 檔案實際大小（bytes） |
| `Blocks: 8` | 檔案佔用的磁碟區塊數（單位是 512 bytes，所以 8×512=4096，表示檔案小於 4KB 但最小配置一個 block） |
| `IO Block: 4096` | 檔案系統的 I/O 區塊大小（ext4 預設 4KB，一次讀寫的最小單位） |
| `Device: 08:01` | 裝置號碼——主編號 8（SCSI/SATA 裝置）、次編號 1（第一個分割區） |
| `Inode: 1310745` | inode 編號——檔案系統內唯一的 inode 索引 |
| `Links: 1` | 硬連結 (hard link) 計數——指向此 inode 的目錄條目數 |
| `Access` | 最後一次讀取檔案的時間（atime） |
| `Modify` | 最後一次修改檔案內容的時間（mtime） |
| `Change` | 最後一次改變檔案中繼資料的時間（ctime，注意不是 crtime） |
| `Birth` | 檔案建立時間（btime/crtime，有些檔案系統不支援） |

```bash
# 查看 inode 使用量
df -i /
```

**預期輸出（範例）**：

```
Filesystem     Inodes  IUsed    IFree IUse% Mounted on
/dev/nvme0n1p2 917504 610234   307270   67% /
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `Inodes` | inode 總數（格式化時就固定，每個 inode 約佔 256 bytes） |
| `IUsed` | 已使用的 inode 數量（≈ 檔案 + 目錄總數） |
| `IFree` | 剩餘 inode 數量 |
| `IUse%` | inode 使用率（inode 用完時即使還有空間也不能建新檔案） |

### 6.4 實戰演練：觀察 dentry 快取

```bash
# 查看 dentry 和 inode 快取用量
cat /proc/slabinfo | grep -E "dentry|inode" | head -5
```

**預期輸出（範例）**：

```
dentry            1234567  1500000    192   42    2 : tunables    0    0    0 : slabdata  35714  35714      0
```

**欄位意義**：dentry 快取——Linux 用來加速路徑解析的記憶體快取。你存取 `/usr/lib/libc.so` 時，核心不需要重新解析每一層目錄，直接從 dentry cache 找到 inode 編號。

---

## 7. I/O 與資料流向 —— Pipe、重導向、標準串流

### 7.1 標準串流 (Standard Streams)

每個 Linux 行程啟動時都有三個預設檔案描述符：

```
      ┌──────────┐
0 ────│  stdin   │──── 鍵盤輸入 / pipe 輸入
      └──────────┘
      ┌──────────┐
1 ────│  stdout  │──── 終端機輸出 / pipe 輸出
      └──────────┘
      ┌──────────┐
2 ────│  stderr  │──── 終端機錯誤輸出（獨立的串流）
      └──────────┘
```

**重導向的底層原理**：

```
在 shell 中執行:  ls > output.txt

原本:
                                 ┌──────────┐
                                 │  stdout   │──→ 終端機 (TTY)
                                 │  (fd=1)   │
                                 └──────────┘

執行 > 重導向後:
                                 ┌──────────┐
                                 │  stdout   │──→ output.txt (fd=1 指向了檔案)
                                 │  (fd=1)   │
                                 └──────────┘

shell 做的步驟：
1. open("output.txt", O_WRONLY|O_CREAT|O_TRUNC, 0644)  → 回傳 fd=3
2. dup2(3, 1)  → 複製 fd 3 到 fd 1，關閉原本的 fd 1
3. close(3)    → 關閉臨時的 fd 3
4. exec("ls")  → ls 的 fd 1 就指向 output.txt
```

### 7.2 Pipe —— 行程間通訊的資料流

```
ls -la /etc          |            grep "conf"
    │                              │
    │      pipe (核心緩衝區)        │
    │  ┌──────────────────────┐    │
    ├──→   pipefd[1] (寫端)   │    │
       │   [ 資料緩衝區 ]     │    │
       │   [  4KB~64KB  ]    │    │
       │   pipefd[0] (讀端)   ├────→
       └──────────────────────┘

資料流圖解：

ls -la /etc 的 stdout  →  pipe[寫端]  →  核心緩衝區  →  pipe[讀端]  →  grep 的 stdin

關鍵特性：
• 單向（資料只能從寫端流向讀端）
• 在核心緩衝區中暫存（不需要寫入磁碟）
• 如果緩衝區滿了：寫行程會被阻塞 (blocked)
• 如果緩衝區空了：讀行程會被阻塞
```

### 7.3 實戰演練：觀察檔案描述符

```bash
# 在一個簡單的 pipe 中查看 fd
ls /proc/$$/fd
```

**預期輸出（範例）**：

```
0  1  2  255
```

**每個 fd 的指向**：

```bash
# 顯示每個 fd 指向的目標
ls -la /proc/$$/fd
```

**預期輸出（範例）**：

```
lrwx------ 1 user user 64 May 30 10:00 0 -> /dev/pts/0
lrwx------ 1 user user 64 May 30 10:00 1 -> /dev/pts/0
lrwx------ 1 user user 64 May 30 10:00 2 -> /dev/pts/0
lrwx------ 1 user user 64 May 30 10:00 255 -> /dev/pts/0
```

**欄位物理意義**：

| 條目 | 意義 |
|------|------|
| `0 -> /dev/pts/0` | stdin 指向虛擬終端機（PTY = pseudo-terminal），pts/0 是你在視窗中看到的 shell |
| `1 -> /dev/pts/0` | stdout 也指向同一個終端機 |
| `2 -> /dev/pts/0` | stderr 也指向同一個終端機 |
| `255` | bash 保留的備用 fd（用於暫存） |
| `lrwx------` | 這些是符號連結，指向實際的開啟檔案描述 |

```bash
# 在 pipe 中觀察 fd
ls -la /proc/$$/fd | grep pipe
# 如果沒有 pipe 則不會有輸出
# 我們直接在 pipe 中查看：
echo "test" | ls -la /proc/self/fd
```

**輸出會說明**：當指令在 pipe 中執行時，0 會指向「來自 pipe 的讀端」（從上一個指令接收資料），1 會指向「走向 pipe 的寫端」（傳送資料給下一個指令）。

### 7.4 /dev/null 和 /dev/zero 的用途

```
/dev/null
  ┌────────────────┐
  │ 寫入 → 資料消失  │  ← 黑洞，永遠填不滿，寫入成功但資料直接被丟棄
  │ 讀取 → 回傳 EOF  │  ← 立即回傳檔案結尾，什麼也讀不到
  └────────────────┘

範例：
  command > /dev/null   → 丟棄 stdout
  command 2> /dev/null  → 丟棄 stderr
  command &> /dev/null  → 丟棄所有輸出

/dev/zero
  ┌────────────────┐
  │ 讀取 → 無限 \0   │  ← 讀取時永遠回傳 0x00 位元組
  └────────────────┘

範例： dd if=/dev/zero of=test.bin bs=1M count=100
      → 建立一個 100MB 的檔案，內容全是 0
```

---

## 8. Linux 權限模型

### 8.1 傳統 UNIX 權限

```
           檔案類型  擁有者   群組   其他人
              │      │││    │││    │││
              ▼      ▼▼▼    ▼▼▼    ▼▼▼
   $ ls -l /etc/passwd
   -rw-r--r--  1 root root  2844 May 30 10:00 /etc/passwd
   ↑          ↑
   檔案類型    權限位元

檔案類型：
  - : 一般檔案
  d : 目錄
  l : 符號連結
  c : 字元裝置（如 /dev/tty）
  b : 區塊裝置（如 /dev/sda）
  s : socket
  p : pipe (FIFO)

權限位元解碼：
  rwx rwx rwx
  │││ │││ │││
  │││ │││ └└└── 其他人 (others)
  │││ ││└────── 群組 (group)
  │││ └└─────── 擁有者 (user/owner)
  └└└────────── 特殊位元 (setuid/setgid/sticky)
```

### 8.2 實戰演練：權限底層表示

權限在 Linux 中實際上是用一個 16-bit 整數儲存的：

```bash
# 用數字檢視權限
stat -c "%a %A %n" /etc/passwd
```

**預期輸出**：`644 -rw-r--r-- /etc/passwd`

**數字權限解碼**：

```
644 (八進制) = 110 100 100 (二進制)
                │   │   │
                │   │   └── 其他人: r-- = 100 = 4
                │   └────── 群組:   r-- = 100 = 4
                └────────── 擁有者: rw- = 110 = 6

每一位元的意義：
  r (4) = 100: 可讀取
  w (2) = 010: 可寫入
  x (1) = 001: 可執行

  rw- = 4+2+0 = 6
  r-x = 4+0+1 = 5
  r-- = 4+0+0 = 4
  --- = 0+0+0 = 0
```

### 8.3 行程憑證 (Credentials)

```
每次系統呼叫檢查權限的流程：

行程呼叫 write(fd, buf, len)
       │
       ▼
    │ 核心檢查行程的「有效 UID」(euid)
    │ VS 檔案 inode 中的「擁有者 UID」和權限位元
    │
    ▼
    │ 比對順序：
    │ 1. 如果行程 euid == 0 (root) → 直接允許 (超級使用者無視權限)
    │ 2. 如果行程 euid == 檔案 uid → 用擁有者權限位元檢查
    │ 3. 如果行程 egid == 檔案 gid → 用群組權限位元檢查
    │ 4. 其他 → 用其他人權限位元檢查
    │
    ▼
    允許或回傳 EACCES / EPERM
```

### 8.4 setuid 位元 —— 為什麼 passwd 能改 /etc/shadow？

```
普通使用者執行 passwd：
  ┌─────────┐        ┌──────────────────┐
  │  user    │ 執行   │  /usr/bin/passwd │
  │  uid=1000│───────│  -rwsr-xr-x      │
  └─────────┘        │  擁有者: root     │
                      │  setuid 位元已設!!│
                      └────────┬─────────┘
                               │
                               ▼
    ┌──────────────────────────────────────┐
    │ 當核心載入執行檔時，偵測到 setuid 位元  │
    │ 行程的有效 UID (euid) 變成 root (0)  │
    │ 而不是原來使用者的 1000               │
    │                                      │
    │ 所以 passwd 可以寫入                  │
    │ /etc/shadow (權限 000，只有 root 可寫)│
    └──────────────────────────────────────┘

安全性：
  setuid 程式必須非常小心！
  例如：PATH 注入、緩衝區溢位都可能讓攻擊者
  取得 root 權限
```

**檢查 setuid**：

```bash
ls -l /usr/bin/passwd /usr/bin/su /usr/bin/sudo
```

**預期輸出**：

```
-rwsr-xr-x 1 root root  68248 Mar 20  2026 /usr/bin/passwd
-rwsr-xr-x 1 root root  55600 Mar 20  2026 /usr/bin/su
-rwsr-xr-x 1 root root 232416 Mar 20  2026 /usr/bin/sudo
```

注意 `s` 出現在 `x` 的位置：`-rwsr-xr-x`，這表示 setuid 位元已設定且擁有者具有執行權限。

---

## 9. 網路堆疊 —— 封包如何進出

### 9.1 Linux 網路堆疊層級

```
應用程式層 (Application)
  socket(AF_INET, SOCK_STREAM, 0) → fd
  connect(fd, &addr, sizeof(addr))
  write(fd, "GET / HTTP/1.1\r\n...", len)
       │
       ▼
┌──────────────────────────────────┐
│  Socket Layer                    │
│  通用 socket 介面                 │
│  根據 family/type 分派到實作       │
├──────────────────────────────────┤
│  TCP/UDP (傳輸層)                 │
│  ┌────────────────────────────┐  │
│  │ TCP: 序列號、ACK、重傳、    │  │
│  │       擁塞控制、流量控制    │  │
│  │ UDP: 無狀態、無保證         │  │
│  └────────────────────────────┘  │
├──────────────────────────────────┤
│  IP (網路層)                      │
│  路由查找、封包分段、TTL          │
│  ┌────────────────────────────┐  │
│  │ ip_rcv() → ip_forward()   │  │
│  │         → ip_local_deliver()│  │
│  └────────────────────────────┘  │
├──────────────────────────────────┤
│  Netfilter (iptables/nftables)   │
│  PREROUTING → FORWARD → POSTRTNG │
│  INPUT → PROCESS → OUTPUT        │
├──────────────────────────────────┤
│  網路卡驅動程式 (Device Driver)   │
│  ┌────────────────────────────┐  │
│  │ struct net_device_ops      │  │
│  │   .ndo_start_xmit = e1000_│  │
│  │   .ndo_open = e1000_open   │  │
│  └────────────────────────────┘  │
├──────────────────────────────────┤
│  網路硬體 (NIC)                   │
│  RX/TX Ring Buffer → DMA        │
└──────────────────────────────────┘
```

### 9.2 封包接收流程

```
網路卡收到封包
       │
       │  NIC 透過 DMA 將封包直接寫入主記憶體
       │  （不需要 CPU 介入）
       ▼
   RX Ring Buffer (環形緩衝區)
       │
       │  NIC 觸發硬體中斷 (IRQ)
       │  核心中斷處理常式執行
       ▼
   NAPI (New API) softirq
       │
       │  關閉中斷，改用輪詢 (polling)
       │  避免中棄風暴 (live lock)
       ▼
   網路層處理 (IP)
       │
       ▼
   傳輸層處理 (TCP/UDP)
       │
       │  查找 socket 對應
       ▼
   放入 socket 接收緩衝區
       │
       │  wake up 等待中的行程
       ▼
   行程從 recv()/read() 回傳
```

### 9.3 實戰演練：網路狀態觀察

```bash
# 觀察 socket 狀態
ss -tulpn | head -10
```

**預期輸出（範例）**：

```
Netid  State   Recv-Q  Send-Q  Local Address:Port   Peer Address:Port   Process
tcp    LISTEN  0       128     0.0.0.0:22           0.0.0.0:*           users:(("sshd",pid=832,fd=3))
tcp    LISTEN  0       128     [::]:22              [::]:*              users:(("sshd",pid=832,fd=4))
udp    UNCONN  0       0       127.0.0.53:53        0.0.0.0:*           users:(("systemd-resolve",pid=622,fd=12))
tcp    ESTAB   0       0       192.168.1.100:45678  10.0.0.1:443        users:(("chrome",pid=3456,fd=89))
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `Netid` | 協定類型：tcp、udp、tcp6、udp6 |
| `State` | socket 狀態：`LISTEN`(監聽中)、`ESTAB`(已連線)、`TIME_WAIT`(等待關閉)、`CLOSE_WAIT`(等待關閉) |
| `Recv-Q` | **接收佇列**：等待應用程式讀取的資料量（bytes）。如果持續不為 0 表示應用程式來不及處理 |
| `Send-Q` | **傳送佇列**：已送出但尚未收到 ACK 確認的資料量（bytes） |
| `Local Address:Port` | 本機監聽的 IP 和 port；`0.0.0.0:22` 表示在所有介面監聽 SSH |
| `Peer Address:Port` | 遠端位址；`0.0.0.0:*` 表示接受任何來源 |
| `Process` | 擁有此 socket 的行程資訊（需要 root 或 `sudo` 才能看到） |

```bash
# 查看網路狀態 (netstat 傳統工具)
netstat -s | head -20
```

**預期輸出（範例）**：

```
Tcp:
    1234567 active connection openings
    2345678 passive connection openings
    34567 failed connection attempts
    1234 connection resets received
    567890 connections established
    12345678 segments received
    23456789 segments sent out
    7890 segments retransmitted
    56 bad segments received
    12345 resets sent
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `active connection openings` | 此機器主動發起的 TCP 連線數（你 connect 別人） |
| `passive connection openings` | 此機器被動接受的 TCP 連線數（別人 connect 你） |
| `failed connection attempts` | 連線失敗次數（對方拒絕、超時等） |
| `segments retransmitted` | 重傳的區段數——**如果這個數字很高，表示網路不穩定或擁塞** |
| `bad segments received` | 收到損壞的 TCP 區段（checksum 錯誤），可能硬體問題 |

### 9.4 實戰演練：traceroute 追蹤封包路徑

```bash
# 追蹤到 google 的封包路由（WSL 可能需要 sudo）
traceroute -n 8.8.8.8 2>/dev/null || echo "請安裝 traceroute"
```

**輸出欄位意義**：

```
traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 60 byte packets
 1  192.168.1.1  0.345ms  0.289ms  0.301ms    ← 你的路由器 (第一跳)
 2  10.0.0.1     2.123ms  2.098ms  2.201ms    ← ISP 機房
 3  172.16.0.5   5.678ms  5.901ms  5.432ms    ← 區域交換節點
 ...
10  8.8.8.8      12.345ms 12.111ms 12.567ms   ← Google DNS
```

**原理**：traceroute 送出 TTL=1,2,3... 的 UDP 封包，每個路由器轉發時 TTL-1，TTL=0 時回傳 ICMP Time Exceeded 訊息。

---

## 10. 系統呼叫追蹤實戰 —— strace

### 10.1 追蹤一個簡單的 cat 指令

```bash
# 用 strace 追蹤 cat 一個小檔案
echo "Hello World" > /tmp/test.txt
strace cat /tmp/test.txt 2>&1 | head -30
```

**預期輸出（範例）**：

```
execve("/usr/bin/cat", ["cat", "/tmp/test.txt"], 0x7ffc12345678 /* 58 vars */) = 0
brk(NULL)                               = 0x556677889000
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f3a4c000000
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=127890, ...}) = 0
mmap(NULL, 127890, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f3a4bfe0000
close(3)                                = 0
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\0\0\0\0\0\0\0\0"..., 832) = 832
mmap(NULL, 2173184, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f3a4bb00000
...
openat(AT_FDCWD, "/tmp/test.txt", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=12, ...}) = 0
read(3, "Hello World\n", 131072)         = 12
write(1, "Hello World\n", 12)            = 12
write(1, "\n", 1)                        = 1
close(3)                                 = 0
close(1)                                 = 0
exit_group(0)                            = ?
+++ exited with 0 +++
```

**步驟解說**：

```
1. execve()    → 載入 cat 程式到記憶體（從磁碟讀取 ELF 格式執行檔）
2. brk(NULL)   → 詢問目前 heap 的邊界在哪
3. mmap(..., PROT_READ|PROT_WRITE, MAP_ANONYMOUS)
               → 配置匿名記憶體頁面（相當於 malloc，用於 cat 的內部緩衝）
4. openat(..., "/etc/ld.so.cache")
               → 打開動態連結器快取（為了找 libc.so 在哪）
5. mmap(..., PROT_READ|PROT_EXEC, ..., "/lib/.../libc.so.6")
               → 把 libc 的程式碼對應到記憶體（可讀可執行但不可寫）
6. openat(..., "/tmp/test.txt", O_RDONLY)
               → 打開你要 cat 的檔案！回傳 fd=3
7. fstat(3)    → 讀取檔案中繼資料（大小 = 12 bytes）
8. read(3, buf, 131072)
               → 從檔案讀取最多 131072 bytes，實際讀到 12 bytes
9. write(1, "Hello World\n", 12)
               → 寫到 stdout (fd=1)，也就是你的螢幕
               注意：write() 是這次操作中唯一真正讓「螢幕顯示東西」的呼叫！
10. exit_group(0) → 行程結束，回傳 0
```

### 10.2 追蹤網路相關呼叫

```bash
# 追蹤 curl 的系統呼叫（只顯示網路相關的）
strace -e network curl -s http://example.com 2>&1 | head -20
```

**預期輸出**：

```
socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3
setsockopt(3, SOL_TCP, TCP_NODELAY, [1], 4) = 0
setsockopt(3, SOL_SOCKET, SO_KEEPALIVE, [1], 4) = 0
connect(3, {sa_family=AF_INET, sin_port=htons(80), sin_addr=inet_addr("93.184.216.34")}, 16) = 0
sendto(3, "GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/8.4.0\r\nAccept: */*\r\n\r\n", 75, 0, NULL, 0) = 75
recvfrom(3, "HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\nCache-Control: max-age=604800\r\nContent-..."}, 102400, 0, NULL, NULL) = 648
```

**欄位物理意義**：

| 系統呼叫 | 意義 |
|---------|------|
| `socket(AF_INET, SOCK_STREAM, IPPROTO_TCP) = 3` | 建立一個 IPv4 TCP socket，回傳 fd=3 |
| `setsockopt(...TCP_NODELAY...)` | 關閉 Nagle 演算法（讓小封包立即送出不等待） |
| `connect(3, {sin_port=htons(80), sin_addr="93.184.216.34"})` | 連接到遠端伺服器的 port 80（HTTP） |
| `sendto(3, "GET / HTTP/1.1...") = 75` | 傳送 HTTP GET 請求（75 bytes） |
| `recvfrom(3, "HTTP/1.1 200 OK...") = 648` | 接收 HTTP 回應（648 bytes） |

---

## 11. 系統監控 —— top、ps、free 底層意義

### 11.1 free —— 記憶體使用量

```bash
free -h
```

**預期輸出（範例）**：

```
               total        used        free      shared  buff/cache   available
Mem:            31Gi        12Gi       4.5Gi       1.2Gi        15Gi        18Gi
Swap:          4.0Gi       0.5Gi       3.5Gi
```

**欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `total` | 實體 RAM 總量（硬體安裝的記憶體減去核心保留的部分） |
| `used` | 被**使用者行程**使用的記憶體（不含 buffer/cache） |
| `free` | 完全沒在用、也沒被 cache 佔用的記憶體。**這項很低是正常的**——Linux 把閒置記憶體拿來 cache |
| `shared` | 多個行程共用的記憶體（如 tmpfs、共用函式庫、Shared Memory IPC） |
| `buff/cache` | **Page Cache**（檔案內容快取）+ **Buffer Cache**（block 裝置中繼資料） |
| `available` | **可用的記憶體總量**（最實用的欄位！= free + 可回收的 cache） |
| `Swap total` | swap 空間總大小（通常是一塊磁碟分區或檔案） |
| `Swap used` | 已使用的 swap 量——**不為 0 正常嗎？** 如果很小（幾 MB）表示只是換出了不常用的頁面；如果持續增長表示真實記憶體不足 |

**記憶體分配圖解**：

```
實體記憶體分佈圖：

┌──────────────────────────────────┐
│  核心程式碼 + 資料 (Kernel)       │  ~ 20-50 MB
├──────────────────────────────────┤
│  使用者行程 (User Processes)      │  ← used (12G)
│  [firefox][chrome][vscode][...] │
├──────────────────────────────────┤
│  Page Cache (檔案快取)            │  ← buff/cache (15G)
│  [cat的內容][libc.so][bash...]  │
├──────────────────────────────────┤
│  Slab (核心內部物件)              │  ← 包含在 used/cache 中
│  [dentry][inode][task_struct]   │
├──────────────────────────────────┤
│  完全空閒 (Truly Free)            │  ← free (4.5G)
└──────────────────────────────────┘

為什麼 available ≠ free + buff/cache？
因為不是所有 cache 都可以立即回收——
例如正在寫入髒頁面 (dirty page) 就不能馬上回收。
available 是核心估算：「如果新程式要求 N GB，我能擠出多少」
```

### 11.2 實戰演練：細看記憶體細節

```bash
cat /proc/meminfo | head -20
```

**預期輸出（範例）**：

```
MemTotal:       32648232 kB
MemFree:         4728900 kB
MemAvailable:   18888888 kB
Buffers:          123456 kB
Cached:         14567890 kB
SwapCached:         1234 kB
Active:         12345678 kB
Inactive:        9876543 kB
Active(anon):    5678901 kB
Inactive(anon):  1234567 kB
Active(file):    6666777 kB
Inactive(file):  8641976 kB
Unevictable:        1234 kB
Mlocked:             0 kB
SwapTotal:       4194304 kB
SwapFree:        3670016 kB
Dirty:               456 kB
Writeback:            0 kB
AnonPages:       6789012 kB
Mapped:          3456789 kB
Shmem:           1234567 kB
```

**關鍵欄位物理意義**：

| 欄位 | 意義 |
|------|------|
| `Active` | 最近被存取過的記憶體頁面（在啟動狀態，不會被優先 swap） |
| `Inactive` | 一段時間沒被存取的頁面（kernel 可以選擇將它們 swap 出去） |
| `Active(anon)` | 活躍的匿名頁面（如行程 heap/stack）——這些是你 swap 時最優先的對象 |
| `Active(file)` | 活躍的檔案頁面（如正在讀取的檔案內容） |
| `Dirty` | **髒頁面**：Page Cache 中已被修改但**尚未寫回磁碟**的頁面量 |
| `Writeback` | 正在被核心寫回磁碟的頁面量（正常應該接近 0） |
| `AnonPages` | 匿名頁面總量（無檔案備份的頁面，如 malloc 的記憶體、堆疊） |
| `Mapped` | 對應到檔案且正在被行程使用的頁面（如 mmap 的檔案、載入的函式庫） |
| `Shmem` | 共享記憶體（如 tmpfs、Shared Memory IPC、dentry/inode cache 部份） |

**髒頁面與寫回機制**：

```
行程寫入檔案
    │
    ▼
資料寫入 Page Cache (記憶體)
    │
    │  頁面被標記為 Dirty
    │  （資料已修改但磁碟上還是舊的）
    ▼
    ┌─────────────────────┐
    │  pdflush / kworker  │  ← 核心執行緒，定時寫回髒頁面
    │  寫回條件：           │
    │  • dirty_ratio 滿了  │  （dirty pages 超過總記憶體百分比）
    │  • dirty_expire_..  │  （髒頁面存在超過指定秒數）
    │  • sync/fsync 被呼叫 │  （使用者主動要求寫回）
    └──────────┬──────────┘
               ▼
    實際寫入磁碟 (I/O)
               │
               ▼
    頁面解除 Dirty 標記
    可用於 page reclaim
```

### 11.3 top —— 即時系統監控

```bash
# 以批次模式執行一次（非互動）
top -bn1 | head -20
```

**預期輸出（範例）**：

```
top - 10:30:00 up 1 day,  3:45,  1 user,  load average: 0.45, 0.32, 0.28
Tasks: 245 total,   1 running, 244 sleeping,   0 stopped,   0 zombie
%Cpu(s):  5.2 us,  1.3 sy,  0.0 ni, 93.0 id,  0.2 wa,  0.0 hi,  0.3 si,  0.0 st
MiB Mem :  31168.0 total,   5892.5 free,  11958.6 used,  13316.9 buff/cache
MiB Swap:   4096.0 total,   3584.0 free,    512.0 used.  18796.3 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
   1234 user      20   0  521000  45678  12345 S   1.2   0.1   1:23.45 chrome
   2345 root      20   0  178900  12345   6789 S   0.5   0.0   0:12.34 sshd
   3456 user      20   0  123456  23456   8901 R   0.3   0.1   0:01.23 top
```

**第一行欄位意義**：

| 欄位 | 意義 |
|------|------|
| `10:30:00` | 目前系統時間 |
| `up 1 day, 3:45` | 系統已連續運作多長時間（可用 `uptime` 指令查看） |
| `1 user` | 目前已登入的使用者數 |
| `load average: 0.45, 0.32, 0.28` | **CPU 負載平均值**：分別為 1/5/15 分鐘的平均值。這個值代表「排程器就緒佇列中的行程數量」（包含正在跑 + 等待 CPU 的）。單核心 CPU 負載 > 1 表示有行程在等 CPU |

**第二行 Tasks**：

| 欄位 | 意義 |
|------|------|
| `245 total` | 行程總數（所有 task_struct 數量） |
| `1 running` | 真正在執行中或準備執行的行程（狀態 R） |
| `244 sleeping` | 等待事件/資源的行程（狀態 S 或 D） |
| `0 zombie` | 已結束但父行程未收屍的行程 |

**第三行 %Cpu(s)**：

```
us (user)    : 使用者空間程式佔用 CPU 時間
sy (system)  : 核心空間（系統呼叫、中斷處理）佔用 CPU 時間
ni (nice)    : 使用者程式中被 nice 調整過優先權的所花時間
id (idle)    : CPU 空閒時間（什麼事都沒做）
wa (iowait)  : CPU 因為等待 I/O（如磁碟）而空轉的時間
hi (hardirq) : 硬體中斷處理時間
si (softirq) : 軟體中斷處理時間（如網路封包接收後續處理）
st (steal)   : 被 hypervisor 偷走的時間（虛擬機器專用）
```

**行程列表欄位**：

| 欄位 | 意義 |
|------|------|
| `VIRT` | **虛擬記憶體總量**（行程對應的所有記憶體，含未實際配置的。例如 malloc(1GB) 但只用了 1MB，VIRT 還是 1GB） |
| `RES` | **常駐記憶體**（Resident size）——實際佔用實體記憶體的量（物理頁框）。這才是真正在用的記憶體 |
| `SHR` | **共享記憶體**（Shared memory）——與其他行程共享的部份（如 libc.so 的程式碼） |
| `S` | 行程狀態（R/S/D/Z/T） |
| `%CPU` | 該行程自上次更新以來的 CPU 使用率 |
| `%MEM` | RES / MemTotal × 100% |
| `TIME+` | 該行程累計使用的 CPU 時間（分鐘:秒.百分秒） |

**VIRT vs RES 圖解**：

```
行程向 OS 要求 100MB 記憶體 (malloc(100*1024*1024))：

        VIRT = 100MB (虛擬)
        ┌──────────────────────────────────────┐
        │                                      │
        │    ┌────────────────────────┐        │
        │    │   RES = 10MB (實際使用) │        │
        │    │  ┌──────────────────┐   │        │
        │    │  │  真正存了資料      │   │        │
        │    │  │  的頁面(實體記憶體)│   │        │
        │    │  └──────────────────┘   │        │
        │    │  ┌──────────────────┐   │        │
        │    │  │  已分配但還未     │   │        │
        │    │  │  寫入的匿名頁面   │   │        │
        │    │  └──────────────────┘   │        │
        │    └────────────────────────┘        │
        │                                      │
        │  ┌────────────────────────┐          │
        │  │  未實際配置的虛擬位址    │          │
        │  │  (第一次存取時才 page   │          │
        │  │   fault 配實體頁框)    │          │
        │  └────────────────────────┘          │
        └──────────────────────────────────────┘
        VIRT = 總虛擬位址空間大小（幾乎總是 >= RES）
        RES  = 實際佔用實體記憶體大小（這才是「用了多少 RAM」）
        SHR  = RES 中與其他行程共用的部份
```

### 11.4 實戰演練：手動觸發記憶體壓力

```bash
# 建立一個消耗記憶體的測試（小心，不要讓系統當掉！）
# 下面的指令會建立一個 256MB 的匿名記憶體映射
python3 -c "
import mmap
import time
# 配置 256 MB 匿名記憶體
buf = bytearray(256 * 1024 * 1024)
print('配置了 256 MB')
print('按 Ctrl+C 釋放')
time.sleep(10)
" &
# 在另一個終端機觀察：
# free -h   # 看 used / available 變化
# top       # 看 VIRT / RES 變化
```

### 11.5 手動觸發 swap

```bash
# 先確認 swap 狀態
swapon --show

# 範例輸出:
# NAME       TYPE      SIZE  USED PRIO
# /swapfile  file       4G  512M   -2

# 模擬記憶體壓力（小心！）
stress-ng --vm 2 --vm-bytes 2G --timeout 30s 2>/dev/null &
# 這會啟動 2 個 worker，每個消耗 2GB 記憶體
# 觀察：
#   free -h       → used 上升, free/available 下降
#   vmstat 1      → si (swap in), so (swap out) 欄位變非零
#   top           → 看到 stress-ng 的 RES 很大
```

---

## 附錄 A：快速查詢表

### 檔案描述符 (File Descriptor)

```
fd 0 = stdin   (標準輸入)
fd 1 = stdout  (標準輸出)
fd 2 = stderr  (標準錯誤輸出)
fd 3+ = 程式自行開啟的檔案 / socket / pipe
```

### 行程狀態 (Process State)

```
R (TASK_RUNNING)       : 正在執行或等待 CPU 排程
S (TASK_INTERRUPTIBLE) : 休眠中，可被訊號喚醒（最常見）
D (TASK_UNINTERRUPTIBLE): 休眠中，不可被打斷（通常等待 I/O）
Z (TASK_DEAD - EXIT_ZOMBIE): 殭屍，已結束但父行程未 wait
T (TASK_STOPPED)       : 停止（收到 SIGSTOP 或正在被除錯）
t (TASK_TRACED)        : 被 ptrace 追蹤中（如 strace 或 gdb）
I (TASK_IDLE)          : 閒置核心執行緒（5.14+ 核心新增）
```

### 常用 /proc 檔案系統

```
/proc/[pid]/status     → 行程狀態、記憶體、權限等摘要
/proc/[pid]/maps       → 虛擬記憶體映射區段
/proc/[pid]/fd/        → 開啟的檔案描述符（符號連結）
/proc/[pid]/cwd        → 符號連結，指向行程的目前工作目錄
/proc/[pid]/exe        → 符號連結，指向執行檔路徑
/proc/[pid]/environ    → 環境變數（以 \0 分隔）
/proc/[pid]/cmdline    → 完整命令列參數（以 \0 分隔）
/proc/[pid]/cgroup     → 控制群組 (cgroup) 資訊
/proc/[pid]/ns/        → 命名空間 (namespace) 資訊
/proc/meminfo          → 系統記憶體詳細狀態
/proc/cpuinfo          → CPU 詳細資訊
/proc/loadavg          → 系統負載平均值
/proc/uptime           → 系統啟動時間
/proc/stat             → 核心統計資料
```

---

## 附錄 B：WSL 與 Linux 差異說明

WSL 2 使用真正的 Linux 核心（在 Hyper-V 虛擬機器中執行），與一般 Linux 差異極小：

```
一般 Linux                    WSL 2
┌──────────┐                 ┌──────────┐
│  你的程式  │                 │  你的程式  │
├──────────┤                 ├──────────┤
│ systemd  │ ← 部分不支援    │  WSL init│
├──────────┤                 ├──────────┤
│ Linux    │                 │ Linux    │ ← 同一個核心
│ Kernel   │                 │ Kernel   │
├──────────┤                 ├──────────┤
│ 硬體驅動  │                 │ Hyper-V  │
│          │                 │ 虛擬硬體  │
├──────────┤                 ├──────────┤
│ 實體硬體  │                 │ Windows  │
│ (CPU/...)│                 │ 核心 + HW│
└──────────┘                 └──────────┘

WSL 2 的限制：
• 沒有 systemd（預設，但可手動啟用）
• 不能直接存取實體硬體（無 PCIe 直通）
• 網路是 NAT（但可設定 mirror 模式）
• 支援全部的 /proc、/sys、cgroup、namespace
• 本書中的 strace、top、free、ps、ss 等指令全部可執行
```

---

> **結語**：Linux 系統運作的精髓在於理解「使用者空間 vs 核心空間」的劃分、「系統呼叫」是兩者間的橋樑，以及「一切皆檔案」的設計哲學。當你執行一個簡單的 `cat` 指令時，背後有數十個系統呼叫、數百次 CPU 模式切換、記憶體分頁機制、VFS 層層轉換——這些底層機制的理解，正是區分「會用 Linux」和「懂 Linux」的關鍵。
>
> *Happy Hacking!*
