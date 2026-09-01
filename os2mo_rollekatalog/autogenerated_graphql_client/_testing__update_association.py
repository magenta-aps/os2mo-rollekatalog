from uuid import UUID

from .base_model import BaseModel


class TestingUpdateAssociation(BaseModel):
    association_update: "TestingUpdateAssociationAssociationUpdate"


class TestingUpdateAssociationAssociationUpdate(BaseModel):
    uuid: UUID


TestingUpdateAssociation.update_forward_refs()
TestingUpdateAssociationAssociationUpdate.update_forward_refs()
