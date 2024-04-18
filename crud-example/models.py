import os
import socket
from typing import Any, Literal
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel

#--------------------------------------------------------
class StatusMessage(BaseModel):
    timestamp: datetime | None = None
    message: str
    method: Literal["GET", "POST", "PUT", "DELETE"]
    hostname: str | None = socket.gethostname()
    request_url: str | None = None

    #-------------
    def model_post_init(self, __context: Any) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now()

#-------------------- 
class Settings(BaseModel):
    data_backend: str | None = os.environ.get("DATA_BACKEND", "file")
    app_port: int | None = int( os.environ.get("APP_PORT", "5000"))
    app_mode: str | None = os.environ.get("APP_MODE", "prod")
    
    data_dir_path: str | None = os.environ.get("DATA_DIR_PATH", "./data")
    couchdb_connection_string: str | None = os.environ.get("COUCHDB_CONNECTION_STRING", "http://localhost:5984/")
    couchdb_database_name: str | None = os.environ.get("COUCHDB_DATABASE_NAME", "apps")
  


#--------------------
class App(BaseModel):
    name: str 
    manufacturer: str | None = None
    opensource: bool | None = False
    created: datetime | None = None
    updated: datetime | None = None
    category: Literal["Office", "Logistics", "Internet", "HR", "Multi Media","Social Media", "Development", "Others"] | None = "Others"
    version: str | None = None

    #-------------
    def model_post_init(self, __context: Any) -> None:
        if not self.created:
            self.created = datetime.now()
        if not self.updated:
            self.updated = datetime.now()

#--------------------
class AppWithId(App):
    id: UUID | None = None
    #-------------
    def model_post_init(self, __context: Any) -> None:
        if not self.id:
            self.id = uuid4()
        if not self.updated:
            self.updated = datetime.now()

#-------------------- 
            


#--------------------------------------------------------