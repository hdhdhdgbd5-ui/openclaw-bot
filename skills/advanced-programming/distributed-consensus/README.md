# 🌐 Distributed Consensus & Byzantine Fault Tolerance

**Build resilient, trustless systems that can survive failures and attacks**

## What You Can Build

| Application | Description | Income Potential |
|-------------|-------------|------------------|
| **Blockchains** | L1/L2 networks | Protocol value |
| **Distributed Databases** | NoSQL, NewSQL | $50K-500K/project |
| **Leader Election** | Fault-tolerant coordination | $20K-100K |
| **State Machine Replication** | Consistent state across nodes | $30K-200K |
| **Cross-Chain Bridges** | Interoperability | $50K-300K |
| **Oracles** | External data feeds | $30K-150K |

---

## 📚 Learning Path

### Week 1: Fundamentals
1. CAP theorem
2. State machine replication
3. Consensus vs agreement
4. Failure models (crash, Byzantine)

### Week 2: Classic Protocols
1. Paxos
2. Raft
3. Viewstamped Replication
4. Practical Byzantine Fault Tolerance (PBFT)

### Week 3: Modern Consensus
1. Tendermint/Cosmos
2. HotStuff (Diem)
3. DAG-based consensus
4. Proof-based systems

### Week 4: Advanced Topics
1. Sharding
2. Randomness beacons
3. Light clients
4. Finality gadgets

---

## 🏗️ Raft Implementation

### Core Raft Algorithm
```go
package raft

import (
    "sync"
    "time"
    "math/rand"
)

type Role string

const (
    RoleFollower  Role = "follower"
    RoleCandidate Role = "candidate"
    RoleLeader    Role = "leader"
)

type LogEntry struct {
    Term    int
    Index   int
    Command interface{}
}

type Raft struct {
    mu sync.RWMutex
    
    // Persistent state
    currentTerm int
    votedFor    int
    log         []LogEntry
    
    // Volatile state
    role        Role
    commitIndex int
    lastApplied int
    
    // Leader state
    nextIndex   []int
    matchIndex  []int
    
    // Configuration
    nodeID      int
    peers       []int
    
    // Channels
    voteCh      chan bool
    appendCh    chan []LogEntry
    commitCh    chan []LogEntry
    
    // Timeouts
    electionTimeout time.Duration
    heartbeatTimeout time.Duration
}

func NewRaft(nodeID int, peers []int) *Raft {
    rf := &Raft{
        nodeID:      nodeID,
        peers:       peers,
        role:        RoleFollower,
        currentTerm: 0,
        votedFor:    -1,
        log:         []LogEntry{{Term: 0, Index: 0}},
        
        electionTimeout:  time.Duration(150+rand.Intn(150)) * time.Millisecond,
        heartbeatTimeout: 50 * time.Millisecond,
        
        voteCh:   make(chan bool),
        appendCh: make(chan []LogEntry),
        commitCh: make(chan []LogEntry),
    }
    
    return rf
}

// ====== Election ======

func (rf *Raft) StartElection() {
    rf.mu.Lock()
    defer rf.mu.Unlock()
    
    rf.role = RoleCandidate
    rf.currentTerm++
    rf.votedFor = rf.nodeID
    
    // Request votes from all peers
    voteCount := 1 // Vote for self
    
    for _, peer := range rf.peers {
        go rf.sendRequestVote(peer, &voteCount)
    }
    
    // Reset election timer
    rf.resetElectionTimer()
}

func (rf *Raft) sendRequestVote(peer int, voteCount *int) {
    lastLogIndex := len(rf.log) - 1
    lastLogTerm := rf.log[lastLogIndex].Term
    
    args := RequestVoteArgs{
        Term:         rf.currentTerm,
        CandidateID:  rf.nodeID,
        LastLogIndex: lastLogIndex,
        LastLogTerm:  lastLogTerm,
    }
    
    reply := new(RequestVoteReply)
    
    if rf.sendRPC(peer, "RequestVote", args, reply) {
        rf.mu.Lock()
        defer rf.mu.Unlock()
        
        if reply.Term > rf.currentTerm {
            rf.currentTerm = reply.Term
            rf.role = RoleFollower
            rf.votedFor = -1
            return
        }
        
        if reply.VoteGranted {
            *voteCount++
            
            // Majority achieved
            if *voteCount > len(rf.peers)/2 {
                rf.becomeLeader()
            }
        }
    }
}

func (rf *Raft) becomeLeader() {
    rf.role = RoleLeader
    
    // Initialize leader state
    n := len(rf.peers) + 1 // Including self
    rf.nextIndex = make([]int, n)
    rf.matchIndex = make([]int, n)
    
    for i := range rf.nextIndex {
        rf.nextIndex[i] = len(rf.log)
    }
    
    // Start sending heartbeats
    go rf.replicateLogs()
}

// ====== Log Replication ======

func (rf *Raft) replicateLogs() {
    for rf.role == RoleLeader {
        for _, peer := range rf.peers {
            go rf.replicateToPeer(peer)
        }
        time.Sleep(rf.heartbeatTimeout)
    }
}

func (rf *Raft) replicateToPeer(peer int) {
    rf.mu.RLock()
    
    prevLogIndex := rf.nextIndex[peer] - 1
    prevLogTerm := rf.log[prevLogIndex].Term
    
    entries := rf.log[rf.nextIndex[peer]:]
    
    args := AppendEntriesArgs{
        Term:         rf.currentTerm,
        LeaderID:     rf.nodeID,
        PrevLogIndex: prevLogIndex,
        PrevLogTerm:  prevLogTerm,
        Entries:      entries,
        LeaderCommit: rf.commitIndex,
    }
    
    rf.mu.RUnlock()
    
    reply := new(AppendEntriesReply)
    
    if rf.sendRPC(peer, "AppendEntries", args, reply) {
        rf.mu.Lock()
        defer rf.mu.Unlock()
        
        if reply.Success {
            rf.nextIndex[peer] = len(rf.log)
            rf.matchIndex[peer] = len(rf.log) - 1
            
            rf.updateCommitIndex()
        } else {
            // Decrement nextIndex and retry
            rf.nextIndex[peer]--
        }
    }
}

func (rf *Raft) updateCommitIndex() {
    // Commit entries that are replicated on majority
    for n := len(rf.log) - 1; n > rf.commitIndex; n-- {
        count := 1 // Self
        
        for _, peer := range rf.peers {
            if rf.matchIndex[peer] >= n {
                count++
            }
        }
        
        if count > len(rf.peers)/2 && rf.log[n].Term == rf.currentTerm {
            rf.commitIndex = n
            break
        }
    }
}
```

