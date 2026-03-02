# Programming Languages Mastery Skill

## Overview
This skill provides comprehensive mastery knowledge for 15 programming languages across multiple paradigms. All agents should use this skill for writing, optimizing, and understanding code in any supported language.

## Supported Languages

1. **C/C++** - Systems programming, performance-critical applications
2. **Assembly** - x86-64, ARM64, RISC-V - Low-level programming
3. **Rust** - Memory safety, concurrency, systems programming
4. **Haskell** - Functional programming, monads, lazy evaluation
5. **APL/J/K** - Array programming, matrix operations
6. **Python** - AI, scripting, data science
7. **JavaScript/TypeScript** - Web development, Node.js
8. **Go** - Microservices, concurrency, cloud-native
9. **Scala** - Functional + OOP, JVM ecosystem
10. **Prolog** - Logic programming, AI, constraint solving
11. **Lisp/Scheme** - Metaprogramming, macros, S-expressions
12. **Forth/PostScript** - Stack-based programming
13. **Erlang/Elixir** - Distributed systems, fault tolerance
14. **OCaml/F#** - Functional programming, type systems
15. **Solidity** - Smart contracts, blockchain development

---

# LANGUAGE REFERENCE

## 1. C/C++

### Syntax Basics
```c
// C Basic Structure
#include <stdio.h>
#include <stdlib.h>

// Function declaration
int add(int a, int b) {
    return a + b;
}

int main(int argc, char *argv[]) {
    // Variables
    int x = 10;
    float y = 3.14;
    char c = 'A';
    int *ptr = &x;
    
    // Control flow
    if (x > 5) {
        printf("x is greater than 5\n");
    } else if (x == 5) {
        printf("x is 5\n");
    } else {
        printf("x is less than 5\n");
    }
    
    // Loops
    for (int i = 0; i < 10; i++) {
        printf("%d ", i);
    }
    
    // While loop
    while (x > 0) {
        x--;
    }
    
    // Switch
    switch (c) {
        case 'A': printf("A\n"); break;
        case 'B': printf("B\n"); break;
        default: printf("Unknown\n");
    }
    
    return 0;
}
```

### C++ Specific (OOP)
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>

class Animal {
private:
    std::string name;
    int age;
    
public:
    // Constructor
    Animal(const std::string& n, int a) : name(n), age(a) {}
    
    // Virtual destructor for polymorphism
    virtual ~Animal() = default;
    
    // Virtual method
    virtual void speak() const = 0;
    
    // Getter
    std::string getName() const { return name; }
    
    // Template method
    template<typename T>
    T getAgeAs() const {
        return static_cast<T>(age);
    }
};

// Inheritance
class Dog : public Animal {
private:
    std::string breed;
    
public:
    Dog(const std::string& n, int a, const std::string& b)
        : Animal(n, a), breed(b) {}
    
    void speak() const override {
        std::cout << "Woof!" << std::endl;
    }
    
    void fetch() const {
        std::cout << "Fetching ball!" << std::endl;
    }
};

// Modern C++ (C++17/20)
int main() {
    // Smart pointers
    auto dog = std::make_unique<Dog>("Buddy", 3, "Labrador");
    dog->speak();
    
    // Range-based for
    std::vector<int> nums = {1, 2, 3, 4, 5};
    for (const auto& n : nums) {
        std::cout << n << " ";
    }
    
    // Structured bindings
    auto [x, y] = std::make_pair(1, 2);
    
    // Concepts (C++20)
    // template<std::integral T>
    // T add(T a, T b) { return a + b; }
    
    // Coroutines (C++20)
    // co_await, co_yield, co_return
    
    return 0;
}
```

### Advanced Patterns

#### RAII (Resource Acquisition Is Initialization)
```cpp
class FileGuard {
    std::FILE* file;
public:
    FileGuard(const char* path, const char* mode) {
        file = std::fopen(path, mode);
        if (!file) throw std::runtime_error("Cannot open file");
    }
    ~FileGuard() {
        if (file) std::fclose(file);
    }
    // Non-copyable
    FileGuard(const FileGuard&) = delete;
    FileGuard& operator=(const FileGuard&) = delete;
};

void writeData() {
    FileGuard guard("data.txt", "w");
    std::fprintf(guard.get(), "Hello, World!");
} // File automatically closed
```

#### CRTP (Curiously Recurring Template Pattern)
```cpp
template<class Derived>
class Base {
public:
    void interface() {
        static_cast<Derived*>(this)->implementation();
    }
};

class Derived : public Base<Derived> {
public:
    void implementation() {
        std::cout << "Implementation\n";
    }
};
```

### Performance Optimization

#### Cache Optimization
```cpp
// Bad: Cache miss on every access
for (int i = 0; i < N; i++) {
    for (int j = 0; j < M; j++) {
        sum += matrix[j][i];  // Column-major access
    }
}

// Good: Cache-friendly
for (int i = 0; i < N; i++) {
    for (int j = 0; j < M; j++) {
        sum += matrix[i][j];  // Row-major access
    }
}
```

#### Move Semantics
```cpp
class Heavy {
    std::vector<int> data;
public:
    Heavy(Heavy&& other) noexcept : data(std::move(other.data)) {}
    Heavy& operator=(Heavy&& other) noexcept {
        data = std::move(other.data);
        return *this;
    }
};

// Use std::move to avoid copies
Heavy h1;
Heavy h2 = std::move(h1);  // Move, not copy
```

### Use Cases
- Operating systems (Linux kernel, Windows)
- Embedded systems
- High-frequency trading
- Game engines (Unreal, Unity)
- Compilers (GCC, Clang)
- Device drivers
- Performance-critical applications

---

## 2. Assembly (x86-64, ARM64, RISC-V)

### x86-64 Assembly (NASM)

```asm
; Hello World in x86-64 NASM
section .data
    msg db "Hello, World!", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; sys_write(fd=1, buf=msg, count=len)
    mov rax, 1              ; syscall number for write
    mov rdi, 1              ; file descriptor 1 (stdout)
    mov rsi, msg            ; pointer to message
    mov rdx, len            ; message length
    syscall                 ; invoke kernel

    ; sys_exit(status=0)
    mov rax, 60             ; syscall number for exit
    xor rdi, rdi            ; exit code 0
    syscall

