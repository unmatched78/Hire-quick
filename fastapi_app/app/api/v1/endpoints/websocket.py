"""
WebSocket API Endpoints

Real-time communication endpoints for notifications, chat, and live updates.
"""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.security import HTTPBearer

from ....core.security import get_current_user_websocket, get_current_user
from ....services.websocket_service import websocket_service, MessageType, NotificationPriority
from ....models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time communication
    
    Args:
        websocket: WebSocket connection
        user_id: User ID for the connection
        token: Optional JWT token for authentication
    """
    try:
        # Authenticate user (simplified for WebSocket)
        if token:
            try:
                # In a real implementation, you'd validate the JWT token here
                user_data = {
                    "user_id": user_id,
                    "name": f"User {user_id}",
                    "user_type": "candidate"  # This would come from token validation
                }
            except Exception as e:
                await websocket.close(code=4001, reason="Authentication failed")
                return
        else:
            user_data = {"user_id": user_id, "name": f"User {user_id}", "user_type": "guest"}
        
        # Accept connection
        await websocket_service.manager.connect(websocket, user_id, user_data)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(websocket, user_id, message)
                
        except WebSocketDisconnect:
            await websocket_service.manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            await websocket_service.manager.disconnect(websocket, user_id)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        await websocket.close(code=4000, reason="Connection error")


async def handle_websocket_message(websocket: WebSocket, user_id: int, message: Dict[str, Any]):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    try:
        if message_type == "ping":
            # Respond to ping with pong
            await websocket.send_text(json.dumps({
                "type": "pong",
                "timestamp": message.get("timestamp")
            }))
            
        elif message_type == "join_room":
            room_id = message.get("room_id")
            if room_id:
                await websocket_service.manager.join_room(user_id, room_id)
                
        elif message_type == "leave_room":
            room_id = message.get("room_id")
            if room_id:
                await websocket_service.manager.leave_room(user_id, room_id)
                
        elif message_type == "chat_message":
            to_user_id = message.get("to_user_id")
            text = message.get("message")
            if to_user_id and text:
                await websocket_service.send_chat_message(
                    from_user_id=user_id,
                    to_user_id=to_user_id,
                    message=text,
                    message_type=message.get("message_type", "text"),
                    metadata=message.get("metadata", {})
                )
                
        elif message_type == "typing_indicator":
            room_id = message.get("room_id")
            is_typing = message.get("is_typing", False)
            if room_id:
                await websocket_service.handle_typing_indicator(user_id, room_id, is_typing)
                
        elif message_type == "get_online_users":
            online_users = websocket_service.manager.get_online_users()
            await websocket.send_text(json.dumps({
                "type": "online_users",
                "users": online_users
            }))
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Failed to process message",
            "error": str(e)
        }))


@router.post("/notifications/send")
async def send_notification(
    user_id: int,
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send a notification to a specific user
    
    Args:
        user_id: Target user ID
        title: Notification title
        message: Notification message
        priority: Notification priority level
        data: Additional notification data
        current_user: Current authenticated user
    """
    try:
        await websocket_service.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            priority=priority,
            data=data or {}
        )
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "target_user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")


