<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# OS2mo-rollekatalog

OS2mo integration for [OS2Rollekatalog](https://www.os2.eu/os2rollekatalog).

Rollekatalog API documentation: https://htk.rollekatalog.dk/download/api.html.


## Usage

```
docker-compose up -d
```

Configuration is done through environment variables. Available options can be
seen in [os2mo_rollekatalog/config.py]. Complex variables such as dict or lists
can be given as JSON strings, as specified by Pydantic's settings parser.


## Development

In development, Rollekatalog is started on http://localhost:8090 and
SimpleSAMLphp on http://localhost:8050. The dev environment is configured for
OS2mos "Kolding" test dataset. In there, the user Ludvig is expected to be
syncronised to Rollekatalog. Run `./dev-environment/devtool` to make the needed changes
to his IT-users, force sync of Ludvig and make him administrator in Rollekatalog.


## Full synchronization

When first deployed or when a "full" sync is needed for other reasons (such as
a changed configuration), the following GraphQL query can be submitted to
OS2mo. The `owner` is the rollekatalog service-account UUID; it scopes the
refresh to this integration's own event listeners so the full sync doesn't
broadcast refresh events to every other integration listening on the same
routing keys.

`$root_uuids` must list the configured `ROOT_ORG_UNIT` **and** every UUID in
`EXTERNAL_ROOTS`, since the integration syncs org units under all of them.

```
mutation RefreshAll($root_uuids: [UUID!]!) {
  employee_refresh(owner: "2011e000-baad-c0de-726f-6c6c656b6174") {
    objects
  }
  org_unit_refresh(
    owner: "2011e000-baad-c0de-726f-6c6c656b6174"
    filter: { ancestor: { uuids: $root_uuids } }
  ) {
    objects
  }
  class_refresh(
    owner: "2011e000-baad-c0de-726f-6c6c656b6174"
    limit: 1
    filter: { facet: { user_keys: "engagement_job_function" } }
  ) {
    objects
  }
}
```

with variables:

```json
{ "root_uuids": ["<ROOT_ORG_UNIT>", "<EXTERNAL_ROOT_1>", "<EXTERNAL_ROOT_2>"] }
```


## Versioning

This project uses [Semantic Versioning](https://semver.org/) with the following
strategy:
- MAJOR: Incompatible API changes.
- MINOR: Backwards-compatible updates and functionality.
- PATCH: Backwards-compatible bug fixes.


## Authors

Magenta ApS <https://magenta.dk>


## License

- This project: [MPL-2.0](LICENSES/MPL-2.0.txt)

This project uses [REUSE](https://reuse.software) for licensing. All licenses can be found in the [LICENSES folder](LICENSES/) of the project.
