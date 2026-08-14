from uuid import UUID

from .base_model import BaseModel


class TestingUpdateAddress(BaseModel):
    address_update: "TestingUpdateAddressAddressUpdate"


class TestingUpdateAddressAddressUpdate(BaseModel):
    uuid: UUID


TestingUpdateAddress.update_forward_refs()
TestingUpdateAddressAddressUpdate.update_forward_refs()
