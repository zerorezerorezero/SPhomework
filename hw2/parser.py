"""
NL 語言語法分析器 (Parser)
將 Token 流轉換為抽象語法樹 (AST)
"""

from typing import List, Optional
from lexer import Token, TokenType
from ast_nodes import *

class Parser:
    """語法分析器"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def error(self, message: str):
        """報告語法錯誤"""
        token = self.current_token()
        raise SyntaxError(f"語法錯誤 在行 {token.line}, 列 {token.column}: {message}")
    
    def current_token(self) -> Token:
        """獲取當前 Token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token
    
    def peek_token(self, offset: int = 0) -> Token:
        """查看當前或未來的 Token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        """移動到下一個 Token 並返回當前 Token"""
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """期望某個特定的 Token 類型"""
        token = self.current_token()
        if token.type != token_type:
            self.error(f"期望 {token_type.name}，但得到 {token.type.name}")
        return self.advance()
    
    def skip_newlines(self):
        """跳過所有換行符"""
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """檢查當前 Token 是否匹配某些類型之一"""
        return self.current_token().type in token_types
    
    def parse(self) -> Program:
        """解析程序"""
        statements = []
        self.skip_newlines()
        
        while self.current_token().type != TokenType.EOF:
            self.skip_newlines()
            if self.current_token().type == TokenType.EOF:
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """解析一個語句"""
        token = self.current_token()
        
        if token.type == TokenType.LET:
            return self.parse_var_decl()
        elif token.type == TokenType.PRINT:
            return self.parse_print_stmt()
        elif token.type == TokenType.READ:
            return self.parse_read_stmt()
        elif token.type == TokenType.IF:
            return self.parse_if_stmt()
        elif token.type == TokenType.WHILE:
            return self.parse_while_stmt()
        elif token.type == TokenType.FOR:
            return self.parse_for_stmt()
        elif token.type == TokenType.FUNC:
            return self.parse_function_def()
        elif token.type == TokenType.RETURN:
            return self.parse_return_stmt()
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_assignment_or_expr()
        else:
            self.error(f"未預期的語句開始: {token.type.name}")
    
    def parse_var_decl(self) -> VarDecl:
        """解析變量聲明: let x = 5 或 let x: int = 5"""
        self.expect(TokenType.LET)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        var_type = None
        if self.match(TokenType.COLON):
            self.advance()
            type_token = self.expect(TokenType.IDENTIFIER)
            var_type = type_token.value
        
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect(TokenType.NEWLINE)
        
        return VarDecl(name, value, var_type)
    
    def parse_assignment_or_expr(self) -> ASTNode:
        """解析賦值或表達式語句"""
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            self.expect(TokenType.NEWLINE)
            return Assignment(name, value)
        else:
            # 這是一個表達式語句 (實際上就是函數調用或單純的表達式)
            self.pos -= 1  # 回退，重新解析為表達式
            expr = self.parse_expression()
            self.expect(TokenType.NEWLINE)
            return expr
    
    def parse_print_stmt(self) -> PrintStmt:
        """解析打印語句: print x, y, z"""
        self.expect(TokenType.PRINT)
        expressions = []
        
        expressions.append(self.parse_expression())
        
        while self.match(TokenType.COMMA):
            self.advance()
            expressions.append(self.parse_expression())
        
        self.expect(TokenType.NEWLINE)
        return PrintStmt(expressions)
    
    def parse_read_stmt(self) -> ReadStmt:
        """解析讀取語句: read x 或 read x: int"""
        self.expect(TokenType.READ)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        var_type = None
        if self.match(TokenType.COLON):
            self.advance()
            type_token = self.expect(TokenType.IDENTIFIER)
            var_type = type_token.value
        
        self.expect(TokenType.NEWLINE)
        return ReadStmt(name, var_type)
    
    def parse_if_stmt(self) -> IfStmt:
        """解析條件語句: if ... then ... else ... end"""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        self.expect(TokenType.NEWLINE)
        
        then_body = self.parse_block_until(TokenType.ELSE, TokenType.END)
        
        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.NEWLINE)
            else_body = self.parse_block_until(TokenType.END)
        
        self.expect(TokenType.END)
        self.expect(TokenType.NEWLINE)
        
        return IfStmt(condition, then_body, else_body)
    
    def parse_while_stmt(self) -> WhileStmt:
        """解析 While 循環: while ... do ... end"""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.DO)
        self.expect(TokenType.NEWLINE)
        
        body = self.parse_block_until(TokenType.END)
        
        self.expect(TokenType.END)
        self.expect(TokenType.NEWLINE)
        
        return WhileStmt(condition, body)
    
    def parse_for_stmt(self) -> ForStmt:
        """解析 For 循環: for i in list do ... end"""
        self.expect(TokenType.FOR)
        var_token = self.expect(TokenType.IDENTIFIER)
        var_name = var_token.value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.DO)
        self.expect(TokenType.NEWLINE)
        
        body = self.parse_block_until(TokenType.END)
        
        self.expect(TokenType.END)
        self.expect(TokenType.NEWLINE)
        
        return ForStmt(var_name, iterable, body)
    
    def parse_function_def(self) -> FunctionDef:
        """解析函數定義: func name(a, b) = ... end"""
        self.expect(TokenType.FUNC)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        parameters = []
        param_types = []
        
        if not self.match(TokenType.RPAREN):
            param_token = self.expect(TokenType.IDENTIFIER)
            parameters.append(param_token.value)
            
            if self.match(TokenType.COLON):
                self.advance()
                type_token = self.expect(TokenType.IDENTIFIER)
                param_types.append(type_token.value)
            else:
                param_types.append(None)
            
            while self.match(TokenType.COMMA):
                self.advance()
                param_token = self.expect(TokenType.IDENTIFIER)
                parameters.append(param_token.value)
                
                if self.match(TokenType.COLON):
                    self.advance()
                    type_token = self.expect(TokenType.IDENTIFIER)
                    param_types.append(type_token.value)
                else:
                    param_types.append(None)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ASSIGN)
        self.expect(TokenType.NEWLINE)
        
        body = self.parse_block_until(TokenType.END)
        
        self.expect(TokenType.END)
        self.expect(TokenType.NEWLINE)
        
        param_types_list = param_types if any(pt is not None for pt in param_types) else None
        return FunctionDef(name, parameters, body, param_types_list)
    
    def parse_return_stmt(self) -> ReturnStmt:
        """解析返回語句: return expr 或 return"""
        self.expect(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.NEWLINE):
            value = self.parse_expression()
        
        self.expect(TokenType.NEWLINE)
        return ReturnStmt(value)
    
    def parse_block_until(self, *end_tokens: TokenType) -> List[ASTNode]:
        """解析語句塊直到遇到結束標記"""
        statements = []
        
        while self.current_token().type not in end_tokens:
            self.skip_newlines()
            if self.current_token().type in end_tokens:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return statements
    
    def parse_expression(self) -> ASTNode:
        """解析表達式"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """解析邏輯或: expr or expr"""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op_token = self.advance()
            right = self.parse_logical_and()
            left = BinaryOp(left, op_token.value, right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """解析邏輯與: expr and expr"""
        left = self.parse_comparison()
        
        while self.match(TokenType.AND):
            op_token = self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, op_token.value, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """解析比較: expr == expr, expr < expr, 等等"""
        left = self.parse_additive()
        
        while self.match(TokenType.EQ, TokenType.NE, TokenType.LT, 
                         TokenType.GT, TokenType.LE, TokenType.GE):
            op_token = self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op_token.value, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """解析加法和減法: expr + expr, expr - expr"""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op_token.value, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """解析乘法、除法、取模: expr * expr, expr / expr, expr % expr"""
        left = self.parse_unary()
        
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op_token.value, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """解析一元運算: -expr, not expr"""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op_token = self.advance()
            expr = self.parse_unary()
            return UnaryOp(op_token.value, expr)
        
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        """解析主表達式: 字面量、標識符、函數調用、括號表達式"""
        token = self.current_token()
        
        # 數字
        if token.type == TokenType.INTEGER:
            self.advance()
            return Literal(token.value)
        
        # 浮點數
        elif token.type == TokenType.FLOAT:
            self.advance()
            return Literal(token.value)
        
        # 字符串
        elif token.type == TokenType.STRING:
            self.advance()
            return Literal(token.value)
        
        # 布爾值
        elif token.type == TokenType.TRUE:
            self.advance()
            return Literal(True)
        
        elif token.type == TokenType.FALSE:
            self.advance()
            return Literal(False)
        
        # nil
        elif token.type == TokenType.NIL:
            self.advance()
            return Literal(None)
        
        # 列表
        elif token.type == TokenType.LBRACKET:
            return self.parse_list_literal()
        
        # 括號表達式
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # 標識符或函數調用
        elif token.type == TokenType.IDENTIFIER:
            name_token = self.advance()
            name = name_token.value
            
            # 函數調用
            if self.match(TokenType.LPAREN):
                self.advance()
                arguments = []
                
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.parse_expression())
                
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, arguments)
            
            # 普通標識符
            else:
                return Identifier(name)
        
        else:
            self.error(f"未預期的主表達式: {token.type.name}")
    
    def parse_list_literal(self) -> ListLiteral:
        """解析列表字面量: [1, 2, 3]"""
        self.expect(TokenType.LBRACKET)
        elements = []
        
        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            
            while self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.RBRACKET):
                    break
                elements.append(self.parse_expression())
        
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements)


def parse(tokens: List[Token]) -> Program:
    """便利函數：直接進行語法分析"""
    parser = Parser(tokens)
    return parser.parse()
