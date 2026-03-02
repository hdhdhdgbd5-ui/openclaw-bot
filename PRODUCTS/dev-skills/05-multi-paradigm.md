# MULTI-PARADIGM MASTERCLASS
## Functional, Logic & Object-Oriented Programming

---

## 1. FUNCTIONAL PROGRAMMING

### 1.1 Higher-Order Functions
```python
"""
Higher-Order Functions and Combinators
"""
from functools import reduce, partial, lru_cache
from typing import Callable, TypeVar, List, Iterable
from itertools import islice, takewhile, dropwhile

T = TypeVar('T')
R = TypeVar('R')

# Function composition
def compose(*functions):
    """Compose functions: compose(f, g, h)(x) = f(g(h(x)))"""
    def composed(x):
        result = x
        for func in reversed(functions):
            result = func(result)
        return result
    return composed

# Left-to-right composition (pipe)
def pipe(*functions):
    """Pipe: pipe(f, g, h)(x) = h(g(f(x)))"""
    def piped(x):
        result = x
        for func in functions:
            result = func(result)
        return result
    return piped

# Curry and Uncurry
def curry(f):
    """Curry a function"""
    def curried(*args):
        if len(args) >= f.__code__.co_argcount:
            return f(*args)
        return lambda *more: curried(*(args + more))
    return curried

def uncurry(f):
    """Uncurry a function"""
    def uncurried(*args):
        result = f
        for arg in args:
            result = result(arg)
        return result
    return uncurried

# Combinators
def flip(f):
    """Flip arguments"""
    def flipped(a, b):
        return f(b, a)
    return flipped

def identity(x):
    """Identity function"""
    return x

def constant(x):
    """Constant function - always returns same value"""
    return lambda _: x

def memoize(f):
    """Memoization decorator"""
    cache = {}
    def memoized(*args):
        if args not in cache:
            cache[args] = f(*args)
        return cache[args]
    return memoized

# Monad implementations
class Maybe:
    """Maybe Monad - handles optional values"""
    def __init__(self, value):
        self._value = value
    
    @staticmethod
    def of(value):
        return Maybe(value) if value is not None else Maybe(None)
    
    def map(self, f):
        if self._value is None:
            return Maybe(None)
        return Maybe(f(self._value))
    
    def flat_map(self, f):
        if self._value is None:
            return Maybe(None)
        return f(self._value)
    
    def get_or_else(self, default):
        return self._value if self._value is not None else default
    
    def __repr__(self):
        return f"Maybe({self._value})"

class Either:
    """Either Monad - handles errors"""
    def __init__(self, value, is_left=False):
        self._value = value
        self._is_left = is_left
    
    @staticmethod
    def left(value):
        return Either(value, True)
    
    @staticmethod
    def right(value):
        return Either(value, False)
    
    def map(self, f):
        if self._is_left:
            return self
        return Either(f(self._value))
    
    def flat_map(self, f):
        if self._is_left:
            return self
        return f(self._value)
    
    def get_or_else(self, default):
        return self._value if not self._is_left else default

class IO:
    """IO Monad - wraps side effects"""
    def __init__(self, effect):
        self._effect = effect
    
    @staticmethod
    def of(value):
        return IO(lambda: value)
    
    def map(self, f):
        return IO(lambda: f(self._effect()))
    
    def flat_map(self, f):
        return IO(lambda: f(self._effect())._effect())
    
    def run(self):
        return self._effect()

# List Monad (List Comprehension)
class LazyList:
    """Lazy list for infinite sequences"""
    def __init__(self, generator):
        self._generator = generator
        self._cached = []
        self._exhausted = False
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if len(self._cached) > self._exhausted:
            self._exhausted += 1
            return self._cached[self._exhausted - 1]
        
        value = next(self._generator)
        self._cached.append(value)
        return value
    
    def take(self, n):
        return LazyList(itertools.islice(self, n))
    
    def map(self, f):
        return LazyList(f(x) for x in self)
    
    def filter(self, pred):
        return LazyList(x for x in self if pred(x))
```