### Paxos Implementation
```python
"""
Simplified Paxos implementation
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, List, Dict
import time
import random

@dataclass
class Proposal:
    proposal_id: int
    value: Optional[any]
    acceptor: int

class PaxosNode:
    """
    Single Paxos node implementation
    """
    
    def __init__(self, node_id: int, peers: List[int]):
        self.node_id = node_id
        self.peers = peers
        
        # State
        self.promised_id: Optional[int] = None
        self.accepted_proposal: Optional[Proposal] = None
        self.proposals: Dict[int, Proposal] = {}  # proposal_id -> proposal
        
        # Current proposal
        self.current_proposal_id: int = node_id * 1000
        self.proposal_value: Optional[any] = None
        
    async def prepare(self, proposal_id: int, from_node: int) -> bool:
        """
        Phase 1a: Acceptor receives PREPARE
        """
        if proposal_id > self.promised_id:
            self.promised_id = proposal_id
            
            # Send promise with accepted proposal (if any)
            accepted = self.accepted_proposal
            return True
        
        return False
    
    async def accept(self, proposal: Proposal) -> bool:
        """
        Phase 2a: Acceptor's ACCEPT request
        """
        if proposal.proposal_id >= self.promised_id:
            self.promised_id = proposal.proposal_id
            self.accepted_proposal = proposal
            
            # Broadcast accepted proposal to all nodes
            for peer in self.peers:
                await self.send_accept(peer, proposal)
            
            return True
        
        return False
    
    async def send_accept(self, peer: int, proposal: Proposal):
        """Send accept request to peer"""
        pass  # Network implementation
    
    async def propose(self, value: any) -> Optional[any]:
        """
        Main entry point: propose a value
        """
        self.proposal_value = value
        
        # Phase 1: Prepare
        proposal_id = self.current_proposal_id
        self.current_proposal_id += len(self.peers)
        
        # Get promises from majority
        promises = []
        
        for peer in self.peers:
            # In practice: network call
            promised = True  # Simplified
            if promised:
                promises.append(peer)
        
        # Need majority
        if len(promises) <= len(self.peers) // 2:
            return None  # Failed
        
        # Phase 2: Accept
        proposal = Proposal(proposal_id, value, self.node_id)
        
        accepts = []
        for peer in self.peers:
            accepted = True  # Simplified
            if accepted:
                accepts.append(peer)
        
        # Need majority
        if len(accepts) > len(self.peers) // 2:
            return value  # Consensus reached!
        
        return None


class MultiPaxos:
    """
    Multi-Paxos for continuous consensus (like Raft)
    """
    
    def __init__(self, nodes: List[PaxosNode]):
        self.nodes = nodes
        self.leader: Optional[int] = None
        self.sequence_num = 0
    
    async def become_leader(self):
        """
        Leader election using Paxos
        """
        # Simplified: first node to complete prepare becomes leader
        for node in self.nodes:
            success = await node.propose("LEADER_CHOICE")
            if success:
                self.leader = node.node_id
                break
    
    async def replicate(self, value: any) -> Optional[any]:
        """
        Replicate value through Paxos
        """
        if self.leader is None:
            return None
        
        leader_node = self.nodes[self.leader]
        
        # Propose through leader
        return await leader_node.propose(value)
```

