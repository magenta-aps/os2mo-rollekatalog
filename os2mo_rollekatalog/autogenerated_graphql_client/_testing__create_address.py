from uuid import UUID

from .base_model import BaseModel


class TestingCreateAddress(BaseModel):
    address_create: "TestingCreateAddressAddressCreate"


class TestingCreateAddressAddressCreate(BaseModel):
    uuid: UUID


TestingCreateAddress.update_forward_refs()
TestingCreateAddressAddressCreate.update_forward_refs()
