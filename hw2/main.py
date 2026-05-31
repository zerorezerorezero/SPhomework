#!/usr/bin/env python3
"""
NL 編程語言解釋器
主程序入口

使用方法:
    python3 main.py <program.nl>       # 執行 NL 程序文件
    python3 main.py                    # 交互式模式
"""

import sys
import os
from lexer import tokenize
from parser import parse
from interpreter import interpret


def run_file(filename: str):
    """運行 NL 程序文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        print(f"[NL 解釋器] 執行文件: {filename}")
        print("-" * 50)
        
        # 詞法分析
        tokens = tokenize(source)
        
        # 語法分析
        ast = parse(tokens)
        
        # 解釋執行
        interpret(ast)
        
        print("-" * 50)
        print("[NL 解釋器] 程序執行完成")
    
    except FileNotFoundError:
        print(f"錯誤: 找不到文件 '{filename}'")
        sys.exit(1)
    
    except SyntaxError as e:
        print(f"語法錯誤: {e}")
        sys.exit(1)
    
    except RuntimeError as e:
        print(f"運行時錯誤: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("NL 編程語言解釋器 - 交互式模式")
    print("=" * 60)
    print("輸入 '.help' 查看幫助")
    print("輸入 '.exit' 或 'Ctrl+D' 退出")
    print("=" * 60)
    print()
    
    from runtime import Runtime
    from lexer import Lexer
    from parser import Parser
    from interpreter import Interpreter
    
    interpreter = Interpreter()
    
    while True:
        try:
            # 讀取一行或多行
            line = input(">>> ")
            
            if line.strip() == "":
                continue
            
            if line.strip() == ".help":
                print_help()
                continue
            
            if line.strip() == ".exit":
                print("再見!")
                sys.exit(0)
            
            # 詞法分析
            lexer = Lexer(line + "\n")
            tokens = lexer.tokenize()
            
            # 語法分析
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 解釋執行
            result = interpreter.interpret(ast)
            
            # 如果返回值不是 None，打印它
            if result is not None:
                print(f"=> {result}")
        
        except EOFError:
            print("\n再見!")
            sys.exit(0)
        
        except SyntaxError as e:
            print(f"語法錯誤: {e}")
        
        except RuntimeError as e:
            print(f"運行時錯誤: {e}")
        
        except Exception as e:
            print(f"錯誤: {e}")


def print_help():
    """打印幫助信息"""
    help_text = """
NL 語言速查表
==============

變量聲明:
  let x = 10
  let name = "Alice"
  let pi: float = 3.14

基本運算:
  let sum = a + b
  let diff = a - b
  let prod = a * b
  let quot = a / b
  let mod = a % b

比較運算:
  a > b,  a < b,  a >= b,  a <= b
  a == b, a != b

邏輯運算:
  a and b,  a or b,  not a

條件語句:
  if condition then
      ...
  else
      ...
  end

While 循環:
  while condition do
      ...
  end

函數定義:
  func add(a, b) =
      return a + b
  end

打印和讀取:
  print x, y, z
  read name

內置函數:
  len(list), type(value), int(x), float(x), string(x), bool(x)

命令:
  .help  - 顯示本幫助
  .exit  - 退出解釋器
"""
    print(help_text)


def main():
    """主函數"""
    if len(sys.argv) > 1:
        # 運行指定的文件
        filename = sys.argv[1]
        run_file(filename)
    else:
        # 交互式模式
        interactive_mode()


if __name__ == "__main__":
    main()
