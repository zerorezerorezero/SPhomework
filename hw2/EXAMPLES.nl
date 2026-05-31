(* NL 編程語言示例程序 *)
(* 這個文件展示 NL 語言的各種功能 *)

(* ===== 示例 1: 基本變量和打印 ===== *)
(* 基本算術 *)
let x = 10
let y = 3
print "Basic Arithmetic:"
print "x =", x
print "y =", y
print "x + y =", x + y
print "x - y =", x - y
print "x * y =", x * y
print "x / y =", x / y
print "x % y =", x % y
print ""

(* ===== 示例 2: 比較和邏輯運算 ===== *)
print "Comparisons and Logic:"
print "x > y =", x > y
print "x < y =", x < y
print "x == y =", x == y
print "x != y =", x != y
print "x >= y =", x >= y
print "x <= y =", x <= y
print "true and false =", true and false
print "true or false =", true or false
print "not true =", not true
print ""

(* ===== 示例 3: 條件語句 ===== *)
print "Conditional Statements:"
let age = 20
if age >= 18 then
    print "You are an adult"
else
    print "You are a minor"
end
print ""

(* ===== 示例 4: While 循環 ===== *)
print "While Loop (1 to 5):"
let i = 1
while i <= 5 do
    print "Count:", i
    i = i + 1
end
print ""

(* ===== 示例 5: 函數定義 ===== *)
print "Function Definition:"
func add(a, b) =
    return a + b
end

func multiply(a, b) =
    return a * b
end

func greet(name) =
    print "Hello,", name
end

let result1 = add(7, 3)
print "add(7, 3) =", result1

let result2 = multiply(4, 5)
print "multiply(4, 5) =", result2

greet("Alice")
print ""

(* ===== 示例 6: 階乘函數 ===== *)
print "Factorial Function:"
func factorial(n) =
    if n <= 1 then
        return 1
    else
        return n * factorial(n - 1)
    end
end

print "factorial(5) =", factorial(5)
print ""

(* ===== 示例 7: 字符串操作 ===== *)
print "String Operations:"
let greeting = "Hello"
let name = "World"
print greeting, name
let message = greeting + " " + name
print message
print ""

(* ===== 示例 8: 複雜表達式 ===== *)
print "Complex Expressions:"
let a = 5
let b = 10
let c = (a + b) * 2
print "a = ", a
print "b = ", b
print "(a + b) * 2 = ", c
print ""

(* ===== 示例 9: 嵌套條件和循環 ===== *)
print "Nested Conditions:"
let score = 85
if score >= 90 then
    print "Grade: A"
else
    if score >= 80 then
        print "Grade: B"
    else
        if score >= 70 then
            print "Grade: C"
        else
            print "Grade: F"
        end
    end
end
print ""

(* ===== 示例 10: 數字求和 ===== *)
print "Sum of Numbers 1 to 10:"
func sum_to_n(n) =
    let sum = 0
    let i = 1
    while i <= n do
        sum = sum + i
        i = i + 1
    end
    return sum
end

print "Sum =", sum_to_n(10)