@router.post("/notifications/broadcast")
async def broadcast_system_message(
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    current_user: User = Depends(get_current_user)
):
    """
    Broadcast a system message to all connected users
    
    Args:
        message: System message to broadcast
        priority: Message priority level
        current_user: Current authenticated user (must be admin)
    """
    # Check if user has admin privileges
    if current_user.user_type != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        await websocket_service.broadcast_system_message(message, priority)
        
        return {
            "success": True,
            "message": "System message broadcasted successfully",
            "broadcast_message": message
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting system message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")


@router.post("/applications/{application_id}/notify-update")
async def notify_application_update(
    application_id: int,
    candidate_id: int,
    status: str,
    message: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send application status update notification
    
    Args:
        application_id: Application ID
        candidate_id: Candidate user ID
        status: New application status
        message: Optional custom message
        current_user: Current authenticated user
    """
    try:
        await websocket_service.send_application_update(
            candidate_id=candidate_id,
            application_id=application_id,
            status=status,
            message=message
        )
        
        return {
            "success": True,
            "message": "Application update notification sent",
            "application_id": application_id,
            "candidate_id": candidate_id,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error sending application update: {e}")
        raise HTTPException(status_code=500, detail="Failed to send application update")


@router.post("/jobs/{job_id}/notify-update")
async def notify_job_update(
    job_id: int,
    update_type: str,
    message: str,
    affected_users: Optional[list[int]] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send job update notification
    
    Args:
        job_id: Job ID
        update_type: Type of update (e.g., 'status_change', 'deadline_extended')
        message: Update message
        affected_users: Optional list of specific users to notify
        current_user: Current authenticated user
    """
    try:
        await websocket_service.send_job_update(
            job_id=job_id,
            update_type=update_type,
            message=message,
            affected_users=affected_users
        )
        
        return {
            "success": True,
            "message": "Job update notification sent",
            "job_id": job_id,
            "update_type": update_type,
            "affected_users": len(affected_users) if affected_users else "all"
        }
        
    except Exception as e:
        logger.error(f"Error sending job update: {e}")
        raise HTTPException(status_code=500, detail="Failed to send job update")


@router.post("/interviews/remind")
async def send_interview_reminder(
    user_id: int,
    interview_data: Dict[str, Any],
    reminder_time: str,
    current_user: User = Depends(get_current_user)
):
    """
    Send interview reminder notification
    
    Args:
        user_id: User ID to remind
        interview_data: Interview details
        reminder_time: When the reminder is for (e.g., "30 minutes")
        current_user: Current authenticated user
    """
    try:
        await websocket_service.send_interview_reminder(
            user_id=user_id,
            interview_data=interview_data,
            reminder_time=reminder_time
        )
        
        return {
            "success": True,
            "message": "Interview reminder sent",
            "user_id": user_id,
            "reminder_time": reminder_time
        }
        
    except Exception as e:
        logger.error(f"Error sending interview reminder: {e}")
        raise HTTPException(status_code=500, detail="Failed to send interview reminder")


@router.get("/stats")
async def get_websocket_stats(current_user: User = Depends(get_current_user)):
    """
    Get WebSocket connection statistics
    
    Args:
        current_user: Current authenticated user
    """
    try:
        stats = websocket_service.get_connection_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/online-users")
async def get_online_users(current_user: User = Depends(get_current_user)):
    """
    Get list of currently online users
    
    Args:
        current_user: Current authenticated user
    """
    try:
        online_users = websocket_service.manager.get_online_users()
        
        return {
            "success": True,
            "online_users": online_users,
            "count": len(online_users)
        }
        
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online users")


@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Join a WebSocket room
    
    Args:
        room_id: Room ID to join
        user_id: Optional user ID (defaults to current user)
        current_user: Current authenticated user
    """
    target_user_id = user_id or current_user.id
    
    try:
        await websocket_service.manager.join_room(target_user_id, room_id)
        
        return {
            "success": True,
            "message": f"User {target_user_id} joined room {room_id}",
            "room_id": room_id,
            "user_id": target_user_id
        }
        
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        raise HTTPException(status_code=500, detail="Failed to join room")


@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: str,
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Leave a WebSocket room
    
    Args:
        room_id: Room ID to leave
        user_id: Optional user ID (defaults to current user)
        current_user: Current authenticated user
    """
    target_user_id = user_id or current_user.id
    
    try:
        await websocket_service.manager.leave_room(target_user_id, room_id)
        
        return {
            "success": True,
            "message": f"User {target_user_id} left room {room_id}",
            "room_id": room_id,
            "user_id": target_user_id
        }
        
    except Exception as e:
        logger.error(f"Error leaving room: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave room")


@router.get("/rooms/{room_id}/users")
async def get_room_users(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get users in a specific room
    
    Args:
        room_id: Room ID
        current_user: Current authenticated user
    """
    try:
        room_users = websocket_service.manager.get_room_users(room_id)
        
        return {
            "success": True,
            "room_id": room_id,
            "users": room_users,
            "count": len(room_users)
        }
        
    except Exception as e:
        logger.error(f"Error getting room users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get room users")