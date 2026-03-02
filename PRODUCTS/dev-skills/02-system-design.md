# SYSTEM DESIGN MASTERCLASS
## Distributed Systems, Microservices & Planet-Scale Architecture

---

## 1. DISTRIBUTED SYSTEMS FUNDAMENTALS

### 1.1 CAP Theorem & Trade-offs
```
        CAP Theorem:
        
        C - Consistency     → All nodes see same data
        A - Availability    → Every request gets response
        P - Partition Tolerance → System works despite network failures
        
        ⚠️  CANNOT have all 3 simultaneously!
        
        CA (not partition tolerant) → Single node databases
        CP (not available during partitions) → Distributed databases (ZooKeeper, etcd)
        AP (not consistent during partitions) → DNS, Cassandra, DynamoDB
```

### 1.2 PACELC Model
```
    If Partition (P):
        - E (Evacuate) → Choose between A or C
    Else (E):
        - L (Latency) → Choose between C or L
        - C (Consistency)
```

---

## 2. CONSENSUS ALGORITHMS

### 2.1 Raft Consensus (Complete Implementation)
```python
"""
Raft Consensus Algorithm
- Leader election
- Log replication
- Safety guarantees
"""
import time
import random
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict
import threading

class NodeState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

@dataclass
class LogEntry:
    term: int
    index: int
    command: str

class RaftNode:
    def __init__(self, node_id: int, peers: List[int]):
        self.node_id = node_id
        self.peers = peers
        self.current_term = 0
        self.voted_for: Optional[int] = None
        self.log: List[LogEntry] = []
        self.state = NodeState.FOLLOWER
        self.commit_index = 0
        self.next_index: Dict[int, int] = {}
        self.match_index: Dict[int, int] = {}
        self.election_timeout = random.uniform(150, 300)
        self.last_contact = time.time()
        self.lock = threading.Lock()
        for peer in peers:
            self.next_index[peer] = len(self.log) + 1
            self.match_index[peer] = 0
    
    def become_follower(self, term: int):
        with self.lock:
            self.state = NodeState.FOLLOWER
            self.current_term = term
            self.voted_for = None
            self.last_contact = time.time()
    
    def become_leader(self):
        with self.lock:
            self.state = NodeState.LEADER
            for peer in self.peers:
                self.next_index[peer] = len(self.log) + 1
                self.match_index[peer] = 0
    
    def request_vote(self, candidate_id: int, candidate_term: int, 
                     last_log_index: int, last_log_term: int) -> Dict:
        with self.lock:
            if candidate_term < self.current_term:
                return {'term': self.current_term, 'vote_granted': False}
            if candidate_term > self.current_term:
                self.become_follower(candidate_term)
            log_ok = (self.voted_for is None or self.voted_for == candidate_id)
            log_ok = log_ok and self.is_log_up_to_date(last_log_index, last_log_term)
            if log_ok:
                self.voted_for = candidate_id
                self.last_contact = time.time()
                return {'term': self.current_term, 'vote_granted': True}
            return {'term': self.current_term, 'vote_granted': False}
    
    def is_log_up_to_date(self, last_log_index: int, last_log_term: int) -> bool:
        if not self.log:
            return True
        last_term = self.log[-1].term
        return (last_log_term > last_term) or (last_log_term == last_term and last_log_index >= len(self.log) - 1)
    
    def start_command(self, command: str) -> bool:
        with self.lock:
            if self.state != NodeState.LEADER:
                return False
            entry = LogEntry(self.current_term, len(self.log), command)
            self.log.append(entry)
            return True
    
    def commit_majority_entries(self) -> bool:
        for idx in range(self.commit_index + 1, len(self.log)):
            count = 1
            for peer in self.peers:
                if self.match_index[peer] >= idx:
                    count += 1
            if count > len(self.peers) // 2:
                self.commit_index = idx
            else:
                break
        return True
```

---

## 3. DISTRIBUTED DATA STORES

### 3.1 Consistent Hashing
```python
"""
Consistent Hashing with Virtual Nodes
"""
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, vnodes=150):
        self.vnodes = vnodes
        self.ring = []
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def add_node(self, node):
        for i in range(self.vnodes):
            vnode_key = f"{node}#VN{i}"
            hash_key = self._hash(vnode_key)
            self.ring.append((hash_key, node))
        self.ring.sort(key=lambda x: x[0])
        self.sorted_keys = [k for k, _ in self.ring]
    
    def get_node(self, key):
        if not self.ring:
            raise ValueError("No nodes in ring")
        hash_key = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, hash_key)
        if idx >= len(self.ring):
            idx = 0
        return self.ring[idx][1]
```

