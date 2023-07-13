from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config_parser_utils import cp
from db_access.db_handler import DBHandlerManager, DBTables, DriverTypes


class Record(BaseModel):
    user_id: int


app = FastAPI(
    debug=True,
    title="Benchmarking FastAPI Pymongo vs FastAPI Motor",
    description="Benchmarking FastAPI Pymongo vs FastAPI Motor",
    swagger_ui_parameters={"deepLinking": True, "displayOperationId": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    summary="Return the health status of this service if it's running",
    operation_id="HealthCheck",
)
async def health_check():
    """
    Health check to see if service is working as expected
    """
    return {"message": f"Service is up and well as of {datetime.utcnow()} UTC."}


@app.post(
    "/async/{driver_type}",
    summary="Add new record",
    operation_id="AddNewRecord",
    tags=["Async"],
)
async def add_new_record(driver_type: DriverTypes, record: Record):
    db_handler = DBHandlerManager.get_db_handler(driver_type=driver_type)
    if driver_type == DriverTypes.MOTOR:
        return await db_handler.set(
            table_name=DBTables.POST_USER.value, value=record.dict()
        )
    if driver_type == DriverTypes.PYMONGO:
        return db_handler.set(table_name=DBTables.POST_USER.value, value=record.dict())


@app.get(
    "/async/{driver_type}",
    summary="Get all records",
    operation_id="GetAllRecords",
    tags=["Async"],
)
async def get_all_records(driver_type: DriverTypes):
    db_handler = DBHandlerManager.get_db_handler(driver_type=driver_type)
    if driver_type == DriverTypes.MOTOR:
        return await db_handler.get_all(table_name=DBTables.GET_USER.value)
    if driver_type == DriverTypes.PYMONGO:
        return db_handler.get_all(table_name=DBTables.GET_USER.value)


@app.post(
    "/sync/pymongo",
    summary="Sync route to add new record",
    operation_id="SyncAddNewRecord",
    tags=["Sync"],
)
def sync_add_new_record(record: Record):
    db_handler = DBHandlerManager.get_db_handler(driver_type=DriverTypes.PYMONGO)
    return db_handler.set(table_name=DBTables.POST_USER.value, value=record.dict())


@app.get(
    "/sync/pymongo",
    summary="Sync route to get all records",
    operation_id="SyncGetAllRecords",
    tags=["Sync"],
)
def sync_get_all_records():
    db_handler = DBHandlerManager.get_db_handler(driver_type=DriverTypes.PYMONGO)
    return db_handler.get_all(table_name=DBTables.GET_USER.value)


if __name__ == "__main__":
    # TODO: On startup create one client.
    uvicorn.run(
        "main:app",
        **cp.get_section("service_config"),
    )
