import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Final, List, Union

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

import env_constants as env_const
from config_parser_utils import cp


class DBNames(str, Enum):
    TESTING: Final = "testing"


class DBTables(str, Enum):
    GET_USER: Final = "get_user"
    POST_USER: Final = "post_user"


class DriverTypes(str, Enum):
    PYMONGO = "pymongo"
    MOTOR = "motor"


class AbstractDBDriverHandler(ABC):
    @abstractmethod
    def set(self, table_name: str, value: Union[str, Dict[str, Any]]) -> Any:
        """
        Set record in the database table.
        """
        pass

    @abstractmethod
    def get_all(self, table_name: str):
        """
        Get all the records from the database table.
        """
        pass


@dataclass
class MongoCredentials:
    url: Union[str, List] = ""
    user: str = ""
    pwd: str = ""
    replicaset: str = ""
    connection_uri: str = ""


def _get_credentials() -> MongoCredentials:
    connection_uri = cp.get_subsection("local_mongodb_config", "CONNECTION_URI")
    replica_set = (
        cp.get_subsection("local_mongodb_config", "REPLICA_SET")
        if cp.get_subsection("local_mongodb_config", "REPLICA_SET")
        else None
    )
    if connection_uri:
        return MongoCredentials(connection_uri=connection_uri, replicaset=replica_set)
    return MongoCredentials(
        url=os.environ.get(
            env_const.DB_URL,
            cp.get_subsection("local_mongodb_config", "MONGODB_URL"),
        ),
        user=os.environ.get(
            env_const.DB_USER,
            cp.get_subsection("local_mongodb_config", "MONGODB_USER"),
        ),
        pwd=os.environ.get(
            env_const.DB_PWD,
            cp.get_subsection("local_mongodb_config", "MONGODB_PWD"),
        ),
    )


class PymongoDBHandler(AbstractDBDriverHandler):
    def __init__(self, database_name: str) -> None:
        cred = _get_credentials()
        self._client = self.initialize_pymongo_client(cred)
        self._mdb = self._client[database_name]

    @staticmethod
    def initialize_pymongo_client(cred: MongoCredentials):
        if cred.connection_uri:
            return MongoClient(cred.connection_uri)
        return MongoClient(
            cred.url,
            username=cred.user,
            password=cred.pwd,
            authMechanism="SCRAM-SHA-256",
            connect=True,
        )

    def set(self, table_name: str, value: Union[str, Dict[str, Any]]) -> Any:
        record = value if isinstance(value, dict) else json.loads(value)
        result = self._mdb[table_name].insert_one(record)
        return {"ack": result.acknowledged, "id": str(result.inserted_id)}

    def get_all(self, table_name: str):
        result = self._mdb[table_name].find({}, projection={"_id": False})
        return [el for el in result]


class MotorDBHandler(AbstractDBDriverHandler):
    def __init__(self, database_name: str) -> None:
        cred = _get_credentials()
        self._client = self.initialize_motor_client(cred)
        self._mdb = self._client[database_name]

    @staticmethod
    def initialize_motor_client(cred: MongoCredentials):
        if cred.connection_uri:
            return AsyncIOMotorClient(cred.connection_uri)
        return AsyncIOMotorClient(
            cred.url,
            username=cred.user,
            password=cred.pwd,
            authMechanism="SCRAM-SHA-256",
            connect=True,
        )

    async def set(self, table_name: str, value: Union[str, Dict[str, Any]]) -> Any:
        record = value if isinstance(value, dict) else json.loads(value)
        result = await self._mdb[table_name].insert_one(record)
        return {"ack": result.acknowledged, "id": str(result.inserted_id)}

    async def get_all(self, table_name: str):
        cursor = self._mdb[table_name].find({}, projection={"_id": False})
        results = []
        async for document in cursor:
            results.append(document)
        return results


class DBHandlerManager:
    @classmethod
    @lru_cache
    def get_db_handler(
        cls,
        database: DBNames = DBNames.TESTING,
        driver_type: DriverTypes = DriverTypes.PYMONGO,
    ):
        _clazz = cls._get_dao(driver_type)
        _instance = _clazz(database_name=database.value)
        return _instance

    @classmethod
    def _get_dao(cls, driver_type: DriverTypes):
        if driver_type == DriverTypes.PYMONGO:
            return PymongoDBHandler
        if driver_type == DriverTypes.MOTOR:
            return MotorDBHandler
        raise ValueError(f"No such driver type: {driver_type}")