---

## ⚔️ Byzantine Fault Tolerance

### PBFT (Practical Byzantine Fault Tolerance)
```python
"""
PBFT Implementation
Tolerates f Byzantine faults with 3f+1 nodes
"""

import asyncio
from dataclasses import dataclass
from typing import Dict, Set, List
import hashlib
import time

@dataclass
class Request:
    client_id: int
    timestamp: int
    operation: str
    
@dataclass
class PrePrepare:
    view: int
    sequence: int
    digest: str
    request: Request

@dataclass
class Prepare:
    view: int
    sequence: int
    digest: str
    node_id: int

@dataclass
class Commit:
    view: int
    sequence: int
    digest: str
    node_id: int

class PBFTNode:
    """
    PBFT replica node
    """
    
    def __init__(self, node_id: int, peers: List[int], f: int):
        self.node_id = node_id
        self.peers = peers
        self.f = f  # Number of Byzantine faults tolerated
        
        # State
        self.view = 0           # Current view (leader term)
        self.sequence = 0       # Sequence number
        self.primary = 0        # Current primary
        
        # Message logs
        self.pre_prepares: Dict[int, PrePrepare] = {}
        self.prepares: Dict[int, List[Prepare]] = {}
        self.commits: Dict[int, List[Commit]] = {}
        
        # Executed requests
        self.executed: Dict[int, any] = {}
        
        # Client state
        self.client_replies: Dict[int, any] = {}
        
    def is_primary(self) -> bool:
        """Check if this node is primary"""
        return self.node_id == self.peers[self.view % len(self.peers)]
    
    async def receive_request(self, request: Request):
        """Client sends request"""
        if not self.is_primary():
            # Forward to primary
            await self.forward_to_primary(request)
            return
        
        # Primary receives request
        await self.pre_prepare(request)
    
    async def pre_prepare(self, request: Request):
        """
        Phase 1: Primary sends PRE-PREPARE
        """
        # Create digest
        digest = hashlib.sha256(
            f"{request.operation}{request.timestamp}".encode()
        ).hexdigest()
        
        # Create pre-prepare message
        pre_prepare = PrePrepare(
            view=self.view,
            sequence=self.sequence,
            digest=digest,
            request=request
        )
        
        self.pre_prepares[self.sequence] = pre_prepare
        self.prepares[self.sequence] = []
        
        # Broadcast to all backups
        for peer in self.peers:
            if peer != self.node_id:
                await self.send_prepare(peer, pre_prepare)
        
        # Self also enters prepare phase
        await self.prepare(pre_prepare)
    
    async def send_prepare(self, peer: int, pre_prepare: PrePrepare):
        """Send PREPARE to peer"""
        prepare = Prepare(
            view=pre_prepare.view,
            sequence=pre_prepare.sequence,
            digest=pre_prepare.digest,
            node_id=self.node_id
        )
        
        # In practice: network call
        await self.receive_prepare(prepare)
    
    async def receive_prepare(self, prepare: Prepare):
        """
        Phase 2: Receive and validate PREPARE
        """
        # Verify view
        if prepare.view != self.view:
            return
        
        # Verify sequence is in watermark
        # (simplified)
        
        # Verify digest matches
        if self.pre_prepares.get(prepare.sequence):
            expected_digest = self.pre_prepares[prepare.sequence].digest
            if prepare.digest != expected_digest:
                return
        
        # Add to prepares
        if prepare.sequence not in self.prepares:
            self.prepares[prepare.sequence] = []
        
        self.prepares[prepare.sequence].append(prepare)
        
        # Check if we have enough prepares (2f)
        if len(self.prepares[prepare.sequence]) >= 2 * self.f:
            await self.commit(prepare.sequence, prepare.digest)
    
    async def commit(self, sequence: int, digest: str):
        """
        Phase 3: Send COMMIT
        """
        if sequence not in self.commits:
            self.commits[sequence] = []
        
        commit = Commit(
            view=self.view,
            sequence=sequence,
            digest=digest,
            node_id=self.node_id
        )
        
        self.commits[sequence].append(commit)
        
        # Broadcast commit
        for peer in self.peers:
            if peer != self.node_id:
                await self.send_commit(peer, commit)
        
        # Check if can execute
        await self.execute(sequence)
    
    async def send_commit(self, peer: int, commit: Commit):
        """Send COMMIT to peer"""
        await self.receive_commit(commit)
    
    async def receive_commit(self, commit: Commit):
        """Receive COMMIT"""
        if commit.view != self.view:
            return
        
        if commit.sequence not in self.commits:
            self.commits[commit.sequence] = []
        
        self.commits[commit.sequence].append(commit)
        
        # Check for 2f+1 commits (including self)
        if len(self.commits[commit.sequence]) >= 2 * self.f + 1:
            await self.execute(commit.sequence)
    
    async def execute(self, sequence: int):
        """
        Execute request (deterministic)
        """
        if sequence in self.executed:
            return
        
        if sequence not in self.pre_prepares:
            return
        
        request = self.pre_prepares[sequence].request
        
        # Execute operation (deterministic)
        result = await self.execute_operation(request.operation)
        
        # Store result
        self.executed[sequence] = result
        
        # Send reply to client
        await self.send_reply(request.client_id, result)
    
    async def execute_operation(self, operation: str) -> any:
        """Execute the actual operation"""
        # Simplified: just return operation result
        return f"executed: {operation}"
    
    async def send_reply(self, client_id: int, result: any):
        """Send reply to client"""
        self.client_replies[client_id] = result
```