### 1.2 Functors & Applicatives
```python
"""
Functor and Applicative Type Classes
"""
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')

class Functor(Generic[T]):
    """Functor - mappable types"""
    def map(self, f: Callable[[T], U]) -> 'Functor[U]':
        raise NotImplementedError

class Applicative(Functor[T]):
    """Applicative - function application within context"""
    @staticmethod
    def pure(value: T) -> 'Applicative[T]':
        raise NotImplementedError
    
    def ap(self, func: 'Applicative[Callable[[T], U]]') -> 'Applicative[U]':
        raise NotImplementedError

# Function as Applicative
class FunctionApp(Applicative[T]):
    def __init__(self, fn: Callable):
        self._fn = fn
    
    @staticmethod
    def pure(value):
        return FunctionApp(lambda _: value)
    
    def map(self, f):
        return FunctionApp(lambda x: f(self._fn(x)))
    
    def ap(self, other):
        return FunctionApp(lambda x: other._fn(x)(self._fn(x)))
    
    def run(self, x):
        return self._fn(x)

# Validation Applicative (for error accumulation)
class Validation:
    """Validation - accumulates errors (unlike Either)"""
    def __init__(self, value, errors=None):
        self.value = value
        self.errors = errors or []
        self.is_valid = len(self.errors) == 0
    
    @staticmethod
    def success(value):
        return Validation(value, [])
    
    @staticmethod
    def failure(errors):
        if isinstance(errors, str):
            errors = [errors]
        return Validation(None, errors)
    
    def map(self, f):
        if self.is_valid:
            return Validation.success(f(self.value))
        return self
    
    def ap(self, other):
        if not self.is_valid or not other.is_valid:
            errors = self.errors + other.errors
            return Validation.failure(errors)
        return Validation.success(other.value(self.value))
```

### 1.3 Lens Library
```python
"""
Lens - Functional approach to immutable data structures
"""
from functools import partial

# Lens definition
class Lens:
    def __init__(self, getter, setter):
        self.get = getter
        self.set = setter
    
    def __call__(self, structure):
        return self.get(structure)
    
    def over(self, transformation):
        """Apply transformation through lens"""
        def transformed(structure):
            old_value = self.get(structure)
            new_value = transformation(old_value)
            return self.set(structure, new_value)
        return transformed
    
    def __mul__(self, other):
        """Compose lenses"""
        def composed_get(structure):
            inner = self.get(structure)
            return other.get(inner)
        
        def composed_set(structure, value):
            inner = self.get(structure)
            new_inner = other.set(inner, value)
            return self.set(structure, new_inner)
        
        return Lens(composed_get, composed_set)
    
    def then(self, transformation):
        """Transform the value through lens"""
        return self.over(transformation)

# Lens creators
def lens(getter, setter):
    return Lens(getter, setter)

def make_lens(*keys):
    """Create lens for nested attribute access"""
    def getter(structure):
        result = structure
        for key in keys:
            result = result[key]
        return result
    
    def setter(structure, value):
        result = structure
        for i, key in enumerate(keys[:-1]):
            result = {**result, key: result[key].copy() if isinstance(result[key], dict) else list(result[key])}
        result[keys[-1]] = value
        return result
    
    return lens(getter, setter)

# Example: Person with address
class Address:
    def __init__(self, city, zipcode):
        self.city = city
        self.zipcode = zipcode

class Person:
    def __init__(self, name, address):
        self.name = name
        self.address = address

# Create lenses
name_lens = lens(lambda p: p.name, lambda p, v: Person(v, p.address))
address_lens = lens(lambda p: p.address, lambda p, v: Person(p.name, v))
city_lens = lens(lambda a: a.city, lambda a, v: Address(v, a.zipcode))

# Compose lenses
person_city = address_lens * city_lens

# Usage
person = Person("Alice", Address("NYC", "10001"))
print(person_city.get(person))  # "NYC"
person2 = person_city.set(person, "Boston")
print(person2.address.city)     # "Boston"
person3 = person_city.over(person, str.upper)
print(person3.address.city)     # "BOSTON"
```

---

## 2. LOGIC PROGRAMMING

