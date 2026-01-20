import asyncio
import json
import uuid
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.connection_data: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Kết nối WebSocket"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        
        self.active_connections[session_id][connection_id] = websocket
        
        # Lưu thông tin connection
        self.connection_data[connection_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "connected_at": asyncio.get_event_loop().time()
        }
        
        return connection_id
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Ngắt kết nối WebSocket"""
        # Tìm connection_id
        for sid, connections in self.active_connections.items():
            for conn_id, ws in connections.items():
                if ws == websocket:
                    connections.pop(conn_id, None)
                    self.connection_data.pop(conn_id, None)
                    
                    # Xóa session nếu không còn connection
                    if not connections:
                        self.active_connections.pop(sid, None)
                    break
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Gửi message đến một WebSocket cụ thể"""
        await websocket.send_text(message)
    
    async def send_json_message(self, data: Dict, websocket: WebSocket):
        """Gửi JSON message đến một WebSocket cụ thể"""
        await websocket.send_json(data)
    
    async def broadcast_to_session(self, session_id: str, message: str):
        """Broadcast message đến tất cả connections trong session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id].values():
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def broadcast_json_to_session(self, session_id: str, data: Dict):
        """Broadcast JSON message đến tất cả connections trong session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id].values():
                try:
                    await connection.send_json(data)
                except:
                    pass
    
    def get_session_connections(self, session_id: str) -> List[WebSocket]:
        """Lấy tất cả connections của một session"""
        return list(self.active_connections.get(session_id, {}).values())
    
    def get_connection_count(self, session_id: str) -> int:
        """Lấy số lượng connections của session"""
        return len(self.active_connections.get(session_id, {}))
    
    def get_active_sessions(self) -> List[str]:
        """Lấy danh sách session đang active"""
        return list(self.active_connections.keys())

class WebSocketManager:
    def __init__(self):
        self.manager = ConnectionManager()
        self.audio_buffers: Dict[str, Dict] = {}  # Lưu buffer audio theo session
    
    async def handle_audio_chunk(self, session_id: str, chunk_data: Dict, connection_id: str):
        """Xử lý audio chunk từ client"""
        
        if session_id not in self.audio_buffers:
            self.audio_buffers[session_id] = {
                "chunks": [],
                "total_chunks": 0,
                "connections": set()
            }
        
        buffer = self.audio_buffers[session_id]
        buffer["connections"].add(connection_id)
        
        # Lưu chunk
        chunk_info = {
            "data": chunk_data.get("chunk"),
            "sequence": chunk_data.get("sequence", 0),
            "timestamp": chunk_data.get("timestamp"),
            "connection_id": connection_id
        }
        
        buffer["chunks"].append(chunk_info)
        buffer["total_chunks"] += 1
        
        # Nếu là chunk cuối từ tất cả connections
        is_last = chunk_data.get("is_last", False)
        
        if is_last:
            buffer["connections"].discard(connection_id)
            
            # Khi tất cả connections đã gửi xong
            if not buffer["connections"]:
                # Ghép tất cả chunks
                full_audio = await self._assemble_audio_chunks(buffer["chunks"])
                
                # Gửi để xử lý
                await self._process_complete_audio(session_id, full_audio, buffer["chunks"])
                
                # Xóa buffer
                self.audio_buffers.pop(session_id, None)
    
    async def _assemble_audio_chunks(self, chunks: List[Dict]) -> str:
        """Ghép audio chunks thành audio hoàn chỉnh"""
        # Sắp xếp theo sequence
        sorted_chunks = sorted(chunks, key=lambda x: x.get("sequence", 0))
        
        # Ghép base64 chunks
        audio_data = ""
        for chunk in sorted_chunks:
            if chunk.get("data"):
                audio_data += chunk["data"]
        
        return audio_data
    
    async def _process_complete_audio(self, session_id: str, audio_data: str, chunks: List[Dict]):
        """Xử lý audio hoàn chỉnh"""
        try:
            # Ở đây có thể gọi speech service để xử lý
            # Ví dụ: speech_to_text, phân tích pronunciation, etc.
            
            # Tạm thời broadcast message thông báo
            await self.manager.broadcast_json_to_session(session_id, {
                "type": "audio_processed",
                "session_id": session_id,
                "chunk_count": len(chunks),
                "status": "processing"
            })
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            await self.manager.broadcast_json_to_session(session_id, {
                "type": "error",
                "message": f"Audio processing error: {str(e)}"
            })
    
    async def handle_text_message(self, session_id: str, message_data: Dict, connection_id: str):
        """Xử lý tin nhắn text"""
        
        text = message_data.get("text", "")
        message_id = message_data.get("message_id", str(uuid.uuid4()))
        
        # Broadcast message đến tất cả connections trong session
        await self.manager.broadcast_json_to_session(session_id, {
            "type": "text_message",
            "message_id": message_id,
            "text": text,
            "sender": connection_id,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        return message_id
    
    async def handle_typing_indicator(self, session_id: str, connection_id: str, is_typing: bool):
        """Xử lý typing indicator"""
        # Gửi cho tất cả connections khác
        for conn_id, websocket in self.manager.active_connections.get(session_id, {}).items():
            if conn_id != connection_id:
                try:
                    await websocket.send_json({
                        "type": "user_typing",
                        "user_id": connection_id,
                        "is_typing": is_typing
                    })
                except:
                    pass
    
    async def send_ai_response(self, session_id: str, response_data: Dict):
        """Gửi phản hồi từ AI"""
        await self.manager.broadcast_json_to_session(session_id, {
            "type": "ai_response",
            **response_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def send_error(self, session_id: str, error_message: str):
        """Gửi thông báo lỗi"""
        await self.manager.broadcast_json_to_session(session_id, {
            "type": "error",
            "message": error_message,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    def cleanup_session(self, session_id: str):
        """Dọn dẹp session"""
        self.active_connections.pop(session_id, None)
        self.audio_buffers.pop(session_id, None)