---

## 🌟 Tendermint Consensus

```go
package tendermint

import (
    "crypto/sha256"
    "sync"
    "time"
)

type Block struct {
    Header    Header
    Data      [][]byte
    Evidence  []Evidence
}

type Header struct {
    Height    int64
    Time      time.Time
    LastBlock []byte
    ValidatorsHash []byte
    AppHash   []byte
}

type Vote struct {
    Type             VoteType
    Height           int64
    Round            int
    BlockID          BlockID
    ValidatorAddress []byte
    Timestamp        time.Time
    Signature        []byte
}

// Tendermint consensus states
const (
    NewRound      = iota
    Propose       // Propose block
    Prevote       // Vote for block
    Precommit     // Commit to block
)

type ConsensusState struct {
    Height    int64
    Round     int
    Step      int
    
    Validators []Validator
    Proposer   int
    
    Block      *Block
    Votes      map[VoteType][]*Vote
    
    mu         sync.RWMutex
}

// Propose block
func (cs *ConsensusState) propose() {
    if !cs.isProposer() {
        return
    }
    
    // Create block proposal
    block := cs.createBlock()
    
    // Broadcast proposal
    cs.broadcast(ProposalMessage{block})
}

// Prevote
func (cs *ConsensusState) prevote() {
    // Vote for block if we have it and it's valid
    // Otherwise vote nil
    
    vote := &Vote{
        Type:       TypePrevote,
        Height:     cs.Height,
        Round:      cs.Round,
        BlockID:    cs.Block.id(),
        Signature:  cs.signVote(),
    }
    
    cs.broadcast(vote)
}

// Precommit  
func (cs *ConsensusState) precommit() {
    // Precommit if we have 2/3+ prevotes for block
    
    vote := &Vote{
        Type:       TypePrecommit,
        Height:     cs.Height,
        Round:      cs.Round,
        BlockID:    cs.Block.id(),
        Signature:  cs.signVote(),
    }
    
    cs.broadcast(vote)
}

// Check for consensus
func (cs *ConsensusState) checkConsensus() {
    // Check if we have 2/3+ votes for any block
    
    prevotes := cs.getVotes(Prevote)
    if hasTwoThirds(prevotes) {
        cs.bLock()
    }
}
```

---

## 🛠️ Tools & Resources

| Tool | Language | Use |
|------|----------|-----|
| **Raft** | Go | Etcd, TiKV |
| **Tendermint** | Go | Cosmos |
| **HotStuff** | Go, Rust | Diem |
| **Casper** | Rust | Ethereum |
| **LibP2P** | Go, Rust | P2P networking |

---

## 📖 Exercises

### Exercise 1: Simple Paxos
Implement basic Paxos:
- Prepare/Accept phases
- Majority checking
- Value learning

### Exercise 2: Raft from Scratch
Build complete Raft:
- Leader election
- Log replication
- Membership changes

### Exercise 3: Byzantine Voting
Build BFT system:
- PBFT message types
- View changes
- Checkpointing

---

## 🎯 Next Steps

1. ✅ Read Raft paper
2. 📚 Study Tendermint/Cosmos SDK
3. 🔒 Understand attack vectors
4. 📖 Read "Distributed Systems" (van Steen)
5. 🏆 Build a blockchain!

**Consensus is hard - now do it in the presence of attackers! ⚔️**
