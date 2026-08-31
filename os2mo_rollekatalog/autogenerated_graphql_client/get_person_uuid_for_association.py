from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetPersonUuidForAssociation(BaseModel):
    associations: "GetPersonUuidForAssociationAssociations"


class GetPersonUuidForAssociationAssociations(BaseModel):
    objects: List["GetPersonUuidForAssociationAssociationsObjects"]


class GetPersonUuidForAssociationAssociationsObjects(BaseModel):
    validities: List["GetPersonUuidForAssociationAssociationsObjectsValidities"]


class GetPersonUuidForAssociationAssociationsObjectsValidities(BaseModel):
    employee_uuid: Optional[UUID]


GetPersonUuidForAssociation.update_forward_refs()
GetPersonUuidForAssociationAssociations.update_forward_refs()
GetPersonUuidForAssociationAssociationsObjects.update_forward_refs()
GetPersonUuidForAssociationAssociationsObjectsValidities.update_forward_refs()