### 2.1 Prolog-like Inference Engine
```python
"""
Logic Programming - Prolog-style inference in Python
"""
from typing import Dict, List, Tuple, Any

class Term:
    """Base term class"""
    pass

class Var(Term):
    """Logic variable"""
    def __init__(self, name):
        self.name = name
        self.binding = None
    
    def __str__(self):
        return f"_{self.name}"
    
    def unify(self, other, subst):
        if self.binding:
            return self.binding.unify(other, subst)
        if isinstance(other, Var) and other.binding:
            return other.unify(self, subst)
        subst[self] = other
        return True

class Atom(Term):
    """Constant"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def unify(self, other, subst):
        if isinstance(other, Var):
            return other.unify(self, subst)
        return self.name == other.name

class Predicate(Term):
    """Predicate (functor)"""
    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def __str__(self):
        args_str = ", ".join(str(a) for a in self.args)
        return f"{self.name}({args_str})"
    
    def unify(self, other, subst):
        if isinstance(other, Var):
            return other.unify(self, subst)
        if not isinstance(other, Predicate):
            return False
        if self.name != other.name or len(self.args) != len(other.args):
            return False
        for a1, a2 in zip(self.args, other.args):
            if not a1.unify(a2, subst):
                return False
        return True

class Clause:
    """Horn clause: head :- body"""
    def __init__(self, head, body=None):
        self.head = head
        self.body = body or []
    
    def __str__(self):
        if self.body:
            body_str = ", ".join(str(a) for a in self.body)
            return f"{self.head} :- {body_str}"
        return str(self.head)

class KnowledgeBase:
    """Prolog-like knowledge base"""
    def __init__(self):
        self.facts: List[Predicate] = []
        self.rules: List[Clause] = []
    
    def assertz(self, clause):
        """Add clause to KB"""
        if isinstance(clause, Predicate):
            self.facts.append(clause)
        else:
            self.rules.append(clause)
    
    def query(self, goal, max_solutions=100):
        """Query the KB"""
        if isinstance(goal, str):
            goal = self._parse_term(goal)
        
        for subst in self._prove([goal], {}, max_solutions):
            yield {str(v): str(b) for v, b in subst.items() if isinstance(v, Var)}
    
    def _prove(self, goals, subst, max_solutions, depth=0):
        if not goals or depth > 1000:
            if not goals:
                yield subst.copy()
            return
        
        goal = goals[0]
        rest = goals[1:]
        
        # Try facts
        for fact in self.facts:
            new_subst = subst.copy()
            if goal.unify(fact, new_subst):
                yield from self._prove(
                    self._apply_subst(rest, new_subst),
                    new_subst, max_solutions, depth + 1
                )
        
        # Try rules
        for rule in self.rules:
            new_subst = subst.copy()
            if isinstance(rule.head, Predicate) and goal.unify(rule.head, new_subst):
                new_goals = self._apply_subst(rule.body + rest, new_subst)
                yield from self._prove(new_goals, new_subst, max_solutions, depth + 1)
    
    def _apply_subst(self, terms, subst):
        def apply(term):
            if isinstance(term, Var):
                return subst.get(term, term)
            if isinstance(term, Predicate):
                return Predicate(term.name, [apply(a) for a in term.args])
            return term
        return [apply(t) for t in terms]
    
    def _parse_term(self, s):
        """Simple term parser"""
        s = s.strip()
        if '(' not in s:
            return Atom(s)
        
        name = s[:s.index('(')]
        inner = s[s.index('(')+1:-1]
        args = [self._parse_term(a.strip()) for a in inner.split(',')]
        return Predicate(name, args)

# Example usage
kb = KnowledgeBase()

# Facts
kb.assertz(Atom("male"))
kb.assertz(Atom("female"))
kb.assertz(Predicate("parent", [Atom("alice"), Atom("bob")]))
kb.assertz(Predicate("parent", [Atom("alice"), Atom("carol")]))
kb.assertz(Predicate("parent", [Atom("bob"), Atom("dave")]))

# Rules
# sibling(X, Y) :- parent(P, X), parent(P, Y), X \= Y
sibling = Clause(
    Predicate("sibling", [Var("X"), Var("Y")]),
    [
        Predicate("parent", [Var("P"), Var("X")]),
        Predicate("parent", [Var("P"), Var("Y")]),
    ]
)
kb.assertz(sibling)

# Query
for solution in kb.query("sibling(_X, _Y)"):
    print(solution)
```

