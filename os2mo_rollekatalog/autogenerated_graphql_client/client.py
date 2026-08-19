from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from ._testing__create_address import (
    TestingCreateAddress,
    TestingCreateAddressAddressCreate,
)
from ._testing__create_class import TestingCreateClass, TestingCreateClassClassCreate
from ._testing__create_employee import (
    TestingCreateEmployee,
    TestingCreateEmployeeEmployeeCreate,
)
from ._testing__create_engagement import (
    TestingCreateEngagement,
    TestingCreateEngagementEngagementCreate,
)
from ._testing__create_facet import TestingCreateFacet, TestingCreateFacetFacetCreate
from ._testing__create_it_system import (
    TestingCreateItSystem,
    TestingCreateItSystemItsystemCreate,
)
from ._testing__create_it_user import (
    TestingCreateItUser,
    TestingCreateItUserItuserCreate,
)
from ._testing__create_manager import (
    TestingCreateManager,
    TestingCreateManagerManagerCreate,
)
from ._testing__create_org_unit import (
    TestingCreateOrgUnit,
    TestingCreateOrgUnitOrgUnitCreate,
)
from ._testing__update_address import (
    TestingUpdateAddress,
    TestingUpdateAddressAddressUpdate,
)
from ._testing__update_it_user import (
    TestingUpdateItUser,
    TestingUpdateItUserItuserUpdate,
)
from ._testing__update_org_unit import (
    TestingUpdateOrgUnit,
    TestingUpdateOrgUnitOrgUnitUpdate,
)
from .async_base_client import AsyncBaseClient
from .base_model import UNSET, UnsetType
from .get_org_unit import GetOrgUnit, GetOrgUnitOrgUnits
from .get_org_unit_uuid_for_kle import GetOrgUnitUuidForKle, GetOrgUnitUuidForKleKles
from .get_org_unit_uuid_for_manager import (
    GetOrgUnitUuidForManager,
    GetOrgUnitUuidForManagerManagers,
)
from .get_person import GetPerson, GetPersonEmployees
from .get_person_uuid_for_address import (
    GetPersonUuidForAddress,
    GetPersonUuidForAddressAddresses,
)
from .get_person_uuid_for_engagement import (
    GetPersonUuidForEngagement,
    GetPersonUuidForEngagementEngagements,
)
from .get_titles import GetTitles, GetTitlesClasses
from .get_uuids_for_it_user import GetUuidsForItUser, GetUuidsForItUserItusers
from .input_types import (
    AddressCreateInput,
    AddressUpdateInput,
    ClassCreateInput,
    EmployeeCreateInput,
    EngagementCreateInput,
    FacetCreateInput,
    ITSystemCreateInput,
    ITUserCreateInput,
    ITUserUpdateInput,
    ManagerCreateInput,
    OrganisationUnitCreateInput,
    OrganisationUnitUpdateInput,
)
from .refresh_all import RefreshAll


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def get_titles(self) -> GetTitlesClasses:
        query = gql(
            """
            query GetTitles {
              classes(filter: {facet: {user_keys: "engagement_job_function"}}) {
                objects {
                  current {
                    name
                    uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetTitles.parse_obj(data).classes

    async def get_person(
        self,
        employee_uuid: UUID,
        root_uuids: List[UUID],
        itsystem_user_keys: List[str],
        employee_email_user_key: str,
        mit_id_user_key: str,
        now: datetime,
    ) -> GetPersonEmployees:
        query = gql(
            """
            query GetPerson($employee_uuid: UUID!, $root_uuids: [UUID!]!, $itsystem_user_keys: [String!]!, $employee_email_user_key: String!, $mit_id_user_key: String!, $now: DateTime!) {
              employees(filter: {uuids: [$employee_uuid], from_date: $now, to_date: null}) {
                objects {
                  current {
                    uuid
                    user_key
                    nickname
                    name
                    email: addresses(
                      filter: {address_type: {user_keys: [$employee_email_user_key]}, from_date: null, to_date: null}
                    ) {
                      uuid
                      value
                      validity {
                        from
                        to
                      }
                      ituser(filter: {from_date: $now, to_date: null}) {
                        uuid
                      }
                    }
                    mitid: addresses(
                      filter: {address_type: {user_keys: [$mit_id_user_key]}, from_date: $now, to_date: null}
                    ) {
                      value
                      ituser(filter: {from_date: $now, to_date: null}) {
                        uuid
                      }
                    }
                    itusers(
                      filter: {itsystem: {user_keys: $itsystem_user_keys}, from_date: $now, to_date: null}
                    ) {
                      uuid
                      user_key
                      external_id
                      itsystem {
                        user_key
                      }
                      validity {
                        from
                        to
                      }
                      addresses(
                        filter: {address_type: {user_keys: [$employee_email_user_key]}, from_date: null, to_date: null}
                      ) {
                        uuid
                        value
                        validity {
                          from
                          to
                        }
                      }
                      engagements(filter: {from_date: $now, to_date: null}) {
                        validities {
                          uuid
                          validity {
                            from
                            to
                          }
                          org_unit(
                            filter: {ancestor: {uuids: $root_uuids}, from_date: $now, to_date: null}
                          ) {
                            uuid
                            org_unit_level {
                              uuid
                            }
                            ancestors {
                              uuid
                              org_unit_level {
                                uuid
                              }
                            }
                            validity {
                              from
                              to
                            }
                          }
                          job_function {
                            name
                            uuid
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "employee_uuid": employee_uuid,
            "root_uuids": root_uuids,
            "itsystem_user_keys": itsystem_user_keys,
            "employee_email_user_key": employee_email_user_key,
            "mit_id_user_key": mit_id_user_key,
            "now": now,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetPerson.parse_obj(data).employees

    async def get_uuids_for_it_user(self, uuid: UUID) -> GetUuidsForItUserItusers:
        query = gql(
            """
            query GetUuidsForItUser($uuid: UUID!) {
              itusers(filter: {uuids: [$uuid]}) {
                objects {
                  validities(start: null, end: null) {
                    person {
                      uuid
                      engagements {
                        org_unit_uuid
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetUuidsForItUser.parse_obj(data).itusers

    async def get_person_uuid_for_address(
        self, uuid: UUID
    ) -> GetPersonUuidForAddressAddresses:
        query = gql(
            """
            query GetPersonUuidForAddress($uuid: UUID!) {
              addresses(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetPersonUuidForAddress.parse_obj(data).addresses

    async def get_person_uuid_for_engagement(
        self, uuid: UUID
    ) -> GetPersonUuidForEngagementEngagements:
        query = gql(
            """
            query GetPersonUuidForEngagement($uuid: UUID!) {
              engagements(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetPersonUuidForEngagement.parse_obj(data).engagements

    async def get_org_unit(
        self,
        uuid: UUID,
        root_uuids: List[UUID],
        itsystem_user_keys: List[str],
        now: datetime,
    ) -> GetOrgUnitOrgUnits:
        query = gql(
            """
            query GetOrgUnit($uuid: UUID!, $root_uuids: [UUID!]!, $itsystem_user_keys: [String!]!, $now: DateTime!) {
              org_units(
                filter: {uuids: [$uuid], ancestor: {uuids: $root_uuids}, from_date: $now, to_date: null}
              ) {
                objects {
                  current {
                    uuid
                    name
                    parent {
                      uuid
                    }
                    org_unit_level {
                      uuid
                    }
                    ancestors {
                      uuid
                      org_unit_level {
                        uuid
                      }
                    }
                    managers(filter: {from_date: $now, to_date: null}) {
                      person(filter: {from_date: $now, to_date: null}) {
                        uuid
                        itusers(
                          filter: {itsystem: {user_keys: $itsystem_user_keys}, from_date: $now, to_date: null}
                        ) {
                          uuid
                          user_key
                          external_id
                          itsystem {
                            user_key
                          }
                          validity {
                            from
                            to
                          }
                          engagements(
                            filter: {org_unit: {uuids: [$uuid]}, from_date: $now, to_date: null}
                          ) {
                            current {
                              org_unit(filter: {from_date: $now, to_date: null}) {
                                uuid
                              }
                            }
                          }
                        }
                      }
                    }
                    kles(filter: {from_date: $now, to_date: null}) {
                      kle_number {
                        user_key
                      }
                      kle_aspects {
                        scope
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuid": uuid,
            "root_uuids": root_uuids,
            "itsystem_user_keys": itsystem_user_keys,
            "now": now,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetOrgUnit.parse_obj(data).org_units

    async def get_org_unit_uuid_for_kle(self, uuid: UUID) -> GetOrgUnitUuidForKleKles:
        query = gql(
            """
            query GetOrgUnitUuidForKle($uuid: UUID!) {
              kles(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    org_unit_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetOrgUnitUuidForKle.parse_obj(data).kles

    async def get_org_unit_uuid_for_manager(
        self, uuid: UUID
    ) -> GetOrgUnitUuidForManagerManagers:
        query = gql(
            """
            query GetOrgUnitUuidForManager($uuid: UUID!) {
              managers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    org_unit_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetOrgUnitUuidForManager.parse_obj(data).managers

    async def _testing__create_facet(
        self, input: FacetCreateInput
    ) -> TestingCreateFacetFacetCreate:
        query = gql(
            """
            mutation _Testing_CreateFacet($input: FacetCreateInput!) {
              facet_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateFacet.parse_obj(data).facet_create

    async def _testing__create_class(
        self, input: ClassCreateInput
    ) -> TestingCreateClassClassCreate:
        query = gql(
            """
            mutation _Testing_CreateClass($input: ClassCreateInput!) {
              class_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateClass.parse_obj(data).class_create

    async def _testing__create_org_unit(
        self, input: OrganisationUnitCreateInput
    ) -> TestingCreateOrgUnitOrgUnitCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnit($input: OrganisationUnitCreateInput!) {
              org_unit_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnit.parse_obj(data).org_unit_create

    async def _testing__update_org_unit(
        self, input: OrganisationUnitUpdateInput
    ) -> TestingUpdateOrgUnitOrgUnitUpdate:
        query = gql(
            """
            mutation _Testing_UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
              org_unit_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingUpdateOrgUnit.parse_obj(data).org_unit_update

    async def _testing__create_employee(
        self, input: EmployeeCreateInput
    ) -> TestingCreateEmployeeEmployeeCreate:
        query = gql(
            """
            mutation _Testing_CreateEmployee($input: EmployeeCreateInput!) {
              employee_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEmployee.parse_obj(data).employee_create

    async def _testing__create_address(
        self, input: AddressCreateInput
    ) -> TestingCreateAddressAddressCreate:
        query = gql(
            """
            mutation _Testing_CreateAddress($input: AddressCreateInput!) {
              address_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateAddress.parse_obj(data).address_create

    async def _testing__update_address(
        self, input: AddressUpdateInput
    ) -> TestingUpdateAddressAddressUpdate:
        query = gql(
            """
            mutation _Testing_UpdateAddress($input: AddressUpdateInput!) {
              address_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingUpdateAddress.parse_obj(data).address_update

    async def _testing__create_it_system(
        self, input: ITSystemCreateInput
    ) -> TestingCreateItSystemItsystemCreate:
        query = gql(
            """
            mutation _Testing_CreateItSystem($input: ITSystemCreateInput!) {
              itsystem_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItSystem.parse_obj(data).itsystem_create

    async def _testing__create_it_user(
        self, input: ITUserCreateInput
    ) -> TestingCreateItUserItuserCreate:
        query = gql(
            """
            mutation _Testing_CreateItUser($input: ITUserCreateInput!) {
              ituser_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItUser.parse_obj(data).ituser_create

    async def _testing__update_it_user(
        self, input: ITUserUpdateInput
    ) -> TestingUpdateItUserItuserUpdate:
        query = gql(
            """
            mutation _Testing_UpdateItUser($input: ITUserUpdateInput!) {
              ituser_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingUpdateItUser.parse_obj(data).ituser_update

    async def _testing__create_engagement(
        self, input: EngagementCreateInput
    ) -> TestingCreateEngagementEngagementCreate:
        query = gql(
            """
            mutation _Testing_CreateEngagement($input: EngagementCreateInput!) {
              engagement_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEngagement.parse_obj(data).engagement_create

    async def _testing__create_manager(
        self, input: ManagerCreateInput
    ) -> TestingCreateManagerManagerCreate:
        query = gql(
            """
            mutation _Testing_CreateManager($input: ManagerCreateInput!) {
              manager_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateManager.parse_obj(data).manager_create

    async def refresh_all(
        self, root_uuid: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> RefreshAll:
        query = gql(
            """
            mutation RefreshAll($root_uuid: [UUID!]) {
              employee_refresh(owner: "2011e000-baad-c0de-726f-6c6c656b6174") {
                objects
              }
              org_unit_refresh(
                owner: "2011e000-baad-c0de-726f-6c6c656b6174"
                filter: {ancestor: {uuids: $root_uuid}}
              ) {
                objects
              }
              class_refresh(
                owner: "2011e000-baad-c0de-726f-6c6c656b6174"
                limit: 1
                filter: {facet: {user_keys: "engagement_job_function"}}
              ) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {"root_uuid": root_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return RefreshAll.parse_obj(data)
