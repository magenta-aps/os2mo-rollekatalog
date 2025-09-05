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
syncronised to Rollekatalog. Run `./dev-environment/devtool` to force sync
Ludvig and make him administrator in Rollekatalog.


## Full synchronization

When first deployed or when a "full" sync is needed for other reasons (such as
a changed configuration), the following GraphQL query can be submitted to
OS2mo:

```
mutation RefreshAll($exchange: "os2mo_rollekatalog", $root_uuid: UUID!) {
  employee_refresh(exchange: $exchange) {
    objects
  }
  org_unit_refresh(
    exchange: $exchange
    filter: { ancestor: { uuids: [$root_uuid] } }
  ) {
    objects
  }
  class_refresh(
    exchange: $exchange
    limit: 1
    filter: { facet: { user_keys: "engagement_job_function" } }
  ) {
    objects
  }
}
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
