from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from typing import List, Dict, Optional
import jwt
from datetime import datetime, timedelta
from config.settings import API_SECRET_KEY
from fastapi import UploadFile

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key")

class ExternalAPI:
    def __init__(self, db_manager):
        self.db = db_manager
        self.app = FastAPI()
        self.setup_routes()
        
    def setup_routes(self):
        """Настройка маршрутов API"""
        
        @self.app.get("/api/v1/operations")
        async def get_operations(api_key: str = Depends(api_key_header)):
            """Получение списка операций"""
            if not await self.verify_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
                
            operations = await self.db.get_operations()
            return {"operations": operations}
            
        @self.app.get("/api/v1/operation/{operation_id}")
        async def get_operation(operation_id: int, api_key: str = Depends(api_key_header)):
            """Получение данных операции"""
            if not await self.verify_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
                
            operation = await self.db.get_operation_data(operation_id)
            if not operation:
                raise HTTPException(status_code=404, detail="Operation not found")
                
            return operation
            
        @self.app.post("/api/v1/operation/{operation_id}/points")
        async def add_points(operation_id: int, points: List[Dict], 
                           api_key: str = Depends(api_key_header)):
            """Добавление точек в операцию"""
            if not await self.verify_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
                
            success = await self.db.add_operation_points(operation_id, points)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to add points")
                
            return {"status": "success"}
            
        @self.app.get("/api/v1/operations/{operation_id}/map")
        async def get_operation_map(operation_id: int, api_key: str = Depends(api_key_header)):
            """Получение данных карты операции"""
            if not await self.verify_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
                
            map_data = await self.map_service.get_operation_map_data(operation_id)
            return {"map_data": map_data}
            
        @self.app.post("/api/v1/operations/{operation_id}/import")
        async def import_operation_data(
            operation_id: int,
            file: UploadFile,
            format: str,
            api_key: str = Depends(api_key_header)
        ):
            """Импорт данных операции"""
            if not await self.verify_api_key(api_key):
                raise HTTPException(status_code=403, detail="Invalid API key")
                
            content = await file.read()
            success = await self.data_exchange_service.import_operation_data(content, format)
            
            return {"success": success}
            
    async def verify_api_key(self, api_key: str) -> bool:
        """Проверка API ключа"""
        try:
            payload = jwt.decode(api_key, API_SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.InvalidTokenError:
            return False
            
    def generate_api_key(self, user_id: int, expires_in_days: int = 30) -> str:
        """Генерация API ключа"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=expires_in_days)
        }
        return jwt.encode(payload, API_SECRET_KEY, algorithm="HS256")
