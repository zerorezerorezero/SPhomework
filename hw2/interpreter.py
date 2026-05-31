"""
NL 語言解釋器
遞歸訪問 AST 並執行代碼
"""

import sys
from typing import Any, List
from ast_nodes import *
from runtime import Runtime, NLFunction, NLBuiltinFunction, is_truthy

class Interpreter:
    """NL 語言解釋器"""
    
    def __init__(self):
        self.runtime = Runtime()
    
    def interpret(self, ast: Program) -> Any:
        """解釋程序"""
        last_value = None
        try:
            for statement in ast.statements:
                last_value = self.execute(statement)
        except ReturnValue as ret:
            # 頂層不應該有 return
            raise RuntimeError("return 語句只能用於函數內")
        
        return last_value
    
    def execute(self, node: ASTNode) -> Any:
        """執行一個 AST 節點"""
        if isinstance(node, Program):
            last_value = None
            for stmt in node.statements:
                last_value = self.execute(stmt)
            return last_value
        
        elif isinstance(node, VarDecl):
            return self.execute_var_decl(node)
        
        elif isinstance(node, Assignment):
            return self.execute_assignment(node)
        
        elif isinstance(node, PrintStmt):
            return self.execute_print(node)
        
        elif isinstance(node, ReadStmt):
            return self.execute_read(node)
        
        elif isinstance(node, IfStmt):
            return self.execute_if(node)
        
        elif isinstance(node, WhileStmt):
            return self.execute_while(node)
        
        elif isinstance(node, ForStmt):
            return self.execute_for(node)
        
        elif isinstance(node, FunctionDef):
            return self.execute_function_def(node)
        
        elif isinstance(node, ReturnStmt):
            return self.execute_return(node)
        
        elif isinstance(node, (Literal, BinaryOp, UnaryOp, Identifier, FunctionCall, ListLiteral)):
            return self.evaluate(node)
        
        else:
            raise RuntimeError(f"未知的 AST 節點類型: {type(node)}")
    
    def evaluate(self, expr: ASTNode) -> Any:
        """計算表達式的值"""
        if isinstance(expr, Literal):
            return expr.value
        
        elif isinstance(expr, Identifier):
            return self.runtime.get(expr.name)
        
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr)
        
        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr)
        
        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr)
        
        elif isinstance(expr, ListLiteral):
            return [self.evaluate(elem) for elem in expr.elements]
        
        else:
            raise RuntimeError(f"未知的表達式類型: {type(expr)}")
    
    # ============ 語句執行 ============
    
    def execute_var_decl(self, node: VarDecl) -> Any:
        """執行變量聲明"""
        value = self.evaluate(node.value)
        self.runtime.define(node.name, value)
        return value
    
    def execute_assignment(self, node: Assignment) -> Any:
        """執行賦值"""
        value = self.evaluate(node.value)
        
        if not self.runtime.exists(node.name):
            raise NameError(f"未定義的變量: {node.name}")
        
        self.runtime.set(node.name, value)
        return value
    
    def execute_print(self, node: PrintStmt) -> None:
        """執行打印語句"""
        values = []
        for expr in node.expressions:
            value = self.evaluate(expr)
            values.append(self._format_value(value))
        
        print(" ".join(values))
        return None
    
    def execute_read(self, node: ReadStmt) -> None:
        """執行讀取語句"""
        try:
            line = input()
            value = line
            
            # 嘗試類型轉換
            if node.var_type == 'int':
                value = int(line)
            elif node.var_type == 'float':
                value = float(line)
            elif node.var_type == 'bool':
                value = line.lower() in ('true', '1', 'yes')
            
            self.runtime.define(node.name, value)
        except EOFError:
            self.runtime.define(node.name, None)
        except ValueError as e:
            raise RuntimeError(f"無法讀取 {node.var_type} 型態的值: {e}")
    
    def execute_if(self, node: IfStmt) -> Any:
        """執行條件語句"""
        condition_value = self.evaluate(node.condition)
        
        if is_truthy(condition_value):
            result = None
            for stmt in node.then_body:
                result = self.execute(stmt)
            return result
        elif node.else_body:
            result = None
            for stmt in node.else_body:
                result = self.execute(stmt)
            return result
        
        return None
    
    def execute_while(self, node: WhileStmt) -> Any:
        """執行 While 循環"""
        result = None
        
        while is_truthy(self.evaluate(node.condition)):
            try:
                for stmt in node.body:
                    result = self.execute(stmt)
            except BreakStatement:
                break
            except ContinueStatement:
                continue
        
        return result
    
    def execute_for(self, node: ForStmt) -> Any:
        """執行 For 循環"""
        iterable_value = self.evaluate(node.iterable)
        result = None
        
        if not isinstance(iterable_value, list):
            raise TypeError(f"For 循環期望列表，但得到 {type(iterable_value).__name__}")
        
        for item in iterable_value:
            try:
                self.runtime.define(node.var_name, item)
                for stmt in node.body:
                    result = self.execute(stmt)
            except BreakStatement:
                break
            except ContinueStatement:
                continue
        
        return result
    
    def execute_function_def(self, node: FunctionDef) -> None:
        """執行函數定義"""
        func = NLFunction(node.name, node.parameters, node.body, self.runtime.current_env)
        self.runtime.define(node.name, func)
        return None
    
    def execute_return(self, node: ReturnStmt) -> None:
        """執行返回語句"""
        value = None
        if node.value:
            value = self.evaluate(node.value)
        raise ReturnValue(value)
    
    # ============ 表達式計算 ============
    
    def evaluate_binary_op(self, node: BinaryOp) -> Any:
        """計算二元運算"""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        
        # 算術運算
        if node.op == '+':
            # 字符串連接或數值相加
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        
        elif node.op == '-':
            return left - right
        
        elif node.op == '*':
            return left * right
        
        elif node.op == '/':
            if right == 0:
                raise RuntimeError("除以零")
            # Python 3 的 / 總是返回浮點數
            return left / right
        
        elif node.op == '%':
            if right == 0:
                raise RuntimeError("除以零")
            return left % right
        
        # 比較運算
        elif node.op == '==':
            return left == right
        
        elif node.op == '!=':
            return left != right
        
        elif node.op == '<':
            return left < right
        
        elif node.op == '>':
            return left > right
        
        elif node.op == '<=':
            return left <= right
        
        elif node.op == '>=':
            return left >= right
        
        # 邏輯運算
        elif node.op == 'and':
            return is_truthy(left) and is_truthy(right)
        
        elif node.op == 'or':
            return is_truthy(left) or is_truthy(right)
        
        else:
            raise RuntimeError(f"未知的二元運算符: {node.op}")
    
    def evaluate_unary_op(self, node: UnaryOp) -> Any:
        """計算一元運算"""
        operand = self.evaluate(node.operand)
        
        if node.op == '-':
            return -operand
        
        elif node.op == '+':
            return +operand
        
        elif node.op == 'not':
            return not is_truthy(operand)
        
        else:
            raise RuntimeError(f"未知的一元運算符: {node.op}")
    
    def evaluate_function_call(self, node: FunctionCall) -> Any:
        """計算函數調用"""
        func = self.runtime.get(node.name)
        
        # 計算參數
        args = [self.evaluate(arg) for arg in node.arguments]
        
        # 內置函數
        if isinstance(func, NLBuiltinFunction):
            try:
                return func(*args)
            except TypeError as e:
                raise RuntimeError(f"函數 {node.name} 調用錯誤: {e}")
        
        # 用戶定義函數
        elif isinstance(func, NLFunction):
            if len(args) != len(func.parameters):
                raise RuntimeError(
                    f"函數 {node.name} 期望 {len(func.parameters)} 個參數，"
                    f"但得到 {len(args)} 個"
                )
            
            # 創建新的作用域
            self.runtime.push_environment()
            
            try:
                # 綁定參數
                for param_name, arg_value in zip(func.parameters, args):
                    self.runtime.define(param_name, arg_value)
                
                # 執行函數體
                result = None
                for stmt in func.body:
                    result = self.execute(stmt)
                
                return result
            
            except ReturnValue as ret:
                return ret.value
            
            finally:
                # 恢復作用域
                self.runtime.pop_environment()
        
        else:
            raise TypeError(f"{node.name} 不是函數")
    
    # ============ 輔助方法 ============
    
    def _format_value(self, value: Any) -> str:
        """將值格式化為字符串用於打印"""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif value is None:
            return "nil"
        elif isinstance(value, float):
            # 如果是整數形式的浮點數，去掉 .0
            if value == int(value):
                return str(int(value))
            return str(value)
        elif isinstance(value, list):
            elements = [self._format_value(e) for e in value]
            return "[" + ", ".join(elements) + "]"
        else:
            return str(value)


def interpret(ast: Program) -> Any:
    """便利函數：直接進行解釋"""
    interpreter = Interpreter()
    return interpreter.interpret(ast)
