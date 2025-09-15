from datetime import datetime
from uuid import UUID

from ._testing__create_employee import (
    TestingCreateEmployee,
    TestingCreateEmployeeEmployeeCreate,
)
from ._testing__create_engagement import (
    TestingCreateEngagement,
    TestingCreateEngagementEngagementCreate,
)
from ._testing__create_it_system import (
    TestingCreateItSystem,
    TestingCreateItSystemItsystemCreate,
)
from ._testing__create_it_user import (
    TestingCreateItUser,
    TestingCreateItUserItuserCreate,
)
from ._testing__create_org_unit import (
    TestingCreateOrgUnit,
    TestingCreateOrgUnitOrgUnitCreate,
)
from ._testing__create_org_unit_root import (
    TestingCreateOrgUnitRoot,
    TestingCreateOrgUnitRootOrgUnitCreate,
)
from ._testing__get_engagement_type import (
    TestingGetEngagementType,
    TestingGetEngagementTypeFacets,
)
from ._testing__get_job_function import (
    TestingGetJobFunction,
    TestingGetJobFunctionFacets,
)
from ._testing__get_org_unit_type import (
    TestingGetOrgUnitType,
    TestingGetOrgUnitTypeClasses,
)
from ._testing__move_org_unit_to_root import (
    TestingMoveOrgUnitToRoot,
    TestingMoveOrgUnitToRootOrgUnitUpdate,
)
from ._testing__rename_org_unit import (
    TestingRenameOrgUnit,
    TestingRenameOrgUnitOrgUnitUpdate,
)
from .async_base_client import AsyncBaseClient
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
                    user_key
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
        root_uuid: UUID,
        ad_itsystem_user_key: str,
        fk_itsystem_user_key: str,
        now: datetime,
    ) -> GetPersonEmployees:
        query = gql(
            """
            query GetPerson($employee_uuid: UUID!, $root_uuid: UUID!, $ad_itsystem_user_key: String!, $fk_itsystem_user_key: String!, $now: DateTime!) {
              employees(filter: {uuids: [$employee_uuid], from_date: $now, to_date: null}) {
                objects {
                  current {
                    uuid
                    user_key
                    nickname
                    name
                    addresses(
                      filter: {address_type: {scope: "EMAIL"}, from_date: $now, to_date: null}
                    ) {
                      uuid
                      value
                    }
                    itusers(
                      filter: {itsystem: {user_keys: [$ad_itsystem_user_key, $fk_itsystem_user_key]}, from_date: $now, to_date: null}
                    ) {
                      user_key
                      external_id
                      itsystem {
                        user_key
                      }
                    }
                    engagements(filter: {from_date: $now, to_date: null}) {
                      org_unit(
                        filter: {ancestor: {uuids: [$root_uuid]}, from_date: $now, to_date: null}
                      ) {
                        uuid
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
            """
        )
        variables: dict[str, object] = {
            "employee_uuid": employee_uuid,
            "root_uuid": root_uuid,
            "ad_itsystem_user_key": ad_itsystem_user_key,
            "fk_itsystem_user_key": fk_itsystem_user_key,
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
        root_uuid: UUID,
        ad_itsystem_user_key: str,
        fk_itsystem_user_key: str,
        now: datetime,
    ) -> GetOrgUnitOrgUnits:
        query = gql(
            """
            query GetOrgUnit($uuid: UUID!, $root_uuid: UUID!, $ad_itsystem_user_key: String!, $fk_itsystem_user_key: String!, $now: DateTime!) {
              org_units(
                filter: {uuids: [$uuid], ancestor: {uuids: [$root_uuid]}, from_date: $now, to_date: null}
              ) {
                objects {
                  current {
                    uuid
                    name
                    parent {
                      uuid
                    }
                    managers(filter: {from_date: $now, to_date: null}) {
                      person(filter: {from_date: $now, to_date: null}) {
                        uuid
                        itusers(
                          filter: {itsystem: {user_keys: [$ad_itsystem_user_key, $fk_itsystem_user_key]}, from_date: $now, to_date: null}
                        ) {
                          user_key
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
            "root_uuid": root_uuid,
            "ad_itsystem_user_key": ad_itsystem_user_key,
            "fk_itsystem_user_key": fk_itsystem_user_key,
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

    async def _testing__get_org_unit_type(self) -> TestingGetOrgUnitTypeClasses:
        query = gql(
            """
            query _Testing_GetOrgUnitType {
              classes(filter: {facet_user_keys: "org_unit_type"}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetOrgUnitType.parse_obj(data).classes

    async def _testing__create_org_unit_root(
        self, name: str, root_uuid: UUID, org_unit_type: UUID
    ) -> TestingCreateOrgUnitRootOrgUnitCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnitRoot($name: String!, $root_uuid: UUID!, $org_unit_type: UUID!) {
              org_unit_create(
                input: {uuid: $root_uuid, name: $name, org_unit_type: $org_unit_type, validity: {from: "2010-02-03"}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "name": name,
            "root_uuid": root_uuid,
            "org_unit_type": org_unit_type,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnitRoot.parse_obj(data).org_unit_create

    async def _testing__create_org_unit(
        self, name: str, parent: UUID, org_unit_type: UUID
    ) -> TestingCreateOrgUnitOrgUnitCreate:
        query = gql(
            """
            mutation _Testing_CreateOrgUnit($name: String!, $parent: UUID!, $org_unit_type: UUID!) {
              org_unit_create(
                input: {name: $name, parent: $parent, org_unit_type: $org_unit_type, validity: {from: "2010-02-03"}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "name": name,
            "parent": parent,
            "org_unit_type": org_unit_type,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnit.parse_obj(data).org_unit_create

    async def _testing__rename_org_unit(
        self, uuid: UUID, name: str
    ) -> TestingRenameOrgUnitOrgUnitUpdate:
        query = gql(
            """
            mutation _Testing_RenameOrgUnit($uuid: UUID!, $name: String!) {
              org_unit_update(
                input: {uuid: $uuid, validity: {from: "2013-05-05"}, name: $name}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid, "name": name}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingRenameOrgUnit.parse_obj(data).org_unit_update

    async def _testing__create_employee(
        self, first_name: str, last_name: str
    ) -> TestingCreateEmployeeEmployeeCreate:
        query = gql(
            """
            mutation _Testing_CreateEmployee($first_name: String!, $last_name: String!) {
              employee_create(input: {given_name: $first_name, surname: $last_name}) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "first_name": first_name,
            "last_name": last_name,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEmployee.parse_obj(data).employee_create

    async def _testing__create_it_system(
        self, name: str
    ) -> TestingCreateItSystemItsystemCreate:
        query = gql(
            """
            mutation _Testing_CreateItSystem($name: String!) {
              itsystem_create(
                input: {user_key: $name, name: $name, validity: {from: "2014-02-01"}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"name": name}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItSystem.parse_obj(data).itsystem_create

    async def _testing__create_it_user(
        self, itsystem: UUID, person: UUID, name: str
    ) -> TestingCreateItUserItuserCreate:
        query = gql(
            """
            mutation _Testing_CreateItUser($itsystem: UUID!, $person: UUID!, $name: String!) {
              ituser_create(
                input: {user_key: $name, itsystem: $itsystem, person: $person, validity: {from: "2015-02-08"}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "itsystem": itsystem,
            "person": person,
            "name": name,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateItUser.parse_obj(data).ituser_create

    async def _testing__create_engagement(
        self, orgunit: UUID, person: UUID, engagement_type: UUID, job_function: UUID
    ) -> TestingCreateEngagementEngagementCreate:
        query = gql(
            """
            mutation _Testing_CreateEngagement($orgunit: UUID!, $person: UUID!, $engagement_type: UUID!, $job_function: UUID!) {
              engagement_create(
                input: {org_unit: $orgunit, engagement_type: $engagement_type, job_function: $job_function, person: $person, validity: {from: "2016-05-05"}}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "orgunit": orgunit,
            "person": person,
            "engagement_type": engagement_type,
            "job_function": job_function,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEngagement.parse_obj(data).engagement_create

    async def _testing__get_engagement_type(self) -> TestingGetEngagementTypeFacets:
        query = gql(
            """
            query _Testing_GetEngagementType {
              facets(filter: {user_keys: "engagement_type"}) {
                objects {
                  current {
                    classes {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetEngagementType.parse_obj(data).facets

    async def _testing__get_job_function(self) -> TestingGetJobFunctionFacets:
        query = gql(
            """
            query _Testing_GetJobFunction {
              facets(filter: {user_keys: "engagement_job_function"}) {
                objects {
                  current {
                    classes {
                      uuid
                      user_key
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingGetJobFunction.parse_obj(data).facets

    async def _testing__move_org_unit_to_root(
        self, uuid: UUID
    ) -> TestingMoveOrgUnitToRootOrgUnitUpdate:
        query = gql(
            """
            mutation _Testing_MoveOrgUnitToRoot($uuid: UUID!) {
              org_unit_update(
                input: {uuid: $uuid, validity: {from: "2020-05-08"}, parent: null}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingMoveOrgUnitToRoot.parse_obj(data).org_unit_update

    async def refresh_all(self, exchange: str, root_uuid: UUID) -> RefreshAll:
        query = gql(
            """
            mutation RefreshAll($exchange: String!, $root_uuid: UUID!) {
              employee_refresh(exchange: $exchange) {
                objects
              }
              org_unit_refresh(exchange: $exchange, filter: {ancestor: {uuids: [$root_uuid]}}) {
                objects
              }
              class_refresh(
                exchange: $exchange
                limit: 1
                filter: {facet: {user_keys: "engagement_job_function"}}
              ) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {"exchange": exchange, "root_uuid": root_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return RefreshAll.parse_obj(data)
