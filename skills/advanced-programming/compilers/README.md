# ⚙️ Compiler Design

**Build languages, virtual machines, and JIT compilers**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Programming Languages** | DSLs, general languages | $100K-500K |
| **JIT Compilers** | High-performance execution | $150K-500K |
| **Transpilers** | Code conversion tools | $50K-200K |
| **Static Analyzers** | Linters, type checkers | $30K-150K |
| **VM Implementations** | Language runtimes | $100K-400K |
| **Query Engines** | SQL, GraphQL | $50K-200K |

---

## 📚 Learning Path

### Week 1: Fundamentals
1. Lexical analysis (Lexing)
2. Parsing (LL, LR)
3. AST representation
4. Visitor pattern

### Week 2: Type Systems
1. Type checking
2. Type inference
3. Generics
4. Subtyping

### Week 3: Code Generation
1. Intermediate representation (IR)
2. Register allocation
3. Instruction selection
4. Optimization passes

### Week 4: Advanced
1. JIT compilation
2. Garbage collection
3. Metacompilation
4. LLVM backend

---

## 🔤 Lexer Implementation

### Token Definition
```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

class TokenType(Enum):
    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    FN = auto()
    LET = auto()
    MUT = auto()
    
    # Literals
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
            'fn': TokenType.FN,
            'let': TokenType.LET,
            'mut': TokenType.MUT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
        }
    
    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char
    
    def peek(self) -> Optional[str]:
        if self.is_at_end():
            return None
        return self.source[self.current]
    
    def peek_next(self) -> Optional[str]:
        if self.current + 1 >= len(self.source):
            return None
        return self.source[self.current + 1]
    
    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def add_token(self, type: TokenType, literal=None):
        self.tokens.append(Token(type, self.source[self.start:self.current], literal, self.line, self.column))
    
    def read_string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            raise SyntaxError("Unterminated string")
        
        # Consume closing quote
        self.advance()
        
        # Create token without quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def read_number(self):
        while self.peek() and self.peek().isdigit():
            self.advance()
        
        # Decimal part
        if self.peek() == '.' and self.peek_next() and self.peek_next().isdigit():
            self.advance()  # consume '.'
            while self.peek() and self.peek().isdigit():
                self.advance()
        
        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)
    
    def read_identifier(self):
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENT)
        self.add_token(token_type)
    
    def scan_token(self):
        c = self.advance()
        
        # Single-character tokens
        if c == '(':
            self.add_token(TokenType.LPAREN)
        elif c == ')':
            self.add_token(TokenType.RPAREN)
        elif c == '{':
            self.add_token(TokenType.LBRACE)
        elif c == '}':
            self.add_token(TokenType.RBRACE)
        elif c == '[':
            self.add_token(TokenType.LBRACKET)
        elif c == ']':
            self.add_token(TokenType.RBRACKET)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.SEMICOLON)
        elif c == ':':
            self.add_token(TokenType.COLON)
        
        # Two-character tokens
        elif c == '=':
            if self.match('='):
                self.add_token(TokenType.EQEQ)
            else:
                self.add_token(TokenType.EQ)
        elif c == '!':
            if self.match('='):
                self.add_token(TokenType.NEQ)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LE)
            else:
                self.add_token(TokenType.LT)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.GE)
            else:
                self.add_token(TokenType.GT)
        
        # Whitespace
        elif c == ' ' or c == '\t' or c == '\r':
            pass
        elif c == '\n':
            self.line += 1
            self.column = 1
        
        # String literals
        elif c == '"':
            self.read_string()
        
        # Numbers
        elif c.isdigit():
            self.read_number()
        
        # Identifiers
        elif c.isalpha() or c == '_':
            self.read_identifier()
        
        else:
            raise SyntaxError(f"Unexpected character: {c}")
    
    def tokenize(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.add_token(TokenType.EOF)
        return self.tokens
```

---

## 🌳 Parser Implementation

### AST Nodes
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Expr:
    pass

@dataclass
class LiteralExpr(Expr):
    value: any

@dataclass
class IdentifierExpr(Expr):
    name: str

@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: TokenType
    right: Expr

@dataclass
class UnaryExpr(Expr):
    operator: TokenType
    right: Expr

@dataclass
class CallExpr(Expr):
    callee: Expr
    arguments: List[Expr]

@dataclass
class IfExpr(Expr):
    condition: Expr
    then_branch: Expr
    else_branch: Optional[Expr]

@dataclass
class FunctionExpr(Expr):
    params: List[str]
    body: Expr

# Statements
@dataclass
class Stmt:
    pass

@dataclass
class ExprStmt(Stmt):
    expression: Expr

@dataclass
class LetStmt(Stmt):
    name: str
    initializer: Optional[Expr]

@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]