### 3.2 CRDTs
```python
"""
CRDTs - Conflict-free Replicated Data Types
"""
import time

class GCounter:
    def __init__(self, node_id):
        self.node_id = node_id
        self.counts = {}
    
    def increment(self, amount=1):
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + amount
    
    def value(self):
        return sum(self.counts.values())
    
    def merge(self, other):
        for node, count in other.counts.items():
            self.counts[node] = max(self.counts.get(node, 0), count)

class LWWRegister:
    def __init__(self):
        self.value = None
        self.timestamp = -1
    
    def set(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        if timestamp > self.timestamp:
            self.value = value
            self.timestamp = timestamp
    
    def get(self):
        return self.value
    
    def merge(self, other):
        if other.timestamp > self.timestamp:
            self.value = other.value
            self.timestamp = other.timestamp
```

---

## 4. MICROSERVICES

### 4.1 Service Registry + Circuit Breaker
```python
import time

class ServiceRegistry:
    def __init__(self):
        self.services = {}
    
    def register(self, service_name, instance_id, host, port):
        if service_name not in self.services:
            self.services[service_name] = []
        instance = {
            'id': instance_id,
            'host': host,
            'port': port,
            'health': 'healthy',
            'last_heartbeat': time.time()
        }
        for i, inst in enumerate(self.services[service_name]):
            if inst['id'] == instance_id:
                self.services[service_name][i] = instance
                return
        self.services[service_name].append(instance)
    
    def discover(self, service_name):
        return self.services.get(service_name, [])

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.state = 'closed'
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half_open'
            else:
                raise Exception("Circuit breaker is OPEN")
        try:
            result = func(*args, **kwargs)
            self.failure_count = 0
            if self.state == 'half_open':
                self.state = 'closed'
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
            raise e
```

### 4.2 API Gateway + Rate Limiter
```python
from dataclasses import dataclass
import time

@dataclass
class Request:
    method: str
    path: str
    headers: dict

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id):
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id] = [
            t for t in self.requests[client_id] 
            if now - t < self.window
        ]
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False
```

---

## 5. DISTRIBUTED TRANSACTIONS

### 5.1 Saga Pattern
```python
class Event:
    def __init__(self, type, data):
        self.type = type
        self.data = data

class EventBus:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                handler(event)

class OrderService:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.orders = {}
    
    def create_order(self, order_id, items):
        order = {'id': order_id, 'items': items, 'status': 'PENDING'}
        self.orders[order_id] = order
        self.event_bus.publish(Event('ORDER_CREATED', order))
```

---

## 6. MESSAGE QUEUES

### 6.1 Kafka-style Producer/Consumer
```python
from dataclasses import dataclass
import time

@dataclass
class Message:
    key: str
    value: bytes
    partition: int
    offset: int

class KafkaPartition:
    def __init__(self, partition_id):
        self.partition_id = partition_id
        self.messages = []
        self.offsets = {}
    
    def append(self, message):
        self.messages.append(message)
        return len(self.messages) - 1
    
    def read(self, offset, max_messages):
        return self.messages[offset:offset + max_messages]

class KafkaTopic:
    def __init__(self, name, num_partitions=3):
        self.name = name
        self.partitions = [KafkaPartition(i) for i in range(num_partitions)]
    
    def produce(self, key, value):
        h = hash(key) if key else 0
        partition = self.partitions[h % len(self.partitions)]
        offset = partition.append(Message(
            key=key, value=value,
            partition=partition.partition_id,
            offset=len(partition.messages)
        ))
        return partition.messages[-1]
```

---

## 7. SCALING PATTERNS

### 7.1 Sharding Strategies
```python
class HashSharder:
    def __init__(self, num_shards):
        self.num_shards = num_shards
    
    def get_shard(self, key):
        return hash(key) % self.num_shards

class RangeSharder:
    def __init__(self, ranges):
        self.ranges = sorted(ranges, key=lambda x: x[0])
    
    def get_shard(self, key):
        for min_val, max_val, shard_id in self.ranges:
            if min_val <= key <= max_val:
                return shard_id
        raise ValueError(f"Key {key} not in any range")
```

---

## 8. OBSERVABILITY

### 8.1 Distributed Tracing
```python
from dataclasses import dataclass, field
from typing import Optional, List
import time
import uuid

@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: dict = field(default_factory=dict)
    
    def finish(self):
        self.end_time = time.time()
    
    def duration_ms(self.end_time:
            return (self.end):
        if self_time - self.start_time) * 1000
        return 0

class Tracer:
    def __init__(self, service_name):
        self.service_name = service_name
        self.spans = []
    
    def start_span(self, operation_name, trace_id=None, parent_id=None):
        if trace_id is None:
            trace_id = uuid.uuid4().hex
        span = Span(
            trace_id=trace_id,
            span_id=uuid.uuid4().hex[:16],
            parent_id=parent_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=time.time()
        )
        self.spans.append(span)
        return span
    
    def inject_context(self, span):
        return {
            'X-Trace-ID': span.trace_id,
            'X-Span-ID': span.span_id
        }
```

*End of System Design Masterclass*