---

## 3. REACTIVE PROGRAMMING

### 3.1 Observable Pattern
```python
"""
Reactive Programming - Observable/Observer Pattern
"""
from typing import Callable, List, Any
from abc import ABC, abstractmethod

class Observable:
    """Observable - subject that can be observed"""
    def __init__(self):
        self._observers: List[Callable] = []
    
    def subscribe(self, observer: Callable):
        """Subscribe to updates"""
        self._observers.append(observer)
        return lambda: self._observers.remove(observer)
    
    def unsubscribe(self, observer: Callable):
        """Unsubscribe from updates"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, *args, **kwargs):
        """Notify all observers"""
        for observer in self._observers:
            observer(*args, **kwargs)

class Subject(Observable):
    """Subject - observable with current value"""
    def __init__(self, initial_value=None):
        super().__init__()
        self._value = initial_value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.notify(new_value)

class BehaviorSubject:
    """BehaviorSubject - always has a current value"""
    def __init__(self, initial_value):
        self._value = initial_value
        self._observers: List[Callable] = []
    
    @property
    def value(self):
        return self._value
    
    def subscribe(self, observer: Callable):
        self._observers.append(observer)
        observer(self._value)  # Emit current value immediately
        return lambda: self._observers.remove(observer)
    
    def next(self, value):
        self._value = value
        for observer in self._observers:
            observer(value)

class ReplaySubject:
    """ReplaySubject - replays last N values to new subscribers"""
    def __init__(self, buffer_size=1):
        self._buffer: List[Any] = []
        self._buffer_size = buffer_size
        self._observers: List[Callable] = []
        self._completed = False
    
    def subscribe(self, observer: Callable):
        self._observers.append(observer)
        # Replay buffered values
        for value in self._buffer:
            observer(value)
        return lambda: self._observers.remove(observer)
    
    def next(self, value):
        if self._completed:
            return
        self._buffer.append(value)
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)
        for observer in self._observers:
            observer(value)
    
    def complete(self):
        self._completed = True
        for observer in self._observers:
            observer.__complete__()

class Operator:
    """Base class for reactive operators"""
    def __init__(self, source):
        self._source = source
    
    def subscribe(self, observer):
        return self._source.subscribe(observer)

class Map(Operator):
    """Map operator"""
    def __init__(self, source, transform):
        super().__init__(source)
        self._transform = transform
    
    def subscribe(self, observer):
        def mapped(value):
            observer(self._transform(value))
        return self._source.subscribe(mapped)

class Filter(Operator):
    """Filter operator"""
    def __init__(self, source, predicate):
        super().__init__(source)
        self._predicate = predicate
    
    def subscribe(self, observer):
        def filtered(value):
            if self._predicate(value):
                observer(value)
        return self._source.subscribe(filtered)

class FlatMap(Operator):
    """FlatMap/MergeMap operator"""
    def __init__(self, source, project):
        super().__init__(source)
        self._project = project
    
    def subscribe(self, observer):
        def flattened(value):
            inner = self._project(value)
            inner.subscribe(observer)
        return self._source.subscribe(flattened)
```

---

## 4. CONCURRENT & PARALLEL

