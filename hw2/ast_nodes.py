"""
NL 語言 - 抽象語法樹 (AST) 節點定義
"""

from dataclasses import dataclass
from typing import List, Optional, Any

# ============ 基礎節點 ============

@dataclass
class ASTNode:
    """所有 AST 節點的基類"""
    pass

# ============ 表達式節點 ============

@dataclass
class Literal(ASTNode):
    """字面量: 數字、字符串、布爾值、nil"""
    value: Any
    
    def __repr__(self):
        return f"Literal({self.value!r})"

@dataclass
class Identifier(ASTNode):
    """標識符: 變量名"""
    name: str
    
    def __repr__(self):
        return f"Identifier({self.name})"

@dataclass
class BinaryOp(ASTNode):
    """二元運算: a op b"""
    left: ASTNode
    op: str
    right: ASTNode
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op!r}, {self.right})"

@dataclass
class UnaryOp(ASTNode):
    """一元運算: op a"""
    op: str
    operand: ASTNode
    
    def __repr__(self):
        return f"UnaryOp({self.op!r}, {self.operand})"

@dataclass
class FunctionCall(ASTNode):
    """函數調用: func(arg1, arg2, ...)"""
    name: str
    arguments: List[ASTNode]
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {len(self.arguments)} args)"

@dataclass
class ListLiteral(ASTNode):
    """列表字面量: [1, 2, 3]"""
    elements: List[ASTNode]
    
    def __repr__(self):
        return f"ListLiteral({len(self.elements)} elements)"

# ============ 語句節點 ============

@dataclass
class VarDecl(ASTNode):
    """變量聲明: let x = 5"""
    name: str
    value: ASTNode
    var_type: Optional[str] = None
    
    def __repr__(self):
        return f"VarDecl({self.name})"

@dataclass
class Assignment(ASTNode):
    """賦值: x = 10"""
    name: str
    value: ASTNode
    
    def __repr__(self):
        return f"Assignment({self.name})"

@dataclass
class PrintStmt(ASTNode):
    """打印語句: print x, y, z"""
    expressions: List[ASTNode]
    
    def __repr__(self):
        return f"PrintStmt({len(self.expressions)} expressions)"

@dataclass
class ReadStmt(ASTNode):
    """讀取語句: read x"""
    name: str
    var_type: Optional[str] = None
    
    def __repr__(self):
        return f"ReadStmt({self.name})"

@dataclass
class IfStmt(ASTNode):
    """條件語句: if ... then ... else ... end"""
    condition: ASTNode
    then_body: List[ASTNode]
    else_body: Optional[List[ASTNode]] = None
    
    def __repr__(self):
        return f"IfStmt(condition)"

@dataclass
class WhileStmt(ASTNode):
    """While 循環: while ... do ... end"""
    condition: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"WhileStmt()"

@dataclass
class ForStmt(ASTNode):
    """For 循環: for i in list do ... end"""
    var_name: str
    iterable: ASTNode
    body: List[ASTNode]
    
    def __repr__(self):
        return f"ForStmt({self.var_name})"

@dataclass
class FunctionDef(ASTNode):
    """函數定義: func name(params) = ... end"""
    name: str
    parameters: List[str]
    body: List[ASTNode]
    param_types: Optional[List[str]] = None
    
    def __repr__(self):
        return f"FunctionDef({self.name})"

@dataclass
class ReturnStmt(ASTNode):
    """返回語句: return expr"""
    value: Optional[ASTNode] = None
    
    def __repr__(self):
        return f"ReturnStmt()"

@dataclass
class Program(ASTNode):
    """程序: 語句列表"""
    statements: List[ASTNode]
    
    def __repr__(self):
        return f"Program({len(self.statements)} statements)"


# ============ 用於追蹤程序流的特殊節點 ============

@dataclass
class ReturnValue(Exception):
    """用於實現 return 的異常"""
    value: Any

@dataclass
class BreakStatement(Exception):
    """用於實現 break 的異常"""
    pass

@dataclass
class ContinueStatement(Exception):
    """用於實現 continue 的異常"""
    pass