@dataclass
class BlockStmt(Stmt):
    statements: List[Stmt]

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]
```

### Recursive Descent Parser
```python
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def consume(self, type: TokenType, message: str):
        if self.check(type):
            return self.advance()
        raise SyntaxError(message)
    
    # ===== Grammar Rules =====
    
    def parse(self) -> List[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
    
    def declaration(self) -> Stmt:
        if self.match(TokenType.LET):
            return self.let_statement()
        if self.match(TokenType.FN):
            return self.function_statement()
        return self.statement()
    
    def statement(self) -> Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.LBRACE):
            return self.block_statement()
        return self.expression_statement()
    
    def let_statement(self) -> LetStmt:
        name = self.consume(TokenType.IDENT, "Expected variable name").lexeme
        
        initializer = None
        if self.match(TokenType.EQ):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return LetStmt(name, initializer)
    
    def if_statement(self) -> IfStmt:
        self.consume(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")
        
        then_branch = self.statement()
        
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfStmt(condition, then_branch, else_branch)
    
    def block_statement(self) -> BlockStmt:
        statements = []
        
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return BlockStmt(statements)
    
    def return_statement(self) -> ReturnStmt:
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ReturnStmt(value)
    
    # ===== Expressions =====
    
    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr = self.or_()
        
        if self.match(TokenType.EQ):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, IdentifierExpr):
                return AssignExpr(expr.name, value)
        
        return expr
    
    def or_(self) -> Expr:
        expr = self.and_()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def and_(self) -> Expr:
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expr:
        expr = self.comparison()
        
        while self.match(TokenType.EQEQ, TokenType.NEQ):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expr:
        expr = self.addition()
        
        while self.match(TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE):
            operator = self.previous()
            right = self.addition()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def addition(self) -> Expr:
        expr = self.multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.multiplication()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def multiplication(self) -> Expr:
        expr = self.unary()
        
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expr:
        if self.match(TokenType.MINUS, TokenType.NOT):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)
        
        return self.call()
    
    def call(self) -> Expr:
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: Expr) -> CallExpr:
        arguments = []
        
        if not self.check(TokenType.RPAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        self.consume(TokenType.RPAREN, "Expected ')' after arguments")
        return CallExpr(callee, arguments)
    
    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return LiteralExpr(False)
        if self.match(TokenType.TRUE):
            return LiteralExpr(True)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenType.IDENT):
            return IdentifierExpr(self.previous().lexeme)
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise SyntaxError("Expected expression")
```

---

## ⚡ Intermediate Representation (IR)

### Three-Address Code (TAC)
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TACInstruction:
    """Three-address code instruction"""
    pass

@dataclass
class TACLabel(TACInstruction):
    name: str

@dataclass
class TACAssign(TACInstruction):
    """x = y op z or x = op y"""
    dest: str
    src1: str
    op: Optional[str] = None
    src2: Optional[str] = None

@dataclass
class TACLoad(TACInstruction):
    """x = *y or *x = y"""
    dest: str
    src: str
    is_store: bool = False

@dataclass
class TACBranch(TACInstruction):
    """if x op y goto L or goto L"""
    condition: Optional[tuple] = None
    target: Optional[str] = None

@dataclass
class TACCall(TACInstruction):
    """x = call f(a, b, c)"""
    dest: Optional[str]
    func: str
    args: List[str]

@dataclass
class TACReturn(TACInstruction):
    value: Optional[str]


class IRGenerator:
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_count = 0
        self.label_count = 0
        self.variables = set()
        self.strings = []
    
    def new_temp(self) -> str:
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        self.variables.add(temp)
        return temp
    
    def new_label(self) -> str:
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def generate(self, ast: List[Stmt]) -> List[TACInstruction]:
        for stmt in ast:
            self.visit_stmt(stmt)
        return self.instructions
    
    def visit_stmt(self, stmt: Stmt):
        if isinstance(stmt, LetStmt):
            if stmt.initializer:
                dest = self.visit_expr(stmt.initializer)
                self.variables.add(stmt.name)
                self.instructions.append(TACAssign(stmt.name, dest))
        
        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                ret = self.visit_expr(stmt.value)
                self.instructions.append(TACReturn(ret))
            else:
                self.instructions.append(TACReturn(None))
        
        elif isinstance(stmt, ExprStmt):
            self.visit_expr(stmt.expression)
        
        elif isinstance(stmt, IfStmt):
            cond = self.visit_expr(stmt.condition)
            else_label = self.new_label()
            end_label = self.new_label()
            
            self.instructions.append(TACBranch(
                (cond, "==", "0"),
                else_label
            ))
            
            self.visit_stmt(stmt.then_branch)
            self.instructions.append(TACBranch(None, end_label))
            
            self.instructions.append(TACLabel(else_label))
            if stmt.else_branch:
                self.visit_stmt(stmt.else_branch)
            
            self.instructions.append(TACLabel(end_label))
    
    def visit_expr(self, expr: Expr) -> str:
        if isinstance(expr, LiteralExpr):
            if isinstance(expr.value, bool):
                return "1" if expr.value else "0"
            return str(expr.value)
        
        elif isinstance(expr, IdentifierExpr):
            return expr.name
        
        elif isinstance(expr, BinaryExpr):
            left = self.visit_expr(expr.left)
            right = self.visit_expr(expr.right)
            dest = self.new_temp()
            
            op_map = {
                TokenType.PLUS: "+",
                TokenType.MINUS: "-",
                TokenType.STAR: "*",
                TokenType.SLASH: "/",
                TokenType.EQEQ: "==",
                TokenType.NEQ: "!=",
                TokenType.LT: "<",
                TokenType.GT: ">",
                TokenType.LE: "<=",
                TokenType.GE: ">=",
            }
            
            op = op_map.get(expr.operator, "?")
            self.instructions.append(TACAssign(dest, left, op, right))
            return dest
        
        elif isinstance(expr, CallExpr):
            args = [self.visit_expr(arg) for arg in expr.arguments]
            dest = self.new_temp()
            self.instructions.append(TACCall(dest, expr.callee.name, args))
            return dest
        
        return "?"
```

