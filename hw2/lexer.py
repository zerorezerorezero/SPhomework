"""
NL 語言詞法分析器 (Lexer)
將源代碼轉換為 Token 流
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    """Token 類型枚舉"""
    # 字面量
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # 關鍵字
    LET = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    DO = auto()
    FUNC = auto()
    RETURN = auto()
    PRINT = auto()
    READ = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()
    
    # 運算符
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    
    # 比較運算符
    EQ = auto()       # ==
    NE = auto()       # !=
    LT = auto()       # <
    GT = auto()       # >
    LE = auto()       # <=
    GE = auto()       # >=
    
    # 賦值
    ASSIGN = auto()   # =
    
    # 分隔符
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACKET = auto() # [
    RBRACKET = auto() # ]
    LBRACE = auto()   # {
    RBRACE = auto()   # }
    COMMA = auto()    # ,
    COLON = auto()    # :
    NEWLINE = auto()
    
    # 特殊
    EOF = auto()
    ERROR = auto()

@dataclass
class Token:
    """代表一個 Token"""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}, {self.column})"

class Lexer:
    """詞法分析器"""
    
    KEYWORDS = {
        'let': TokenType.LET,
        'if': TokenType.IF,
        'then': TokenType.THEN,
        'else': TokenType.ELSE,
        'end': TokenType.END,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'do': TokenType.DO,
        'func': TokenType.FUNC,
        'return': TokenType.RETURN,
        'print': TokenType.PRINT,
        'read': TokenType.READ,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'nil': TokenType.NIL,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str):
        """報告詞法錯誤"""
        raise SyntaxError(f"詞法錯誤 在行 {self.line}, 列 {self.column}: {message}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """查看當前或未來的字符，不移動指針"""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """讀取一個字符並前進"""
        if self.pos < len(self.source):
            ch = self.source[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return ch
        return None
    
    def skip_whitespace(self):
        """跳過空格和製表符（不包括換行符）"""
        while self.peek() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """跳過註釋"""
        if self.peek() == '(' and self.peek(1) == '*':
            self.advance()  # (
            self.advance()  # *
            while True:
                if self.peek() is None:
                    self.error("未終止的註釋")
                if self.peek() == '*' and self.peek(1) == ')':
                    self.advance()  # *
                    self.advance()  # )
                    break
                self.advance()
    
    def read_string(self) -> str:
        """讀取字符串字面量"""
        quote = self.advance()  # " 或 '
        result = ""
        while True:
            ch = self.peek()
            if ch is None:
                self.error("未終止的字符串")
            if ch == quote:
                self.advance()
                break
            if ch == '\\':
                self.advance()
                next_ch = self.advance()
                if next_ch == 'n':
                    result += '\n'
                elif next_ch == 't':
                    result += '\t'
                elif next_ch == 'r':
                    result += '\r'
                elif next_ch == '\\':
                    result += '\\'
                elif next_ch == quote:
                    result += quote
                else:
                    result += next_ch
            else:
                result += self.advance()
        return result
    
    def read_number(self) -> Token:
        """讀取數字字面量"""
        start_line = self.line
        start_column = self.column
        num_str = ""
        
        while self.peek() and self.peek().isdigit():
            num_str += self.advance()
        
        # 檢查浮點數
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            num_str += self.advance()  # .
            while self.peek() and self.peek().isdigit():
                num_str += self.advance()
            return Token(TokenType.FLOAT, float(num_str), start_line, start_column)
        
        return Token(TokenType.INTEGER, int(num_str), start_line, start_column)
    
    def read_identifier(self) -> Token:
        """讀取標識符或關鍵字"""
        start_line = self.line
        start_column = self.column
        name = ""
        
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            name += self.advance()
        
        # 檢查是否是關鍵字
        if name in self.KEYWORDS:
            token_type = self.KEYWORDS[name]
            return Token(token_type, name, start_line, start_column)
        
        return Token(TokenType.IDENTIFIER, name, start_line, start_column)
    
    def tokenize(self) -> List[Token]:
        """進行詞法分析，返回 Token 列表"""
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            # 檢查註釋
            if self.peek() == '(' and self.peek(1) == '*':
                self.skip_comment()
                continue
            
            line = self.line
            column = self.column
            ch = self.peek()
            
            if ch is None:
                break
            
            # 換行符
            if ch == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', line, column))
                continue
            
            # 字符串
            if ch in '"\'':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, line, column))
                continue
            
            # 數字
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # 標識符或關鍵字
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # 運算符和分隔符
            self.advance()
            
            if ch == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, column))
            elif ch == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line, column))
            elif ch == '*':
                self.tokens.append(Token(TokenType.STAR, '*', line, column))
            elif ch == '/':
                self.tokens.append(Token(TokenType.SLASH, '/', line, column))
            elif ch == '%':
                self.tokens.append(Token(TokenType.PERCENT, '%', line, column))
            elif ch == '=':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', line, column))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', line, column))
            elif ch == '!':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', line, column))
                else:
                    self.error(f"未預期的字符: {ch}")
            elif ch == '<':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', line, column))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', line, column))
            elif ch == '>':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', line, column))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', line, column))
            elif ch == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, column))
            elif ch == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, column))
            elif ch == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', line, column))
            elif ch == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', line, column))
            elif ch == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', line, column))
            elif ch == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', line, column))
            elif ch == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, column))
            elif ch == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, column))
            else:
                self.error(f"未預期的字符: {ch}")
        
        # 添加 EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens


def tokenize(source: str) -> List[Token]:
    """便利函數：直接進行詞法分析"""
    lexer = Lexer(source)
    return lexer.tokenize()
