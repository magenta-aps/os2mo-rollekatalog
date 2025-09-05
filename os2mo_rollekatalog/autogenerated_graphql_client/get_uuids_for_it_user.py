from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetUuidsForItUser(BaseModel):
    itusers: "GetUuidsForItUserItusers"


class GetUuidsForItUserItusers(BaseModel):
    objects: List["GetUuidsForItUserItusersObjects"]


class GetUuidsForItUserItusersObjects(BaseModel):
    validities: List["GetUuidsForItUserItusersObjectsValidities"]


class GetUuidsForItUserItusersObjectsValidities(BaseModel):
    person: Optional[List["GetUuidsForItUserItusersObjectsValiditiesPerson"]]


class GetUuidsForItUserItusersObjectsValiditiesPerson(BaseModel):
    uuid: UUID
    engagements: List["GetUuidsForItUserItusersObjectsValiditiesPersonEngagements"]


class GetUuidsForItUserItusersObjectsValiditiesPersonEngagements(BaseModel):
    org_unit_uuid: UUID


GetUuidsForItUser.update_forward_refs()
GetUuidsForItUserItusers.update_forward_refs()
GetUuidsForItUserItusersObjects.update_forward_refs()
GetUuidsForItUserItusersObjectsValidities.update_forward_refs()
GetUuidsForItUserItusersObjectsValiditiesPerson.update_forward_refs()
GetUuidsForItUserItusersObjectsValiditiesPersonEngagements.update_forward_refs()
