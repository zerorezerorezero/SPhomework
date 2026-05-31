NL 語言解釋器 - 快速開始指南
==============================

## 📦 項目位置
/workspaces/codespaces-blank/HW/HW2/

## 🚀 運行方式

### 方法 1: 執行示例程序
```bash
cd /workspaces/codespaces-blank/HW/HW2
python3 main.py EXAMPLES.nl
```

### 方法 2: 執行測試程序
```bash
python3 main.py TEST_EXAMPLES.nl
```

### 方法 3: 交互式 REPL 模式
```bash
python3 main.py
```

### 方法 4: 使用 Bash 腳本
```bash
chmod +x run.sh
./run.sh EXAMPLES.nl
```

## 📚 主要文件說明

| 文件 | 說明 |
|------|------|
| `lexer.py` | 詞法分析器 - 將源代碼轉為 Token |
| `parser.py` | 語法分析器 - 構建抽象語法樹 (AST) |
| `interpreter.py` | 解釋器 - 執行 AST 代碼 |
| `runtime.py` | 運行時環境 - 變量、函數、內置函數 |
| `ast_nodes.py` | AST 節點定義 |
| `main.py` | 主程序入口 |
| `EXAMPLES.nl` | 完整功能示例 |
| `TEST_EXAMPLES.nl` | 詳細測試程序 |
| `LANGUAGE_SPEC.md` | 語言規範與 EBNF 語法 |
| `PROJECT_SUMMARY.md` | 項目完成總結 |

## 💡 語言特性

### 1. 變量與基本類型
```nl
let x = 10
let name = "Alice"
let pi = 3.14
let flag = true
let items = [1, 2, 3]
```

### 2. 運算符
```nl
(* 算術 *)
let sum = a + b
let diff = a - b
let prod = a * b
let quot = a / b
let mod = a % b

(* 比較 *)
a > b,  a < b,  a >= b,  a <= b
a == b, a != b

(* 邏輯 *)
a and b,  a or b,  not a
```

### 3. 條件語句
```nl
if condition then
    print "是的"
else
    print "不是"
end
```

### 4. 循環
```nl
(* While 循環 *)
while i < 10 do
    i = i + 1
end

(* For 循環 *)
for item in items do
    print item
end
```

### 5. 函數
```nl
func greet(name) =
    print "你好,", name
end

func add(a, b) =
    return a + b
end

greet("World")
let result = add(5, 3)
```

### 6. 內置函數
```nl
len(list)           (* 返回列表長度 *)
type(value)         (* 返回值的型態 *)
int(value)          (* 轉換為整數 *)
float(value)        (* 轉換為浮點數 *)
string(value)       (* 轉換為字符串 *)
bool(value)         (* 轉換為布爾值 *)
range(n)            (* 生成 0 到 n-1 的列表 *)
```

## 🔍 常見程序範例

### 範例 1: 計算階乘
```nl
func factorial(n) =
    if n <= 1 then
        return 1
    else
        return n * factorial(n - 1)
    end
end

print "5! =", factorial(5)
```

### 範例 2: 求和
```nl
func sum_range(n) =
    let sum = 0
    let i = 1
    while i <= n do
        sum = sum + i
        i = i + 1
    end
    return sum
end

print "1到100的和:", sum_range(100)
```

### 範例 3: 列表處理
```nl
let numbers = [1, 2, 3, 4, 5]
let sum = 0
for n in numbers do
    sum = sum + n
end
print "列表和:", sum
```

## ⚙️ 系統架構

```
源代碼 (.nl 文件)
    ↓
[詞法分析器] → Token 流
    ↓
[語法分析器] → 抽象語法樹 (AST)
    ↓
[解釋器] → 執行結果
    ↓
[運行時環境] → 變量/函數管理
```

## 🧪 測試功能

已通過測試：
✓ 基本算術運算
✓ 字符串操作
✓ 型態轉換
✓ 布爾邏輯
✓ 條件判斷
✓ 迴圈 (While/For)
✓ 函數定義與遞歸
✓ 列表操作
✓ 內置函數
✓ 複雜表達式

## 🔧 故障排查

### 錯誤: "未定義的變量"
確保變量已使用 `let` 聲明

### 錯誤: "期望換行符"
每個語句必須以換行符結尾

### 錯誤: "未終止的註釋"
確保 `(* 註釋 *)` 中的 *)是正確的

### 錯誤: "期望 xxx"
檢查語法是否正確，特別是 if/while/func 的結尾

## 📖 更多信息

詳見以下文件：
- `LANGUAGE_SPEC.md` - 完整的語言規範和 EBNF 語法
- `PROJECT_SUMMARY.md` - 項目設計和實現詳解
- `README.md` - 項目概述

## 👨‍💻 開發信息

- **語言**: Python 3
- **代碼行數**: ~1,750 行
- **文檔**: 2,575 行（包括文檔）
- **支持平台**: Linux, macOS, Windows (需 Python 3)

## 📝 許可

教學項目 - 可自由使用和修改

---
**最後更新**: 2026-05-31
**版本**: 1.0
**狀態**: ✅ 完全可用