; Function with stack frame
section .text
    global add_numbers

add_numbers:
    push rbp
    mov rbp, rsp
    sub rsp, 16             ; allocate local variables
    
    ; Parameters: rdi = a, rsi = b
    mov [rbp-8], rdi        ; store a
    mov [rbp-16], rsi       ; store b
    
    mov rax, [rbp-8]
    add rax, [rbp-16]       ; rax = a + b
    
    leave
    ret
```

### ARM64 Assembly (AArch64)

```asm
// Hello World in ARM64
.section data
msg: .asciz "Hello, World!\n"
len = . - msg

.section text
.global _start
_start:
    // write(fd=1, buf=msg, count=len)
    mov x0, 1              // fd = 1 (stdout)
    adrp x1, msg@PAGE      // load page address
    add x1, x1, msg@PAGEOFF // load offset
    mov x2, len            // length
    mov x16, 4             // syscall number for write
    svc 0                  // invoke kernel

    // exit(status=0)
    mov x0, 0              // status = 0
    mov x16, 1             // syscall number for exit
    svc 0

// Function call example
.global add
add:
    add x0, x0, x1         // x0 = x0 + x1
    ret                     // return

// Loop example
.global sum_array
sum_array:
    cbz x2, .Ldone         // if count == 0, done
    mov x3, 0              // sum = 0
.Lloop:
    ldr x4, [x1], 8       // load *arr++, x4 = *arr
    add x3, x3, x4         // sum += *arr
    subs x2, x2, 1         // count--
    b.ne .Lloop            // if count != 0, loop
.Ldone:
    mov x0, x3             // return sum
    ret
```

### RISC-V Assembly

```asm
# RISC-V RV64G Assembly
.section data
msg: .asciz "Hello, World!\n"
len = 14

.section text
.globl _start
_start:
    # write(fd=1, buf=msg, count=len)
    li a0, 1              # fd = 1
    la a1, msg            # buf = msg
    li a2, 14             # count = len
    li a7, 64             # syscall write
    ecall

    # exit(status=0)
    li a0, 0              # status = 0
    li a7, 93             # syscall exit
    ecall

# Function: int sum(int n)
# a0 = n, returns sum
.globl sum
sum:
    li t0, 0              # i = 0
    li t1, 0              # sum = 0
loop:
    bgt t0, a0, done      # if i > n, done
    add t1, t1, t0        # sum += i
    addi t0, t0, 1       # i++
    j loop
done:
    mv a0, t1            # return sum
    ret
```

### Advanced Patterns

#### System Call Interface (x86-64 Linux)
```asm
; rax = syscall number, rdi, rsi, rdx, r10, r8, r9 = args
; Return in rax

; read(fd, buf, count)
mov rax, 0        ; sys_read
mov rdi, 0        ; fd = stdin
mov rsi, buf      ; buffer
mov rdx, 100     ; count
syscall
```

### Use Cases
- Operating system kernels
- Bootloaders
- Embedded systems
- Performance-critical inner loops
- Cryptography
- Reverse engineering
- Malware analysis

---

## 3. Rust

### Syntax Basics

```rust
// Basic types and variables
fn main() {
    // Immutable by default
    let x = 5;
    let mut y = 10;  // Mutable
    
    // Types
    let i: i32 = 42;
    let f: f64 = 3.14;
    let b: bool = true;
    let c: char = 'x';
    let s: &str = "hello";
    let v: Vec<i32> = vec![1, 2, 3];
    
    // Control flow
    if x > 5 {
        println!("x is greater than 5");
    } else if x == 5 {
        println!("x is 5");
    } else {
        println!("x is less than 5");
    }
    
    // Pattern matching
    match x {
        1 => println!("one"),
        2 => println!("two"),
        n if n > 10 => println!("big: {}", n),
        _ => println!("other"),
    }
    
    // Loops
    for i in 0..10 {
        println!("{}", i);
    }
}

// Functions
fn add(a: i32, b: i32) -> i32 {
    a + b  // No semicolon = return value
}

fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Error handling
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

### Ownership and Borrowing

```rust
// Ownership rules:
// 1. Each value has exactly one owner
// 2. When owner goes out of scope, value is dropped
// 3. Only one mutable reference OR multiple immutable references

fn main() {
    let s1 = String::from("hello");
    let s2 = s1;  // s1 moved to s2
    // println!("{}", s1);  // ERROR: s1 no longer valid
    
    // Borrowing
    let s3 = String::from("world");
    let len = calculate_length(&s3);  // Borrow s3
    
    // Mutable reference
    let mut s4 = String::from("hello");
    change(&mut s4);
}

// Lifetime annotations
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change(s: &mut String) {
    s.push_str(", world");
}
```

### Advanced Patterns

#### Result and Option Chaining
```rust
use std::num::ParseIntError;

fn parse_and_double(s: &str) -> Result<i32, ParseIntError> {
    s.parse::<i32>()
        .map(|n| n * 2)
        .map_err(|e| e)
}

// Using ? operator
fn read_config() -> Result<Config, io::Error> {
    let mut file = File::open("config.json")?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let config: Config = serde_json::from_str(&contents)?;
    Ok(config)
}
```

#### Concurrency
```rust
use std::thread;
use std::sync::{Arc, Mutex};

fn parallel_processing() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);
    let results = Arc::new(Mutex::new(Vec::new()));
    
    let mut handles = vec![];
    
    for item in data.iter() {
        let data = Arc::clone(&data);
        let results = Arc::clone(&results);
        
        let handle = thread::spawn(move || {
            let result = expensive_computation(*item);
            let mut results = results.lock().unwrap();
            results.push(result);
        });
        
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

// Async/Await
async fn fetch_url(url: &str) -> Result<String, reqwest::Error> {
    let response = reqwest::get(url).await?;
    let body = response.text().await?;
    Ok(body)
}
```

#### Traits
```rust
trait Summary {
    fn summarize(&self) -> String;
    fn summarize_author(&self) -> String {
        String::from("(Unknown)")
    }
}

trait Printable {
    fn print(&self);
}

// Blanket implementations
impl<T: Display> Printable for T {
    fn print(&self) {
        println!("{}", self);
    }
}

// Trait bounds
fn notify<T: Summary>(item: &T) {
    println!("Breaking: {}", item.summarize());
}
```

