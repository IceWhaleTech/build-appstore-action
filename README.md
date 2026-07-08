# Build ZimaOS AppStore Action

This composite GitHub Action wraps [`scripts/build_appstore.py`](./scripts/build_appstore.py) so other repositories can build ZimaOS-compatible AppStore output in a reusable way.

## What it does

- sets up Python
- installs required Python dependencies
- optionally installs required Ubuntu system packages
- normalizes `base-url`
- runs `build_appstore.py`

## Runner support

This action currently targets `ubuntu-latest` or other Debian/Ubuntu-based runners when `install-system-deps` is left enabled, because it uses `apt-get` to install `librsvg2-bin`.

## Inputs

| Name | Required | Default | Description |
|---|---|---|---|
| `source` | No | `.` | Source repository root |
| `output` | No | `dist` | Output directory |
| `base-url` | No | `""` | Base URL prefix for generated asset links |
| `cache-file` | No | `""` | Optional image metadata cache file |
| `digest-cache-file` | No | `""` | Optional image digest cache file |
| `python-version` | No | `3.11` | Python version used to run the build |
| `install-system-deps` | No | `true` | Whether to install `librsvg2-bin` via `apt-get` |

## Outputs

| Name | Description |
|---|---|
| `output-dir` | Final output directory passed to `build_appstore.py` |
| `base-url` | Final base URL used for the build |

## Secrets and environment

If you want better registry rate limits and digest resolution coverage, pass these environment variables:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## Usage

```yaml
name: Build AppStore

on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build dist
        uses: IceWhaleTech/build-appstore-action@v1
        with:
          source: .
          output: dist
          base-url: https://cdn.jsdelivr.net/gh/${{ github.repository }}@gh-pages
          cache-file: .cache/build_appstore/image-size-cache.json
          digest-cache-file: .cache/build_appstore/image-digest-cache.json
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
```

## Publishing as a public action

This repository is already structured as a standalone public action:

1. `action.yml` is at the repository root.
2. `scripts/build_appstore.py` is vendored into the repository.
3. `requirements.txt` lives beside the action metadata.

To publish it for stable reuse:

1. Commit and push the repository contents.
2. Create a release tag such as `v1.0.0`.
3. Add or move a major tag such as `v1`.
4. Reference it from workflows as `uses: IceWhaleTech/build-appstore-action@v1`.

If you later change behavior in a backward-incompatible way, publish that as a new major tag such as `v2`.