### 4.1 Actor Model
```python
"""
Actor Model - Concurrency without shared state
"""
import asyncio
from typing import Any, Dict, List, Callable

class Actor:
    """Base Actor"""
    def __init__(self, address: str):
        self.address = address
        self._mailbox: asyncio.Queue = asyncio.Queue()
        self._handlers: Dict[str, Callable] = {}
    
    async def receive(self, message: Any):
        """Handle incoming message"""
        if isinstance(message, tuple):
            msg_type, payload = message
            handler = self._handlers.get(msg_type)
            if handler:
                await handler(payload)
        else:
            await self.default_handler(message)
    
    async def default_handler(self, message: Any):
        """Override for custom handling"""
        pass
    
    def on(self, msg_type: str):
        """Decorator to register message handler"""
        def decorator(func):
            self._handlers[msg_type] = func
            return func
        return decorator
    
    async def start(self):
        """Main loop"""
        while True:
            message = await self._mailbox.get()
            if message is None:
                break
            await self.receive(message)
    
    async def tell(self, message: Any):
        """Send message (fire and forget)"""
        await self._mailbox.put(message)
    
    async def ask(self, message: Any, timeout=30):
        """Send message and wait for response"""
        future = asyncio.Future()
        
        async def handler(response):
            if not future.done():
                future.set_result(response)
        
        self._handlers['_response'] = handler
        await self._mailbox.put(message)
        
        return await asyncio.wait_for(future, timeout=timeout)

class ActorSystem:
    """Actor System - manages actors"""
    def __init__(self):
        self._actors: Dict[str, Actor] = {}
        self._tasks: List[asyncio.Task] = []
    
    async def spawn(self, actor: Actor):
        """Create and start an actor"""
        self._actors[actor.address] = actor
        task = asyncio.create_task(actor.start())
        self._tasks.append(task)
    
    def actor_of(self, address: str) -> Actor:
        """Get actor by address"""
        return self._actors.get(address)
    
    async def shutdown(self):
        """Shutdown all actors"""
        for actor in self._actors.values():
            await actor._mailbox.put(None)
        await asyncio.gather(*self._tasks)

# Example: Counter Actor
class CounterActor(Actor):
    def __init__(self, address):
        super().__init__(address)
        self.count = 0
    
    @Actor.on
    async def on_increment(self, amount):
        self.count += amount
        print(f"Count: {self.count}")
    
    @Actor.on
    async def on_get_count(self):
        return self.count

# Usage
async def main():
    system = ActorSystem()
    counter = CounterActor("counter")
    await system.spawn(counter)
    
    await counter.tell(('increment', 5))
    await counter.tell(('increment', 3))
    
    result = await counter.ask(('get_count', None))
    print(f"Final count: {result}")
    
    await system.shutdown()

asyncio.run(main())
```

---

## 5. DESIGN PATTERNS

### 5.1 Modern Patterns
```python
"""
Modern Design Patterns in Python
"""

# Singleton (Borg Pattern)
class Borg:
    _shared_state = {}
    
    def __new__(cls):
        obj = super().__new__(cls)
        obj.__dict__ = cls._shared_state
        return obj

# Factory with registration
class Factory:
    _registry = {}
    
    @classmethod
    def register(cls, name, cls_):
        cls._registry[name] = cls_
    
    @classmethod
    def create(cls, name, *args, **kwargs):
        if name not in cls._registry:
            raise ValueError(f"Unknown: {name}")
        return cls._registry[name](*args, **kwargs)

# Dependency Injection
class Container:
    def __init__(self):
        self._services = {}
    
    def register(self, interface, implementation):
        self._services[interface] = implementation
    
    def resolve(self, interface):
        return self._services.get(interface)

# Repository Pattern
class Repository(ABC):
    @abstractmethod
    def get(self, id): pass
    
    @abstractmethod
    def add(self, entity): pass
    
    @abstractmethod
    def delete(self, id): pass

class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}
    
    def get(self, id):
        return self._storage.get(id)
    
    def add(self, entity):
        self._storage[entity.id] = entity
    
    def delete(self, id):
        if id in self._storage:
            del self._storage[id]

# Visitor Pattern
class Visitor:
    def visit_concrete_a(self, element): pass
    def visit_concrete_b(self, element): pass

class Element(ABC):
    @abstractmethod
    def accept(self, visitor): pass

class ConcreteElementA(Element):
    def accept(self, visitor):
        visitor.visit_concrete_a(self)

# Strategy Pattern with decorators
def strategy(func):
    """Strategy decorator"""
    func._is_strategy = True
    return func

class Context:
    def __init__(self):
        self._strategies = {}
    
    def register(self, name, func):
        self._strategies[name] = func
    
    def execute(self, name, *args, **kwargs):
        return self._strategies[name](*args, **kwargs)

# Builder Pattern
class Builder:
    def __init__(self):
        self._object = {}
    
    def set_name(self, name):
        self._object['name'] = name
        return self
    
    def set_age(self, age):
        self._object['age'] = age
        return self
    
    def build(self):
        return self._object.copy()

# Chain of Responsibility
class Handler:
    def __init__(self):
        self._next = None
    
    def set_next(self, handler):
        self._next = handler
        return handler
    
    def handle(self, request):
        if self.can_handle(request):
            return self.process(request)
        if self._next:
            return self._next.handle(request)
        return None
    
    def can_handle(self, request): return True
    def process(self, request): return request
```

