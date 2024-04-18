import os
from uuid import UUID
from datetime import datetime, timedelta, timezone
import uvicorn

from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status as HTTPStatus


from models import StatusMessage, App, AppWithId
from settings import settings

# Custom Databackend Import----------------------------------------
if settings.data_backend == "couchdb":
  from tools import AppsCouchdbBackend as Apps
else:
  from tools import AppsFileBackend as Apps


#-Build and prep the App--------------------------------------------
tags_metadata = [
  {
    "name": "api-root",
    "description": "API State and testing",
  },
  {
    "name": "api-crud",
    "description": "Rest API CRUD Example",
  }
]

app = FastAPI(openapi_tags=tags_metadata)

#-Custom Middleware Functions----------------------------------------
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True
) 

#-The Routes--------------------------------------------------------
@app.get("/api", tags=["api-control"], response_model=StatusMessage)
async def api_status_get(request:Request):     
  my_status = StatusMessage(
    message="Hello from the API",
    method=request.method.upper(),
    request_url=request.url._url
  )
  return my_status

#-------------------
@app.post("/api/app", tags=["api-crud"], response_model=AppWithId)
async def api_app_post(item:App):
  new_item = AppWithId(**item.model_dump())
  try:
    apps = Apps()
    apps.add_item(item=new_item)
    # apps.save_data()
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  return new_item

#-------------------
@app.get("/api/apps", tags=["api-crud"], response_model=list[AppWithId])
async def api_apps_get():
  try:
    apps = Apps()
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  return apps.data


#-------------------
@app.get("/api/app/{id}", tags=["api-crud"], response_model=AppWithId)
async def api_app_get(id:UUID):
  try:
    apps = Apps()
    item = apps.get_item(id=id)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  return item

#-------------------
@app.put("/api/app/{id}", tags=["api-crud"], response_model=AppWithId)
async def api_app_put(id:UUID, item:AppWithId):
  try:
    apps = Apps()
    new_item = apps.update_item(id=id, item=item)
    # apps.save_data()
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  return new_item

#-------------------
@app.delete("/api/app/{id}", tags=["api-crud"], response_model=UUID)
async def api_app_delete(id:UUID):
  try:
    apps = Apps()
    apps.delete_item(id=id)
    # apps.save_data()
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))
  return id

#-------------------


#-------------------


#-The Runner--------------------------------------------------------
if __name__ == "__main__":
 
  if settings.app_mode == "dev":
    print("=> API Mode is: DEV")
    uvicorn.run(app="__main__:app", host="0.0.0.0", port=settings.app_port, reload=True)
  else:
    print("=> API Mode is: PROD")
    uvicorn.run(app="__main__:app", host="0.0.0.0", port=settings.app_port)

  
#-------------------------------------------------------------------