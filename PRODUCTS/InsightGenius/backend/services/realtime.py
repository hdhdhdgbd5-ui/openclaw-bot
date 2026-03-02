"""
Real-time Service
WebSocket management and real-time data streaming
"""

import asyncio
from typing import Dict, List, Set
from datetime import datetime
from fastapi import WebSocket

from core.logging import logger

class RealTimeManager:
    """Manages WebSocket connections and real-time data streaming"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[int, Set[WebSocket]] = {}  # dataset_id -> connections
        self.streaming_datasets: Set[int] = set()
        self.active_alerts: List[Dict] = []
        self._running = False
    
    async def start(self):
        """Start real-time services"""
        self._running = True
        logger.info("Real-time manager started")
    
    async def stop(self):
        """Stop real-time services"""
        self._running = False
        # Close all connections
        for ws in list(self.active_connections):
            await ws.close()
        logger.info("Real-time manager stopped")
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to InsightGenius real-time updates"
        })
    
    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for dataset_id, connections in self.subscriptions.items():
            connections.discard(websocket)
        
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def handle_message(self, websocket: WebSocket, data: Dict):
        """Handle incoming WebSocket message"""
        msg_type = data.get("type")
        
        if msg_type == "subscribe":
            dataset_id = data.get("dataset_id")
            if dataset_id:
                await self._subscribe(websocket, dataset_id)
        
        elif msg_type == "unsubscribe":
            dataset_id = data.get("dataset_id")
            if dataset_id:
                await self._unsubscribe(websocket, dataset_id)
        
        elif msg_type == "ping":
            await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
    
    async def _subscribe(self, websocket: WebSocket, dataset_id: int):
        """Subscribe connection to dataset updates"""
        if dataset_id not in self.subscriptions:
            self.subscriptions[dataset_id] = set()
        self.subscriptions[dataset_id].add(websocket)
        
        await websocket.send_json({
            "type": "subscribed",
            "dataset_id": dataset_id,
            "message": f"Subscribed to dataset {dataset_id}"
        })
    
    async def _unsubscribe(self, websocket: WebSocket, dataset_id: int):
        """Unsubscribe connection from dataset updates"""
        if dataset_id in self.subscriptions:
            self.subscriptions[dataset_id].discard(websocket)
        
        await websocket.send_json({
            "type": "unsubscribed",
            "dataset_id": dataset_id
        })
    
    async def broadcast_to_dataset(self, dataset_id: int, message: Dict):
        """Broadcast message to all subscribers of a dataset"""
        if dataset_id not in self.subscriptions:
            return
        
        disconnected = set()
        for ws in self.subscriptions[dataset_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws)
    
    async def broadcast_alert(self, alert: Dict):
        """Broadcast alert to all connected clients"""
        message = {
            "type": "alert",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = set()
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.add(ws)
        
        for ws in disconnected:
            await self.disconnect(ws)
    
    async def test_alert(self, alert_config: Dict, user_id: int):
        """Send test alert"""
        test_alert = {
            "id": "test",
            "title": "Test Alert",
            "message": "This is a test alert from InsightGenius",
            "severity": "info",
            "config": alert_config,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_alert(test_alert)