### Use Cases
- Systems programming (OS, filesystems)
- WebAssembly
- CLI tools (ripgrep, fd)
- Web services (Actix, Axum)
- Blockchain (Solana, Polkadot)
- Embedded systems

---

## 4. Haskell

### Syntax Basics

```haskell
-- Basic types
x :: Int
x = 42

y :: Double
y = 3.14

z :: Bool
z = True

name :: String
name = "Hello"

-- Lists
nums :: [Int]
nums = [1, 2, 3, 4, 5]

-- Functions
add :: Int -> Int -> Int
add a b = a + b

-- Pattern matching
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)

-- Guards
grade :: Int -> String
grade n
    | n >= 90 = "A"
    | n >= 80 = "B"
    | n >= 70 = "C"
    | n >= 60 = "D"
    | otherwise = "F"

-- Case expressions
describeList :: [a] -> String
describeList xs = case xs of
    [] -> "Empty list"
    [x] -> "Singleton: " ++ show x
    _ -> "Long list"
```

### Monads

```haskell
-- Maybe monad
safeDiv :: Integral a => a -> a -> Maybe a
safeDiv _ 0 = Nothing
safeDiv a b = Just (a `div` b)

-- Using Maybe with do-notation
calculate :: Int -> Int -> Maybe Int
calculate a b = do
    x <- safeDiv a b
    y <- safeDiv x 2
    return (y + 1)

-- Either monad (error handling)
divide :: Int -> Int -> Either String Int
divide _ 0 = Left "Division by zero"
divide a b = Right (a `div` b)

-- IO monad
main :: IO ()
main = do
    putStrLn "Enter your name:"
    name <- getLine
    putStrLn ("Hello, " ++ name ++ "!")

-- List monad (nondeterministic)
rolls :: [(Int, Int)]
rolls = do
    x <- [1..6]
    y <- [1..6]
    return (x, y)
```

### Advanced Patterns

#### Monoids
```haskell
import Data.Semigroup
import Data.Monoid

newtype Sum a = Sum { getSum :: a }
instance Num a => Semigroup (Sum a) where
    Sum a <> Sum b = Sum (a + b)

instance Num a => Monoid (Sum a) where
    mempty = Sum 0

-- Using Sum monoid
total :: [Int] -> Int
total = getSum . mconcat . map Sum
```

#### Lazy Evaluation
```haskell
-- Infinite list (lazy)
fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Take from infinite list
first10Fibs :: [Integer]
first10Fibs = take 10 fibs
```

### Use Cases
- Compilers (GHC)
- Formal verification
- Financial modeling
- Web servers (Yesod, Servant)
- Parsers (Parsec)
- Cryptography

---

## 5. APL/J/K (Array Programming)

### APL

```apl
⍝ Basic operations
+ - × ÷ ⌈ ⌊ |         ⍝ Arithmetic
∧ ∨ ⍱ ⍲              ⍝ Logical
< ≤ = ≥ > ≠           ⍝ Comparison

⍝ Vector operations
1 2 3 + 4 5 6        ⍝ 5 7 9
+/ 1 2 3 4           ⍝ 10 (sum)
⌈/ 3 1 4 1 5         ⍝ 5 (maximum)

⍝ Matrix
m ← 3 3 ⍴ ⍳9          ⍝ 3×3 matrix
⍉m                    ⍝ transpose

⍝ Functional
{⍵*2}¨ 1 2 3        ⍝ apply function to each
(+/÷≢) 1 2 3 4       ⍝ average
```

### J

```j
NB. Basic operations
+ - * %               NB. add, subtract, multiply, divide

NB. Vector operations
1 2 3 + 4 5 6        NB. 5 7 9
+/ 1 2 3 4           NB. 10 (sum)
>./ 3 1 4 1 5        NB. 5 (maximum)

NB. Matrix
m =. 3 3 $ 1 2 3 4 5 6 7 8 9
|: m                 NB. transpose
```

### K

```k
/ Basic operations
+ - * %              / add, sub, mul, div

/ Vector operations
1 2 3 + 4 5 6       / 5 7 9
+/ 1 2 3 4          / 10 (sum)
|/ 3 1 4 1 5        / 5 (max)

/ Functional
+/!10               / sum 0-9
{x*2}'1 2 3         / apply function
```

### Use Cases
- Financial modeling
- Signal processing
- Machine learning
- Data analysis
- Scientific computing

---

## 6. Python

### Syntax Basics

```python
# Variables and types
x = 42                      # int
y = 3.14                    # float  
z = True                    # bool
s = "hello"                 # str
lst = [1, 2, 3]            # list
tup = (1, 2, 3)            # tuple
d = {"a": 1, "b": 2}       # dict
s = {1, 2, 3}              # set

# Control flow
if x > 10:
    print("big")
elif x == 10:
    print("ten")
else:
    print("small")

# Match statement (Python 3.10+)
match x:
    case 1:
        print("one")
    case n if n > 10:
        print(f"big: {n}")
    case _:
        print("other")

# Loops
for i in range(10):
    print(i)

# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

### Functions

```python
# Basic function
def add(a: int, b: int) -> int:
    return a + b

# Default arguments
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# *args and **kwargs
def func(*args, **kwargs):
    print(args)    # tuple
    print(kwargs)  # dict

# Lambda
square = lambda x: x ** 2