---

## 6. TYPE SYSTEM ADVANCED

### 6.1 Generic Types & Constraints
```python
"""
Advanced Type System Features
"""
from typing import TypeVar, Generic, Protocol, Union, Optional
from dataclasses import dataclass

# Generic types
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    def __init__(self):
        self._items = []
    
    def push(self, item: T):
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()
    
    def peek(self) -> T:
        return self._items[-1]

# Generic with constraint
TNumeric = TypeVar('TNumeric', int, float)

def average(a: TNumeric, b: TNumeric) -> float:
    return (a + b) / 2

# Protocol (structural subtyping)
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(d: Drawable) -> None:
    d.draw()

# Type guards
from typing import TypeGuard

def is_list_of_strings(val: any) -> TypeGuard[list[str]]:
    return isinstance(val, list) and all(isinstance(x, str) for x in val)

# NewType for type aliases
from typing import NewType

UserId = NewType('UserId', int)
OrderId = NewType('OrderId', str)

def get_user(user_id: UserId) -> dict:
    return {"id": user_id, "name": "User"}

# Variance
# Covariant (out) - Producer
from typing import Generic, TypeVar

T_co = TypeVar('T_co', covariant=True)

class Producer(Generic[T_co]):
    def produce(self) -> T_co: ...

# Contravariant (in) - Consumer  
T_contra = TypeVar('T_contra', contravariant=True)

class Consumer(Generic[T_contra]):
    def consume(self, item: T_contra) -> None: ...

# Literal types
from typing import Literal

def status(code: Literal[200, 201, 400, 404, 500]) -> str:
    return f"Status: {code}"

# TypedDict
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: Optional[str]

user: UserDict = {"id": 1, "name": "Alice"}
```

---

## 7. METAPROGRAMMING

### 7.1 Decorators & Descriptors
```python
"""
Metaprogramming in Python
"""
import time
from functools import wraps
from typing import get_type_hints, get_origin, get_args

# Decorator factory
def retry(max_attempts=3, delay=1):
    """Retry decorator with configurable attempts"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# Class decorator
def singleton(cls):
    """Singleton decorator"""
    instances = {}
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

# Descriptor
class Validator:
    """Descriptor for validation"""
    def __init__(self, validate):
        self.validate = validate
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not self.validate(value):
            raise ValueError(f"Invalid {self.name}: {value}")
        obj.__dict__[self.name] = value

class Range:
    """Range validator descriptor"""
    def __init__(self, min_val, max_val):
        self.min = min_val
        self.max = max_val
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if not (self.min <= value <= self.max):
            raise ValueError(f"{self.name} must be between {self.min} and {self.max}")
        obj.__dict__[self.name] = value

# Usage of descriptors
class Person:
    name = Validator(lambda x: isinstance(x, str) and len(x) > 0)
    age = Range(0, 150)
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Metaclass
class PluginMeta(type):
    """Metaclass for plugin system"""
    _plugins = {}
    
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if namespace.get('register', False):
            mcs._plugins[name] = cls
        return cls
    
    @classmethod
    def get_plugins(mcs):
        return mcs._plugins

class Plugin(metaclass=PluginMeta):
    register = True
    
    def process(self, data):
        raise NotImplementedError
```

---

*End of Multi-Paradigm Masterclass*
