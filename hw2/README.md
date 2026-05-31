# NL 編程語言設計與解釋器

## 項目概述
設計一個**貼近自然語言、易於理解**的編程語言 **NL (Natural Language)**，並實現其解釋器。

### 語言特點
- ✅ 類似英語/中文的直觀語法
- ✅ 強類型系統（運行時型態推論）
- ✅ 支持基本運算符: `+`, `-`, `*`, `/`, `>`, `<`, `>=`, `<=`, `==`, `!=`, `and`, `or`
- ✅ 條件語句、循環、函數定義
- ✅ 完整的解釋器實現

## 文件結構
```
HW2/
├── README.md                 (本文件)
├── LANGUAGE_SPEC.md          (語言規範與EBNF語法)
├── EXAMPLES.nl               (示例程序)
├── lexer.py                  (詞法分析器)
├── parser.py                 (語法分析器)
├── interpreter.py            (解釋器)
├── runtime.py                (運行時環境)
└── main.py                   (主程序入口)
```

## 快速開始

### 運行程序
```bash
python3 main.py examples.nl
```

### 編寫 NL 程序
NL 程序文件名以 `.nl` 結尾

## 技術架構
1. **詞法分析 (Lexer)**: 將源代碼轉換為 Token 流
2. **語法分析 (Parser)**: 構建抽象語法樹 (AST)
3. **解釋執行 (Interpreter)**: 遞歸訪問 AST 並執行

## 型態系統
- `int` - 整數
- `float` - 浮點數
- `string` - 字符串
- `bool` - 布爾值
- `nil` - 空值

## 垃圾回收
NL 語言使用 **Python 的自動垃圾回收**，無需手動管理內存。