# Decorator
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Took {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

# Generator
def count_to(n):
    for i in range(n):
        yield i

# Async
import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return {"data": 42}

async def main():
    result = await fetch_data()
```

### Classes and OOP

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

class Animal:
    def __init__(self, name: str, age: int):
        self.name = name
        self._age = age
    
    @property
    def age(self):
        return self._age
    
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return "Woof!"
```

### Advanced Patterns

#### Context Managers
```python
class FileManager:
    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

with FileManager("test.txt", "w") as f:
    f.write("Hello")
```

#### Async/Await Patterns
```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()
```

### Use Cases
- AI/ML (PyTorch, TensorFlow)
- Data science (Pandas, NumPy)
- Web development (Django, FastAPI)
- Scripting and automation
- Scientific computing
- DevOps (Ansible, Terraform)

---

## 7. JavaScript/TypeScript

### JavaScript Basics

```javascript
// Variables (ES6+)
let x = 42;           // mutable
const y = 3.14;       // immutable
var z = true;         // avoid (function scope)

// Types
const num = 42;
const str = "hello";
const bool = true;
const arr = [1, 2, 3];
const obj = { a: 1, b: 2 };
const sym = Symbol("id");
const big = 123n;

// Destructuring
const [first, ...rest] = [1, 2, 3, 4];
const { name, age } = { name: "John", age: 30 };

// Control flow
if (x > 10) {
    console.log("big");
} else if (x === 10) {
    console.log("ten");
} else {
    console.log("small");
}

// Ternary
const result = x > 10 ? "big" : "small";

// Switch
switch (x) {
    case 1: console.log("one"); break;
    default: console.log("other");
}

// Loops
for (let i = 0; i < 10; i++) console.log(i);
for (const item of arr) console.log(item);
for (const [key, val] of Object.entries(obj)) console.log(key, val);

// Array methods
arr.map(x => x * 2);
arr.filter(x => x > 5);
arr.reduce((acc, x) => acc + x, 0);
arr.find(x => x > 5);
arr.some(x => x > 5);
arr.every(x => x > 0);
```

### Functions

```javascript
// Function declaration
function add(a, b) {
    return a + b;
}

// Arrow functions
const add = (a, b) => a + b;
const square = x => x * x;

// Default parameters
function greet(name = "World") {
    return `Hello, ${name}!`;
}

// Rest parameters
function sum(...numbers) {
    return numbers.reduce((a, b) => a + b, 0);
}

// Higher-order functions
const apply = (fn, value) => fn(value);
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);

// Closures
function counter() {
    let count = 0;
    return () => ++count;
}

// Callbacks
arr.forEach(item => console.log(item));

// Async functions
async function fetchData() {
    try {
        const response = await fetch(url);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}
```

### Classes

```javascript
class Animal {
    constructor(name, age) {
        this.name = name;
        this._age = age;
    }
    
    speak() {
        console.log("...");
    }
    
    get age() {
        return this._age;
    }
    
    set age(value) {
        if (value < 0) throw new Error("Age cannot be negative");
        this._age = value;
    }
    
    static create(name, age) {
        return new Animal(name, age);
    }
}

class Dog extends Animal {
    constructor(name, age, breed) {
        super(name, age);
        this.breed = breed;
    }
    
    speak() {
        console.log("Woof!");
    }
}
```

### TypeScript

```typescript
// Type annotations
let x: number = 42;
let name: string = "John";
let items: number[] = [1, 2, 3];
let person: { name: string; age: number } = { name: "John", age: 30 };

// Interfaces
interface Person {
    name: string;
    age: number;
    email?: string;  // optional
}

const person: Person = { name: "John", age: 30 };

// Type aliases
type ID = string | number;
type Status = "pending" | "active" | "completed";

// Generics
function identity<T>(arg: T): T {
    return arg;
}

interface Repository<T> {
    find(id: string): Promise<T | null>;
    save(item: T): Promise<void>;
}

// Utility types
type PartialPerson = Partial<Person>;
type RequiredPerson = Required<Person>;
type PickName = Pick<Person, "name">;
type OmitAge = Omit<Person, "age">;
```

### Advanced Patterns

#### Decorators (experimental)
```typescript
function logged(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = function(...args: any[]) {
        console.log(`Calling ${propertyKey} with`, args);
        return original.apply(this, args);
    };
    return descriptor;
}

class Calculator {
    @logged
    add(a: number, b: number): number {
        return a + b;
    }
}
```

#### Async Patterns
```typescript
// Promise chaining
fetch(url)
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));

// Async/await
async function main() {
    try {
        const res = await fetch(url);
        const data = await res.json();
    } catch (e) {
        console.error(e);
    }
}

// Parallel execution
const [users, posts] = await Promise.all([
    fetchUsers(),
    fetchPosts()
]);
```

### Use Cases
- Web development (React, Vue, Angular)
- Node.js backend
- Mobile (React Native)
- Desktop (Electron)
- API development (Express, NestJS)
- Full-stack (Next.js, Nuxt)

---

## 8. Go

### Syntax Basics

```go
package main

import (
    "fmt"
    "strings"
)

func main() {
    // Variables
    var x int = 42
    y := 3.14 // Short declaration
    const Pi = 3.14
    
    // Types
    var s string = "hello"
    var arr []int = []int{1, 2, 3}
    m := map[string]int{"a": 1, "b": 2}
    
    // Control flow
    if x > 10 {
        fmt.Println("big")
    } else if x == 10 {
        fmt.Println("ten")
    } else {
        fmt.Println("small")
    }
    
    // Switch
    switch x {
    case 1:
        fmt.Println("one")
    default:
        fmt.Println("other")
    }
    
    // Loops
    for i := 0; i < 10; i++ {
        fmt.Println(i)
    }
    
    // Range
    for i, v := range arr {
        fmt.Println(i, v)
    }
}
```

### Functions

```go
// Basic function
func add(a, b int) int {
    return a + b
}

// Multiple return values
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// Named return values
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return // naked return
}

// Variadic
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

// Higher-order functions
func apply(n int, fn func(int) int) int {
    return fn(n)
}

// Closure
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}
```

### Structs and Interfaces

```go
type Animal struct {
    Name string
    Age  int
}

func (a *Animal) Speak() string {
    return "..."
}

type Dog struct {
    Animal
    Breed string
}

func (d *Dog) Speak() string {
    return "Woof!"
}

// Interface
type Speaker interface {
    Speak() string
}

func sayHello(s Speaker) {
    fmt.Println(s.Speak())
}
```

### Concurrency

```go
import "sync"

func main() {
    // Goroutines
    go func() {
        fmt.Println("Hello from goroutine")
    }()
    
    // WaitGroups
    var wg sync.WaitGroup
    wg.Add(1)
    go func() {
        defer wg.Done()
        fmt.Println("Working")
    }()
    wg.Wait()
    
    // Channels
    ch := make(chan int)
    go func() {
        ch <- 42 // Send
    }()
    value := <-ch // Receive
    
    // Buffered channel
    buffered := make(chan int, 10)
    
    // Select
    select {
    case msg := <-ch1:
        fmt.Println(msg)
    case ch2 <- data:
        fmt.Println("Sent")
    case <-time.After(time.Second):
        fmt.Println("Timeout")
    }
    
    // Mutex
    var mu sync.Mutex
    mu.Lock()
    // critical section
    mu.Unlock()
}
```

### Error Handling

```go
func readFile(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read %s: %w", path, err)
    }
    return data, nil
}

// Custom error type
type ValidationError struct {
    Field   string
        Message string
}

func (e *ValidationError) Error() string {
    return e.Field + ": " + e.Message
}
```

### Use Cases
- Microservices
- Cloud-native applications
- CLI tools
- Web servers
- DevOps tools (Kubernetes, Docker)
- Networking tools

---

## 9. Scala

### Syntax Basics

```scala
// Variables
val x: Int = 42           // immutable
var y: Double = 3.14      // mutable

// Types
val s: String = "hello"
val lst: List[Int] = List(1, 2, 3)
val m: Map[String, Int] = Map("a" -> 1, "b" -> 2)

// Control flow
if (x > 10) {
    println("big")
} else if (x == 10) {
    println("ten")
} else {
    println("small")
}

// Pattern matching
x match {
    case 1 => println("one")
    case n if n > 10 => println(s"big: $n")
    case _ => println("other")
}

// Loops
for (i <- 0 until 10) println(i)
for (i <- 0 until 10; if i % 2 == 0) println(i)

// For comprehension
val result = for {
    x <- List(1, 2, 3)
    y <- List(4, 5, 6)
} yield x + y
```

### Functions

```scala
// Function
def add(a: Int, b: Int): Int = a + b

// Multiple parameters
def greet(name: String, greeting: String = "Hello"): String = 
    s"$greeting, $name!"

// Recursive
def factorial(n: BigInt): BigInt = 
    if (n <= 1) 1 else n * factorial(n - 1)

// Higher-order
def apply(f: Int => Int, x: Int): Int = f(x)

// Curried
def curriedSum(x: Int)(y: Int): Int = x + y

// By-name parameter
def whileLoop(condition: => Boolean)(body: => Unit): Unit = 
    if (condition) { body; whileLoop(condition)(body) }
```

### Classes and OOP

```scala
// Class
class Animal(val name: String, var age: Int) {
    def speak(): String = "..."
    
    def this(name: String) = this(name, 0)
}

object Animal {
    def apply(name: String, age: Int): Animal = new Animal(name, age)
}

// Case class (immutable, equals, hashCode, copy)
case class Dog(name: String, breed: String) extends Animal(name) {
    override def speak(): String = "Woof!"
}

// Singleton object
object MathUtils {
    def square(x: Int): Int = x * x
}

// Traits (like interfaces with implementation)
trait Walking {
    def walk(): String = "Walking..."
}

trait Running {
    def run(): String = "Running..."
}

class Cat(name: String) extends Animal(name) with Walking with Running {
    override def speak(): String = "Meow!"
    override def walk(): String = "Cat walking"
    override def run(): String = "Cat running"
}
```

### Collections

```scala
// List operations
val lst = List(1, 2, 3, 4, 5)
lst.map(_ * 2)           // List(2, 4, 6, 8, 10)
lst.filter(_ > 2)         // List(3, 4, 5)
lst.reduce(_ + _)         // 15
lst.exists(_ > 3)         // true
lst.forall(_ > 0)         // true
lst.take(3)               // List(1, 2, 3)
lst.drop(2)               // List(3, 4, 5)

// Option handling
val maybe: Option[Int] = Some(42)
maybe.map(_ * 2)          // Some(84)
maybe.getOrElse(0)       // 42
None.getOrElse(0)        // 0

// Either
def divide(a: Int, b: Int): Either[String, Int] = 
    if (b == 0) Left("Error") else Right(a / b)
```

### Futures and Concurrency

```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.ExecutionContext.Implicits.global

def fetchData(id: Int): Future[String] = Future {
    s"Data for $id"
}

val result = for {
    data1 <- fetchData(1)
    data2 <- fetchData(2)
} yield s"$data1 and $data2"
```

### Use Cases
- Apache Spark
- Big data processing
- Web frameworks (Play, Lift)
- Distributed systems
- Compilers (Scalac)

---

## 10. Prolog

### Syntax Basics

```prolog
% Facts
father(john, mary).
father(john, tom).
mother(sue, mary).
mother(sue, tom).

% Rules
parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).

sibling(X, Y) :- 
    parent(Z, X), 
    parent(Z, Y), 
    X \= Y.

% Queries
% ?- parent(john, X).
% X = mary ;
% X = tom.

% ?- grandparent(X, Y).
% X = john,
% Y = mary ;
% X = john,
% Y = tom.
```

### Data Types

```prolog
% Numbers
% 42, 3.14, -17

% Atoms (constants)
% john, mary, 'Hello World'

% Variables (start with uppercase)
% X, Y, Name, _ (anonymous variable)

% Structures
point(3, 5).
date(2024, 1, 15).
person(name(john, smith), age(30)).

% Lists
% [1, 2, 3]
% [head | tail]
% [a, b, c | rest]

% List operations
member(X, [X | _]).
member(X, [_ | T]) :- member(X, T).

append([], L, L).
append([H | T], L2, [H | T2]) :- append(T, L2, T2).

length([], 0).
length([_ | T], N) :- length(T, N1), N is N1 + 1.

reverse([], []).
reverse([H | T], R) :- reverse(T, TR), append(TR, [H], R).
```

### Advanced Patterns

```prolog
% Cut (!) - prevents backtracking
max(X, Y, X) :- X >= Y, !.
max(_, Y, Y).

% If-then-else
% (Condition -> Then ; Else)

% Negation
not(member(X, L)) :- \+ member(X, L).

% Meta-call
call(member(a, [a, b, c])).  % true

% DCG (Definite Clause Grammar)
sentence --> noun_phrase, verb_phrase.
noun_phrase --> det, noun.
det --> [the].
noun --> [cat] ; [dog].
verb_phrase --> verb.
verb --> [sleeps] ; [runs].

% ?- sentence([the, cat, sleeps], []).
% true.

% Findall
% findall(X, goal, List)
% findall(X, parent(_, X), Children).

% Setof
% setof(X, parent(john, X), Children).
```

### Arithmetic

```prolog
% is/2 evaluates arithmetic
add(X, Y, Z) :- Z is X + Y.

factorial(0, 1).
factorial(N, F) :- 
    N > 0, 
    N1 is N - 1, 
    factorial(N1, F1), 
    F is N * F1.

% Built-in
% +, -, *, /, // (integer div), mod, **
% =:=(equal), =\=(not equal), <, >, =<, >=
```

### Use Cases
- AI and expert systems
- Natural language processing
- Constraint solving
- Theorem proving
- Database query languages (Datalog)
- Puzzle solving

---

## 11. Lisp/Scheme

### Basic Syntax

```lisp
; Comments start with ;

;; Variables
(set! x 42)
(define y 3.14)
(define name "John")

;; Types
; Numbers: 42, 3.14, 1/3, #b101, #o52, #x2a
; Strings: "hello"
; Characters: #\a
; Booleans: #t #f
; Symbols: 'foo
; Lists: (1 2 3)
; Vectors: #(1 2 3)

;; Control flow
(if (> x 10)
    (display "big")
    (display "small"))

(cond
    ((> x 10) (display "big"))
    ((= x 10) (display "ten"))
    (else (display "small")))

(case x
    (1 (display "one"))
    (2 (display "two"))
    (else (display "other")))

;; Loops
(do ((i 0 (+ i 1)))
    ((>= i 10))
    (display i))

(let loop ((i 0))
    (if (< i 10)
        (begin
            (display i)
            (loop (+ i 1)))))

(for-each (lambda (x) (display x)) '(1 2 3))
(map (lambda (x) (* x x)) '(1 2 3))
```

### Functions

```lisp
;; Define function
(define (add a b)
    (+ a b))

;; Recursive
(define (factorial n)
    (if (= n 0)
        1
        (* n (factorial (- n 1)))))

;; Higher-order
(define (apply-twice f x)
    (f (f x)))

;; Curried
(define ((add-c a) b)
    (+ a b))

;; Variadic
(define (sum . numbers)
    (apply + numbers))

;; Lambda
(lambda (x y) (+ x y))

;; Closures
(define (make-counter)
    (let ((count 0))
        (lambda ()
            (set! count (+ count 1))
            count)))
```

### Macros

```lisp
;; Define macro
(define-macro (when condition . body)
    `(if ,condition (begin ,@body)))

