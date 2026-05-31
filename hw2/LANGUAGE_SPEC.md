# NL 語言規範與 EBNF 語法

## 1. 語言設計目標

NL (Natural Language) 是一個**貼近自然語言**的編程語言，目標是：
- 代碼易於閱讀和理解
- 語法直觀，接近英語
- 適合初學者學習編程概念
- 支持基本的編程構造

## 2. EBNF 語法定義

```ebnf
(* NL 語言完整文法 *)

Program         = { Statement }

Statement       = VarDecl
                | Assignment
                | PrintStmt
                | ReadStmt
                | IfStmt
                | WhileStmt
                | ForStmt
                | FunctionDef
                | ReturnStmt
                | ExprStmt
                | Block

(* 變量聲明 *)
VarDecl         = "let" Identifier "=" Expression "newline"
                | "let" Identifier ":" Type "=" Expression "newline"

(* 賦值語句 *)
Assignment      = Identifier "=" Expression "newline"

(* 打印語句 *)
PrintStmt       = "print" Expression { "," Expression } "newline"

(* 讀取輸入 *)
ReadStmt        = "read" Identifier [ ":" Type ] "newline"

(* 條件語句 *)
IfStmt          = "if" Expression "then" "newline"
                    { Statement }
                  [ "else" "newline"
                    { Statement } ]
                  "end" "newline"

(* While 循環 *)
WhileStmt       = "while" Expression "do" "newline"
                    { Statement }
                  "end" "newline"

(* For 循環 *)
ForStmt         = "for" Identifier "in" Identifier "do" "newline"
                    { Statement }
                  "end" "newline"

(* 函數定義 *)
FunctionDef     = "func" Identifier "(" [ ParameterList ] ")" "=" "newline"
                    { Statement }
                  "end" "newline"

ParameterList   = Identifier [ ":" Type ] { "," Identifier [ ":" Type ] }

(* 返回語句 *)
ReturnStmt      = "return" Expression "newline"
                | "return" "newline"

(* 表達式語句 *)
ExprStmt        = Expression "newline"

(* 塊語句 *)
Block           = "{" { Statement } "}"

(* 表達式 *)
Expression      = LogicalOr

LogicalOr       = LogicalAnd { "or" LogicalAnd }

LogicalAnd      = Comparison { "and" Comparison }

Comparison      = AddSub { ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) AddSub }

AddSub          = MulDiv { ( "+" | "-" ) MulDiv }

MulDiv          = Unary { ( "*" | "/" | "%" ) Unary }

Unary           = [ "not" | "-" | "+" ] Primary

Primary         = Number
                | String
                | Boolean
                | "nil"
                | Identifier
                | FunctionCall
                | "(" Expression ")"
                | ListLiteral

FunctionCall    = Identifier "(" [ ArgumentList ] ")"

ArgumentList    = Expression { "," Expression }

ListLiteral     = "[" [ Expression { "," Expression } ] "]"

Number          = Integer | Float

Integer         = Digit { Digit }

Float           = Digit { Digit } "." Digit { Digit }

String          = '"' { StringChar } '"'
                | "'" { StringChar } "'"

Boolean         = "true" | "false"

Identifier      = Letter { Letter | Digit | "_" }

Type            = "int" | "float" | "string" | "bool" | "list"

Letter          = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"

Digit           = "0" | "1" | ... | "9"

StringChar      = ? 任何字符除了引號 ?
```

## 3. 語法範例

### 3.1 變量聲明
```
let x = 10
let name = "Alice"
let pi: float = 3.14
```

### 3.2 基本運算
```
let a = 5
let b = 3
let sum = a + b        (* 8 *)
let diff = a - b       (* 2 *)
let prod = a * b       (* 15 *)
let quot = a / b       (* 1.666... *)
let mod = a % b        (* 2 *)
```

### 3.3 比較運算
```
let x = 5
let y = 3
print x > y            (* true *)
print x < y            (* false *)
print x == y           (* false *)
print x != y           (* true *)
```

### 3.4 邏輯運算
```
let sunny = true
let warm = true
if sunny and warm then
    print "Great weather!"
end
```

### 3.5 條件語句
```
let age = 18
if age >= 18 then
    print "You are an adult"
else
    print "You are a minor"
end
```

### 3.6 While 循環
```
let i = 1
while i <= 5 do
    print i
    i = i + 1
end
```

### 3.7 函數定義與調用
```
func add(a, b) =
    return a + b
end

let result = add(3, 4)
print result           (* 7 *)
```

### 3.8 列表 (初步支持)
```
let numbers = [1, 2, 3, 4, 5]
```

## 4. 關鍵字列表

| 關鍵字 | 用途 |
|--------|------|
| `let` | 變量聲明 |
| `if` | 條件開始 |
| `then` | if 的條件真分支 |
| `else` | if 的條件假分支 |
| `end` | 結束 if/while/for/func |
| `while` | While 循環 |
| `for` | For 循環 |
| `in` | For 循環中的 in |
| `do` | While/For 循環開始 |
| `func` | 函數定義 |
| `return` | 返回值 |
| `print` | 打印輸出 |
| `read` | 讀取輸入 |
| `and` | 邏輯與 |
| `or` | 邏輯或 |
| `not` | 邏輯非 |
| `true` | 布爾真 |
| `false` | 布爾假 |
| `nil` | 空值 |

## 5. 運算符優先級

| 優先級 | 運算符 | 關聯性 |
|--------|--------|--------|
| 1 (最高) | `not`, `-`, `+` (一元) | 右 |
| 2 | `*`, `/`, `%` | 左 |
| 3 | `+`, `-` (二元) | 左 |
| 4 | `<`, `>`, `<=`, `>=` | 左 |
| 5 | `==`, `!=` | 左 |
| 6 | `and` | 左 |
| 7 (最低) | `or` | 左 |

## 6. 型態系統

### 6.1 基本型態
- `int` - 32 位整數
- `float` - 浮點數
- `string` - 字符串
- `bool` - 布爾值 (true/false)
- `nil` - 空值
- `list` - 列表

### 6.2 型態推論
NL 在**運行時進行型態推論**，變量類型由第一個賦值決定。

### 6.3 型態轉換
自動進行隱式型態轉換：
- `int` + `float` → `float`
- `string` + `string` → `string`
- 其他混合操作遵循常見規則

## 7. 內建函數

| 函數 | 說明 |
|-----|------|
| `print(...)` | 打印到控制台，支持多個參數 |
| `read()` | 從標準輸入讀取一行 |
| `len(list)` | 返回列表長度 |
| `type(value)` | 返回值的類型 |
| `int(value)` | 轉換為整數 |
| `float(value)` | 轉換為浮點數 |
| `string(value)` | 轉換為字符串 |

## 8. 作用域規則

- 全局作用域：程序頂層定義的變量
- 局部作用域：函數內定義的變量，函數退出後銷毀
- 變量隱藏：內層作用域可以隱藏外層同名變量

## 9. 錯誤處理

NL 提供基本的運行時錯誤檢測：
- 未定義的變量使用
- 類型不匹配操作
- 除以零
- 數組索引越界
- 函數參數數量不匹配