---

## 🚀 JIT Compiler with LLVM

### Simple JIT
```python
import llvmcore
import llvmlite.ir as ir

class JITCompiler:
    def __init__(self):
        self.module = ir.Module("main")
        self.builder = ir.IRBuilder()
        self.llvm.initialize()
        self.llvm.initialize_all_targets()
        
        # Create execution engine
        self.target = self.llvm.Target.from_default_triple()
        self.target_machine = self.target.create_target_machine()
        self.engine = self.target_machine.create_engine()
    
    def compile_function(self, name: str, args: List[str], body_ir: List[TACInstruction]):
        # Function type
        func_type = ir.FunctionType(ir.IntType(64), [ir.IntType(64)] * len(args))
        
        # Create function
        func = ir.Function(self.module, func_type, name=name)
        
        # Create entry block
        entry = func.append_basic_block(name="entry")
        self.builder.position_at_end(entry)
        
        # Allocate arguments
        arg_values = list(func.args)
        
        # Compile IR to LLVM
        self.compile_ir(body_ir, arg_values)
        
        # Return
        self.builder.ret(ir.Constant(ir.IntType(64), 0))
        
        # Compile to machine code
        self.engine.add_module(self.module)
        self.engine.finalize_object()
        
        # Get function pointer
        return self.engine.get_function_address(name)
    
    def compile_ir(self, ir_instructions: List[TACInstruction], args: List[ir.Value]):
        # Maps temp/var names to LLVM values
        env = {f"t{i}": ir.Constant(ir.IntType(64), 0) for i in range(100)}
        env.update({f"arg{i}": args[i] for i in range(len(args))})
        
        for instr in ir_instructions:
            if isinstance(instr, TACAssign):
                left = env.get(instr.src1, ir.Constant(ir.IntType(64), int(instr.src1) or 0))
                
                if instr.op and instr.src2:
                    right = env.get(instr.src2, ir.Constant(ir.IntType(64), int(instr.src2) or 0))
                    
                    if instr.op == "+":
                        result = self.builder.add(left, right, name=instr.dest)
                    elif instr.op == "-":
                        result = self.builder.sub(left, right, name=instr.dest)
                    elif instr.op == "*":
                        result = self.builder.mul(left, right, name=instr.dest)
                    elif instr.op == "/":
                        result = self.builder.sdiv(left, right, name=instr.dest)
                else:
                    result = left
                
                env[instr.dest] = result
```

---

## 🛠️ Tools

| Tool | Language | Use |
|------|----------|-----|
| **LLVM** | C++ | Production compiler |
| **GCC** | C | GNU compiler |
| **MLIR** | C++ | Compiler infrastructure |
| **ANTLR** | Java | Parser generator |
| **LLVM bindings** | Python | JIT compilation |

---

## 📖 Exercises

### Exercise 1: Calculator
Build calculator with:
- Lexer + Parser + Evaluator
- Support +, -, *, /, ()

### Exercise 2: Type Checker
Add type system:
- Static type inference
- Type errors

### Exercise 3: JIT Compiler
Compile to x- Generate86:
 machine code
- Execute at runtime

---

## 🎯 Next Steps

1. ✅ Read "Crafting Interpreters"
2. 📚 Study "Compilers: Principles and Techniques"
3. 🔒 Read LLVM documentation
4. 📖 Build a toy language
5. 🏆 Contribute to LLVM/MLIR

**Compile all the things! ⚙️**
