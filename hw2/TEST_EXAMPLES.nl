(* NL 編程語言 - 測試程序 *)
(* 展示更多語言功能的測試 *)

print "========================================="
print "NL 語言測試程序"
print "========================================="
print ""

(* ===== 測試 1: 字符串和類型轉換 ===== *)
print "[TEST 1] 字符串和型態轉換"
let num = 42
let text = "The answer is "
let message = text + num
print message

let str_num = "123"
let converted = int(str_num)
print "轉換結果:", converted
print ""

(* ===== 測試 2: 浮點數運算 ===== *)
print "[TEST 2] 浮點數運算"
let pi = 3.14159
let radius = 5
let area = pi * radius * radius
print "圓的面積 (半徑=5):", area
print ""

(* ===== 測試 3: 複雜布爾表達式 ===== *)
print "[TEST 3] 複雜布爾表達式"
let x = 10
let y = 20
let z = 30
let result = (x < y) and (y < z) and (x < z)
print "10 < 20 < 30:", result

let result2 = (x > y) or (y < z)
print "(10 > 20) or (20 < 30):", result2
print ""

(* ===== 測試 4: 巢狀函數調用 ===== *)
print "[TEST 4] 巢狀函數調用"
func square(n) =
    return n * n
end

func double(n) =
    return n + n
end

let a = 5
let b = square(a)
let c = double(b)
print "square(5) =", b
print "double(square(5)) =", c
print ""

(* ===== 測試 5: 條件語句中的表達式 ===== *)
print "[TEST 5] 條件語句中的表達式"
let score = 92
if score >= 90 then
    print "等級: A (優秀)"
else
    if score >= 80 then
        print "等級: B (良好)"
    else
        if score >= 70 then
            print "等級: C (及格)"
        else
            if score >= 60 then
                print "等級: D (勉強)"
            else
                print "等級: F (不及格)"
            end
        end
    end
end
print ""

(* ===== 測試 6: 列表操作 ===== *)
print "[TEST 6] 列表操作"
let numbers = [1, 2, 3, 4, 5]
print "列表:", numbers
print "列表長度:", len(numbers)

let mixed_list = [1, "hello", 3.14, true]
print "混合列表:", mixed_list
print ""

(* ===== 測試 7: 使用 for 循環遍歷列表 ===== *)
print "[TEST 7] For 循環遍歷列表"
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits do
    print "水果:", fruit
end
print ""

(* ===== 測試 8: 計算所有數字的乘積 ===== *)
print "[TEST 8] 計算乘積"
func product(numbers) =
    let result = 1
    for num in numbers do
        result = result * num
    end
    return result
end

let nums = [2, 3, 4, 5]
let prod = product(nums)
print "乘積 [2, 3, 4, 5] =", prod
print ""

(* ===== 測試 9: 求最大值 ===== *)
print "[TEST 9] 求最大值"
func max(a, b) =
    if a > b then
        return a
    else
        return b
    end
end

func max_of_three(a, b, c) =
    let max_ab = max(a, b)
    return max(max_ab, c)
end

print "max(10, 20) =", max(10, 20)
print "max_of_three(5, 15, 10) =", max_of_three(5, 15, 10)
print ""

(* ===== 測試 10: 複雜的字符串操作 ===== *)
print "[TEST 10] 字符串操作"
let first_name = "John"
let last_name = "Doe"
let age = 25
let intro = first_name + " " + last_name + " 是 " + age + " 歲"
print intro
print ""

(* ===== 測試 11: 型態檢查 ===== *)
print "[TEST 11] 型態檢查"
let i = 42
let f = 3.14
let s = "hello"
let b = true
let n = nil

print "type(42) =", type(i)
print "type(3.14) =", type(f)
print "type(\"hello\") =", type(s)
print "type(true) =", type(b)
print "type(nil) =", type(n)
print ""

(* ===== 測試 12: 布爾邏輯 ===== *)
print "[TEST 12] 布爾邏輯"
let t = true
let f = false
print "true and true =", t and t
print "true and false =", t and f
print "true or false =", t or f
print "false or false =", f or f
print "not true =", not t
print "not false =", not f
print ""

print "========================================="
print "所有測試完成!"
print "========================================="
