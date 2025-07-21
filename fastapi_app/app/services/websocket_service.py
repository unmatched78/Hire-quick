"""
WebSocket Service

Real-time communication service for notifications, chat, and live updates.
"""

import json
import asyncio
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    NOTIFICATION = "notification"
    CHAT_MESSAGE = "chat_message"
    APPLICATION_UPDATE = "application_update"
    JOB_UPDATE = "job_update"
    INTERVIEW_REMINDER = "interview_reminder"
    SYSTEM_MESSAGE = "system_message"
    TYPING_INDICATOR = "typing_indicator"
    USER_STATUS = "user_status"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store user metadata
        self.user_metadata: Dict[int, Dict[str, Any]] = {}
        # Store room memberships (for chat rooms, company channels, etc.)
        self.rooms: Dict[str, Set[int]] = {}
        # Store typing indicators
        self.typing_users: Dict[str, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, user_data: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        
        # Store user metadata
        if user_data:
            self.user_metadata[user_id] = user_data
        
        logger.info(f"User {user_id} connected via WebSocket")
        
        # Send welcome message
        await self.send_personal_message({
            "type": MessageType.SYSTEM_MESSAGE,
            "message": "Connected to Hire Quick real-time service",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        }, user_id)
        
        # Notify others about user status
        await self.broadcast_user_status(user_id, "online")

    async def disconnect(self, websocket: WebSocket, user_id: int):
        """Handle WebSocket disconnection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_metadata:
                    del self.user_metadata[user_id]
                
                # Remove from all rooms
                for room_id in list(self.rooms.keys()):
                    self.rooms[room_id].discard(user_id)
                    if not self.rooms[room_id]:
                        del self.rooms[room_id]
                
                # Notify others about user status
                await self.broadcast_user_status(user_id, "offline")
        
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            message_json = json.dumps(message)
            disconnected_sockets = set()
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected_sockets.add(websocket)
            
            # Clean up disconnected sockets
            for websocket in disconnected_sockets:
                await self.disconnect(websocket, user_id)

    async def send_to_room(self, message: Dict[str, Any], room_id: str):
        """Send message to all users in a room"""
        if room_id in self.rooms:
            for user_id in self.rooms[room_id]:
                await self.send_personal_message(message, user_id)

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

    async def join_room(self, user_id: int, room_id: str):
        """Add user to a room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        
        self.rooms[room_id].add(user_id)
        
        # Notify room about new member
        await self.send_to_room({
            "type": MessageType.SYSTEM_MESSAGE,
            "message": f"User {user_id} joined the room",
            "room_id": room_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, room_id)

    async def leave_room(self, user_id: int, room_id: str):
        """Remove user from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(user_id)
            
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            else:
                # Notify room about member leaving
                await self.send_to_room({
                    "type": MessageType.SYSTEM_MESSAGE,
                    "message": f"User {user_id} left the room",
                    "room_id": room_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }, room_id)

    async def broadcast_user_status(self, user_id: int, status: str):
        """Broadcast user status change"""
        user_data = self.user_metadata.get(user_id, {})
        
        message = {
            "type": MessageType.USER_STATUS,
            "user_id": user_id,
            "status": status,
            "user_name": user_data.get("name", f"User {user_id}"),
            "user_type": user_data.get("user_type", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connected users (could be optimized to send only to relevant users)
        await self.broadcast_to_all(message)

    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users"""
        online_users = []
        for user_id, connections in self.active_connections.items():
            if connections:  # User has active connections
                user_data = self.user_metadata.get(user_id, {})
                online_users.append({
                    "user_id": user_id,
                    "name": user_data.get("name", f"User {user_id}"),
                    "user_type": user_data.get("user_type", "unknown"),
                    "connection_count": len(connections),
                    "last_seen": datetime.utcnow().isoformat()
                })
        
        return online_users

    def get_room_users(self, room_id: str) -> List[int]:
        """Get users in a specific room"""
        return list(self.rooms.get(room_id, set()))


class WebSocketService:
    """WebSocket service for real-time features"""
    
    def __init__(self):
        self.manager = ConnectionManager()

    async def send_notification(
        self, 
        user_id: int, 
        title: str, 
        message: str, 
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Dict[str, Any] = None
    ):
        """Send a notification to a user"""
        notification = {
            "type": MessageType.NOTIFICATION,
            "title": title,
            "message": message,
            "priority": priority.value,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "id": f"notif_{user_id}_{int(datetime.utcnow().timestamp())}"
        }
        
        await self.manager.send_personal_message(notification, user_id)
        logger.info(f"Notification sent to user {user_id}: {title}")

    async def send_application_update(
        self, 
        candidate_id: int, 
        application_id: int, 
        status: str, 
        message: str = None
    ):
        """Send application status update"""
        update = {
            "type": MessageType.APPLICATION_UPDATE,
            "application_id": application_id,
            "status": status,
            "message": message or f"Your application status has been updated to: {status}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.send_personal_message(update, candidate_id)
        logger.info(f"Application update sent to candidate {candidate_id}: {status}")

    async def send_job_update(
        self, 
        job_id: int, 
        update_type: str, 
        message: str,
        affected_users: List[int] = None
    ):
        """Send job-related updates"""
        update = {
            "type": MessageType.JOB_UPDATE,
            "job_id": job_id,
            "update_type": update_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if affected_users:
            for user_id in affected_users:
                await self.manager.send_personal_message(update, user_id)
        else:
            await self.manager.broadcast_to_all(update)
        
        logger.info(f"Job update sent for job {job_id}: {update_type}")

    async def send_interview_reminder(
        self, 
        user_id: int, 
        interview_data: Dict[str, Any],
        reminder_time: str
    ):
        """Send interview reminder"""
        reminder = {
            "type": MessageType.INTERVIEW_REMINDER,
            "interview_data": interview_data,
            "reminder_time": reminder_time,
            "message": f"Interview reminder: {interview_data.get('job_title', 'Interview')} in {reminder_time}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.send_personal_message(reminder, user_id)
        logger.info(f"Interview reminder sent to user {user_id}")

    async def send_chat_message(
        self, 
        from_user_id: int, 
        to_user_id: int, 
        message: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None
    ):
        """Send chat message between users"""
        chat_message = {
            "type": MessageType.CHAT_MESSAGE,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "message": message,
            "message_type": message_type,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "id": f"msg_{from_user_id}_{to_user_id}_{int(datetime.utcnow().timestamp())}"
        }
        
        # Send to both sender and recipient
        await self.manager.send_personal_message(chat_message, from_user_id)
        await self.manager.send_personal_message(chat_message, to_user_id)
        
        logger.info(f"Chat message sent from {from_user_id} to {to_user_id}")

    async def broadcast_system_message(self, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM):
        """Broadcast system-wide message"""
        system_message = {
            "type": MessageType.SYSTEM_MESSAGE,
            "message": message,
            "priority": priority.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_all(system_message)
        logger.info(f"System message broadcasted: {message}")

    async def handle_typing_indicator(self, user_id: int, room_id: str, is_typing: bool):
        """Handle typing indicators"""
        if room_id not in self.manager.typing_users:
            self.manager.typing_users[room_id] = set()
        
        if is_typing:
            self.manager.typing_users[room_id].add(user_id)
        else:
            self.manager.typing_users[room_id].discard(user_id)
        
        # Broadcast typing indicator to room
        typing_message = {
            "type": MessageType.TYPING_INDICATOR,
            "room_id": room_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "typing_users": list(self.manager.typing_users[room_id]),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.send_to_room(typing_message, room_id)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in self.manager.active_connections.values())
        
        return {
            "total_users": len(self.manager.active_connections),
            "total_connections": total_connections,
            "active_rooms": len(self.manager.rooms),
            "online_users": self.manager.get_online_users(),
            "rooms": {room_id: len(users) for room_id, users in self.manager.rooms.items()},
            "timestamp": datetime.utcnow().isoformat()
        }


# Global WebSocket service instance
websocket_service = WebSocketService()