;; Syntax-rules (hygienic)
(define-syntax when
    (syntax-rules ()
        ((_ condition body ...)
         (if condition (begin body ...)))))

;; Pattern matching macro
(define-syntax case
    (syntax-rules (else)
        ((_ expr ((key ...) body ...) ... (else else-body ...))
         (let ((v expr))
           (cond
             ((memv v '(key ...)) body ...) ...
             (else else-body ...))))
        ((_ expr (key body ...) ...)
         (let ((v expr))
           (cond
             ((memv v '(key)) body ...) ...)))))

;; Loop macro (SRFI)
(do-times (i 10)
    (display i))
```

### Scheme Specific

```lisp
;; Tail recursion (important in Scheme)
(define (factorial n)
    (define (fact n acc)
        (if (= n 0)
            acc
            (fact (- n 1) (* n acc))))
    (fact n 1))

;; Continuations
(define (find-first pred lst)
    (call/cc
        (lambda (return)
            (for-each
                (lambda (x)
                    (when (pred x) (return x)))
                lst)
            #f)))

;; Delayed evaluation
(define (force promise)
    (promise))

(define-macro (delay expr)
    (lambda () expr))

;; Streams (lazy lists)
(define (stream-map f s)
    (cons (car s)
          (delay (stream-map f (force (cdr s))))))

;; Multiple values
(values 1 2 3)
(let-values (((a b c) (values 1 2 3)))
    (display a))
```

### Use Cases
- Emacs (elisp)
- AutoCAD
- Reddit (早期)
- Algorithm research
- Education (SICP)
- Language implementation

---

## 12. Forth/PostScript

### Forth Basics

```forth
\ Comments

\ Stack operations
42 .              \ print 42
1 2 + .           \ prints 3
10 20 SWAP . .   \ prints 20 10
1 2 3 ROT . . .  \ prints 2 3 1
1 2 3 DROP       \ drops 1
1 2 DUP . .      \ duplicates 1

\ Defining words
: SQUARE DUP * ;
5 SQUARE .       \ prints 25

: GREET ." Hello, World!" ;
GREET

\ Variables
VARIABLE COUNTER
10 COUNTER !
COUNTER @ .      \ prints 10

\ Constants
42 CONSTANT ANSWER
ANSWER .         \ prints 42

\ Control flow
: POSITIVE? ( n -- flag )
    0 > ;

-5 POSITIVE? .   \ prints -1 (false)
5 POSITIVE? .   \ prints 0 (true in Forth)

: ABSOLUTE ( n -- n )
    DUP 0< IF NEGATE THEN ;

: FACTORIAL ( n -- n )
    1 SWAP
    BEGIN DUP 1 > WHILE
        SWAP OVER * SWAP 1 -
    REPEAT
    DROP ;

\ Loops
10 0 DO I . LOOP         \ prints 0-9
10 0 DO I 2 MOD 0= IF ." even " THEN LOOP
```

### Advanced Patterns

```forth
\ Creating new control structures
: BEGIN-UNTIL ( flag -- )
    POSTPONE BEGIN
    POSTPONE UNTIL
; IMMEDIATE

\ Vectored execution
' DUP EXECUTE      \ executes DUP

\ Memory
CREATE BUFFER 100 ALLOT
BUFFER 50 C!       \ store byte at offset 50
BUFFER 50 C@       \ fetch byte

\ Strings
: HELLO S" Hello, World!" ;
HELLO TYPE

\ Compilation vs Execution
: HELLO ( -- )
    [ ." compiled" ]
    POSTPONE ." runtime" ;

\ Deferred words
DEFER PRINT
: HELLO-PRINT ." Hello!" ;
' HELLO-PRINT IS PRINT
```

### PostScript

```postscript
% PostScript (stack-based, like Forth)
42 =                    % prints 42
(Hello) =               % prints Hello
[1 2 3] ==              % prints array

% Procedural
/add { add } def
3 4 add =               % prints 7

% Graphics
100 100 moveto
200 200 lineto
stroke

% Functions
/cube { dup mul mul } def
3 cube =                % prints 27

% Conditionals
/x 10 def
x 5 gt { (big) = } { (small) = } ifelse

% Loops
0 { i 10 lt } { i = i 1 add } while
```

### Use Cases
- Embedded systems
- Bootloaders
- Retro computing
- Print documents (PDF/PostScript)
- Forth: OpenFirmware, NASA missions
- PostScript: PDF generation

---

## 13. Erlang/Elixir

### Erlang Basics

```erlang
% Modules
-module(math).
-export([add/2, factorial/1]).

% Functions
add(A, B) -> A + B.

factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

% Pattern matching
sum([]) -> 0;
sum([H|T]) -> H + sum(T).

% Case expressions
describe(X) ->
    case X of
        1 -> "one";
        2 -> "two";
        N when N > 10 -> "big";
        _ -> "other"
    end.

% Guards
is_positive(N) when N > 0 -> true;
is_positive(_) -> false.

% List comprehensions
double(L) -> [X*2 || X <- L].
evens(L) -> [X || X <- L, X rem 2 == 0].

% Records
-record(person, {name, age}).
-demo() ->
    P = #person{name="John", age=30},
    P#person.name.
```

### Concurrency

```erlang
% Spawning processes
Pid = spawn(fun() -> io:format("Hello~n") end).

% Message passing
Pid ! {hello, self()}.

% Receiving messages
receive
    {hello, From} -> io:format("Got hello from ~p~n", [From]);
    {goodbye} -> io:format("Goodbye~n")
after 5000 -> io:format("Timeout~n")
end.

% Process links and monitors
spawn_link(fun() -> ... end).
monitor(process, Pid).

% OTP behaviors
-module(my_server).
-behaviour(gen_server).
-export([init/1, handle_call/3, handle_cast/2]).

init(_) -> {ok, #{}}.
handle_call({add, A, B}, _From, State) -> {reply, A+B, State}.
handle_cast({set, Val}, _State) -> {noreply, #{value => Val}}.
```

### Elixir Basics

```elixir
# Variables
x = 42
y = 3.14

# Types
list = [1, 2, 3]
map = %{a: 1, b: 2}
tuple = {1, 2, 3}

# Pattern matching
[a, b] = [1, 2]
% a = 1, b = 2

# Functions
defmodule Math do
    def add(a, b), do: a + b
    
    # Guard clauses
    def factorial(0), do: 1
    def factorial(n) when n > 0, do: n * factorial(n - 1)
    
    # Default arguments
    def greet(name \\ "World"), do: "Hello, #{name}!"
    
    # Pipe operator
    def process(data) do
        data
        |> validate()
        |> transform()
        |> save()
    end
end

# Control flow
if x > 10, do: "big", else: "small"

cond do
    x > 10 -> "big"
    x == 10 -> "ten"
    true -> "small"
end

# Case
case x do
    1 -> "one"
    n when n > 10 -> "big"
    _ -> "other"
end
```

### Concurrency in Elixir

```elixir
# Spawning processes
spawn(fn -> IO.puts("Hello") end)

# Message passing
send(self(), {:hello, "world"})

receive do
    {:hello, msg} -> IO.puts(msg)
after 5000 -> IO.puts("timeout")
end

# Tasks
task = Task.async(fn -> do_something() end)
result = Task.await(task)

# GenServer
defmodule MyServer do
    use GenServer
    
    def init(state), do: {:ok, state}
    
    def handle_call(:get, _from, state), do: {:reply, state[:value], state}
    def handle_cast({:set, val}, state), do: {:noreply, Map.put(state, :value, val)}
end

# Supervision tree
defmodule App do
    use Application
    
    def start(_type, _args) do
        children = [
            {MyServer, []},
            {DatabasePool, []}
        ]
        Supervisor.start_link(children, strategy: :one_for_one)
    end
end
```

### Use Cases
- Telecom (Ericsson)
- WhatsApp (Erlang)
- Discord (Elixir)
- Distributed systems
- Real-time applications
- Embedded systems (Nerves)

---

## 14. OCaml/F#

### OCaml Basics

```ocaml
(* Variables *)
let x = 42
let y = 3.14
let z = x + int_of_float y  (* 45 *)

(* Immutable by default *)
let x = 10  (* creates new binding *)

(* Types *)
let s : string = "hello"
let lst : int list = [1; 2; 3]
let arr : int array = [|1; 2; 3|]
let opt : int option = Some 42
let pair : int * string = (1, "one")

(* Pattern matching *)
let describe = function
    | 1 -> "one"
    | 2 -> "two"
    | n when n > 10 -> "big"
    | _ -> "other"

(* Functions *)
let add a b = a + b
let rec factorial = function
    | 0 -> 1
    | n -> n * factorial (n - 1)

(* Higher-order *)
let apply f x = f x
let rec map f = function
    | [] -> []
    | h :: t -> f h :: map f t
```

### Advanced Patterns

```ocaml
(* Currying *)
let add = fun a -> fun b -> a + b
let add a b = a + b  (* equivalent *)

(* Partial application *)
let add1 = add 1
let result = add1 5  (* 6 *)

(* Polymorphic *)
let identity x = x
let compose f g x = f (g x)

(* Option handling *)
let safe_div a b =
    match b with
    | 0 -> None
    | _ -> Some (a / b)

(* Error handling *)
let result = match safe_div 10 2 with
    | Some x -> string_of_int x
    | None -> "Error"

(* Monads *)
let bind opt f =
    match opt with
    | Some x -> f x
    | None -> None

(* Lazy *)
let lazy_val = lazy (expensive_calculation ())

(* Functors *)
module type SET = sig
    type 'a t
    val empty : 'a t
    val add : 'a -> 'a t -> 'a t
    val mem : 'a -> 'a t -> bool
end
```

### F# Basics

```fsharp
// Variables
let x = 42
let mutable y = 10
y <- 20  // mutation

// Types
let s: string = "hello"
let lst: int list = [1; 2; 3]
let arr: int array = [|1; 2; 3|]
let opt: int option = Some 42
let result: Result<int, string> = Ok 42

// Pattern matching
let describe = function
    | 1 -> "one"
    | 2 -> "two"
    | n when n > 10 -> "big"
    | _ -> "other"

// Functions
let add a b = a + b
let rec factorial = function
    | 0 -> 1
    | n -> n * factorial (n - 1)

// Pipelines
let result = 
    [1; 2; 3]
    |> List.filter (fun x -> x > 1)
    |> List.map (fun x -> x * 2)

// Computation expressions
type MaybeBuilder() =
    member _.Return(x) = Some x
    member _.Bind(m, f) = Option.bind f m
    member _.Zero() = None

let maybe = MaybeBuilder()
let result = maybe {
    let! x = Some 1
    let! y = Some 2
    return x + y
}
```

### Object-Oriented

```fsharp
type Person(name: string, age: int) =
    member val Name = name with get, set
    member val Age = age with get, set
    
    member this.Greet() = 
        sprintf "Hello, I'm %s" this.Name

    static member Create(name) = Person(name, 0)

// Inheritance
type Student(name, age, grade) =
    inherit Person(name, age)
    member val Grade = grade

// Interface
type IPrintable =
    abstract member Print: unit -> string

type Doc() =
    interface IPrintable with
        member this.Print() = "Document"
```

### Use Cases
- Formal verification (Coq)
- Compilers (F#, OCaml)
- Financial modeling
- Web frameworks (Gatling, Giraffe)
- Data science
- Jane Street trading

---

## 15. Solidity

### Syntax Basics

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Contract definition
contract SimpleStorage {
    // State variables
    uint256 private storedData;
    address public owner;
    
    // Events
    event DataChanged(uint256 newValue);
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    // Function
    function set(uint256 x) public {
        storedData = x;
        emit DataChanged(x);
    }
    
    function get() public view returns (uint256) {
        return storedData;
    }
}
```

### Data Types

```solidity
// Value types
bool flag = true;
int256 signed = -42;
uint256 unsigned = 42;
address addr = 0x123...;
bytes32 hash = keccak256(abi.encodePacked("data"));

// Reference types
uint256[] dynamicArray;
mapping(address => uint256) balanceOf;
struct Person {
    string name;
    uint256 age;
}
enum State { Pending, Active, Completed }

// Arrays
uint256[] arr;
arr.push(1);
arr[0];
arr.length;

// Mappings
mapping(address => uint256) balances;
balances[msg.sender] = 100;
```

### Functions

```solidity
contract Functions {
    // Pure functions (no state access)
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b;
    }
    
    // View functions (read state)
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
    
    // Payable functions (receive Ether)
    function deposit() public payable {
        // msg.value contains Ether sent
    }
    
    function withdraw() public {
        payable(msg.sender).transfer(address(this).balance);
    }
    
    // Visibility: public, private, internal, external
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    function protected() public onlyOwner {
        // only owner can call
    }
}
```

### Advanced Patterns

```solidity
// Inheritance
contract Ownable {
    address public owner;
    constructor() { owner = msg.sender; }
    modifier onlyOwner() { require(msg.sender == owner); _; }
}

contract Token is Ownable {
    mapping(address => uint256) public balances;
    
    function mint(address to, uint256 amount) public onlyOwner {
        balances[to] += amount;
    }
}

// Reentrancy guard
contract Safe {
    bool internal locked;
    
    modifier noReentrant() {
        require(!locked);
        locked = true;
        _;
        locked = false;
    }
    
    function withdraw() public noReentrant {
        payable(msg.sender).transfer(address(this).balance);
    }
}

// ERC-20 Interface
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    event Transfer(address indexed from, address indexed to, uint256 value);
}

// Library
library Math {
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a >= b ? a : b;
    }
}
```

### Security Considerations

```solidity
// Reentrancy
// ✓ Checks-Effects-Interactions pattern
function withdraw() public {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;  // Effect first
    payable(msg.sender).transfer(amount);  // Interaction last
}

// Integer overflow (pre-0.8)
// ✓ Use SafeMath or Solidity 0.8+
uint256 public total = type(uint256).max;

// Access control
// ✓ Use Ownable, Roles

// Front-running
// ✓ Commit-reveal schemes, private transactions
```

### Use Cases
- Decentralized finance (DeFi)
- NFTs (ERC-721, ERC-1155)
- DAOs
- Token contracts
- Decentralized exchanges
- Gaming
- Supply chain tracking

---

# QUICK REFERENCE

## Common Patterns by Language

### Error Handling
- **Rust**: Result<T, E>, Option<T>, ? operator
- **Go**: Multiple return values, error interface
- **Python**: try/except/finally, exceptions
- **JavaScript**: try/catch, Promises
- **Haskell**: Either, Maybe, IO
- **Elixir**: {:ok, value} | {:error, reason}

### Concurrency
- **Go**: Goroutines, channels, select
- **Rust**: async/await, tokio, rayon
- **Erlang/Elixir**: OTP, Actors, GenServer
- **Python**: asyncio, threading
- **JavaScript**: async/await, Web Workers

### Functional Programming
- **Haskell**: Lazy evaluation, monads, functors
- **OCaml/F#**: Pattern matching, algebraic types
- **Scala**: Case classes, for comprehensions
- **Clojure**: Atoms, refs, agents

### Metaprogramming
- **Lisp/Scheme**: Macros, code as data
- **Rust**: Macros, procedural macros
- **Python**: Decorators, metaclasses
- **C++**: Templates, SFINAE
- **Elixir**: Macros

---

This skill provides the foundation for writing production-quality code in any of these 15 programming languages. Use this reference when implementing solutions in any supported language.

## Installation
This is a reference skill. Agents should read and understand the concepts. No installation required.

## Usage
Import this skill to access comprehensive language references. Check the appropriate section for syntax, patterns, and examples in your target language.