# Developer playbook

How to run each part of this repository, in the order you would meet them, with the failure each
step produces when a prerequisite is missing. [Development](development.md) is the reference for
*what* the commands check; this page is the reference for *getting them to run at all*.

This page is not published to the documentation site.

## Toolchain

| Tool | Version | Pinned by | Used for |
| --- | --- | --- | --- |
| `uv` | any recent | — | every Python environment, command, build and lock |
| Node | **24.19.0** | `website/.node-version`, `website/package.json` `engines` | the React portal only |
| pnpm | **11.0.9** | `website/package.json` `packageManager` | the React portal only |

Python is managed entirely by `uv`; you never create a virtualenv by hand and never run `pip`.

**Node is the version to get right first.** The portal declares `>=24 <25`. An older Node does not
hard-fail — pnpm prints

```text
[WARN] Unsupported engine: wanted: {"node":">=24 <25"} (current: {"node":"v22.20.0", ...})
```

and runs the command anyway. That is worse than a failure, because CI builds on 24 and a local run
on 22 is not the same run. Install the pinned version:

```bash
fnm install 24.19.0 && fnm use 24.19.0     # or: nvm install 24.19.0 && nvm use
node --version                             # must print v24.19.0
```

pnpm comes from `corepack`, which ships with Node — you do not install pnpm separately. Always
invoke it as `corepack pnpm`, and always from inside `website/`: corepack resolves the
`packageManager` field from its own working directory, so `pnpm --dir website ...` picks the wrong
version or none at all.

## The library

```bash
uv sync --all-extras --all-groups --locked
```

That single command installs the library, its extras, and every dependency group — including
`portal`, which holds `griffe` and `marimo`. The portal build shells back into this environment, so
skipping it makes the *website* fail later with a confusing Python error.

Run things:

```bash
uv run python -c "import scorequant as sq; print(sq.__all__)"
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto -m "not docs_execution"   # library tier
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto -m docs_execution         # prose tier
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py             # float32 leg
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_fit.py -k name         # one test, no -n
```

`-n auto` for a full run, omitted for a targeted one. X64 is an application choice made by the
caller; the package never touches global JAX configuration at import.

## The reference documentation site (MkDocs)

```bash
uv run mkdocs serve            # http://127.0.0.1:8000
uv run mkdocs build --strict   # what CI runs; a broken link or nav entry fails it
```

The API reference is collected from docstrings by mkdocstrings. `development.md`, `roadmap.md`,
`system-design.md`, this page, `adr/**` and `proposals/**` are excluded from the published site
(`mkdocs.yml` `exclude_docs`), and `tests/test_readme.py` asserts that the exclusion list and the
prose guard agree.

## The React portal

A Docusaurus site with a real Pyodide runtime, isolated from Python packaging.

### First run

```bash
cd website
corepack pnpm install --frozen-lockfile
corepack pnpm start                    # http://localhost:3000/scorequant/portal/
```

`start` runs `generate` first, and `generate` shells back to
`uv run python website/scripts/generate_data.py` from the repository root. **A bare
`pnpm install && pnpm start` fails** if the Python environment is not synced with the `portal`
group, because that script imports `griffe` to read the API surface.

In dev mode the Lab falls back to its fixture and search falls back to an in-memory route list;
both need the production build below.

### Production build

```bash
cd website
corepack pnpm build
```

`build` is `prepare:runtime` followed by `build:content`. `prepare:runtime` **downloads the pinned
Pyodide release (~15 MB) from GitHub and runs `uv build --wheel` from the repository root**, so it
needs network access and a working Python environment. It prunes Pyodide to the seven files the Lab
actually loads and drops the ScoreQuant wheel into `website/static/runtime/wheels/`.

Note `website/static/runtime/manifest.json` pins the wheel by filename, including its version — a
version bump requires re-running `prepare:runtime` rather than editing the manifest.

### Checks

```bash
corepack pnpm typecheck     # tsc --noEmit, strict
corepack pnpm lint          # eslint, type-aware
corepack pnpm test          # vitest
corepack pnpm validate      # generate + lessons + typecheck + lint + test + build:site
corepack pnpm test:e2e      # playwright; needs a prior build, it serves build/
```

### Previewing both sites together

```bash
uv run mkdocs build --strict
cd website && corepack pnpm assemble:preview
```

This writes `.pages-preview/` with MkDocs at the root and the portal at `/portal/`. It does **not**
deploy. Promoting the portal to the site root is a separately authorized migration step
([ADR 0019](adr/0019-react-learning-portal.md)); `portal-preview.yml` only uploads an artifact.

### Things that will cost you an hour if nobody says them

- `website/src/lab/protocol.generated.ts` is committed **and** generated. Edit
  `website/schema/lab-protocol.schema.json` and run `corepack pnpm generate:protocol`.
- `website/src/generated/portal-data.json` is likewise committed and generated, by
  `website/scripts/generate_data.py`.
- `website/src/css/global.css` is one file holding every page's styles. There are no CSS modules.
- There is no backend and no HTTP call to one. The `remote-jax` and `remote-pytorch` runners exist
  in the protocol schema and are explicitly unimplemented.
- In CI, `corepack enable` must run both before and after `setup-node`, because `cache: pnpm`
  shells out to `pnpm store path` in between.

## Examples and the FlowCyt study

Every example honors one environment variable:

```bash
SCOREQUANT_EXAMPLE_FAST=1 uv run python -m examples.gaussian_location
```

Any non-empty value shrinks dataset sizes and optimizer budgets. Unset keeps the full
research-scale sizes that produced the committed gallery figures — so leave it unset only when you
intend to regenerate and inspect them.

The FlowCyt study runs from the committed 1.3 MB fixture by default:

```bash
uv run python -m examples.cell_population --fixture examples/data/flowcyt_fixture.npz --quick
uv run python -m examples.cell_population --data-dir flowcyt-results/data_original   # full study
```

The full 3.7 GB dataset is gitignored and never committed. The FlowCyt data is licensed
CC BY-NC-SA 4.0, separately from ScoreQuant's MIT license; anything derived from it inherits
attribution and share-alike.

## Benchmarks

```bash
JAX_ENABLE_X64=1 uv run python benchmarks/bench.py --rows 20000 --bins 8
JAX_ENABLE_X64=1 uv run python benchmarks/bench.py --check benchmarks/baselines.json \
  --time-tolerance 10 --quality-rtol 1e-6
```

Run these unpinned and single-process — no `-n`, no thread pinning — because that is how
`benchmarks/baselines.json` was measured. Quality is the real regression signal; wall-clock is
deliberately given a loose tolerance because CI machines differ.

## Publishing a release

Nothing publishes automatically. `release.yml` triggers on a `v*` tag, so publication is a
deliberate push.

**Once, before the first release**, create the trusted publishers in the web UI. This is the only
step that cannot be done from here, and it is what removes the need for an API token anywhere:

| Field | Value |
| --- | --- |
| PyPI project | `scorequant` |
| Owner | `VitalyVorobyev` |
| Repository | `scorequant` |
| Workflow | `release.yml` |
| Environment | `pypi` (and `testpypi` on test.pypi.org) |

Then rehearse on TestPyPI — run the `Release` workflow manually with target `testpypi`, and install
what it produced into a scratch environment:

```bash
uv venv /tmp/sq && uv pip install --python /tmp/sq/bin/python   --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ scorequant
/tmp/sq/bin/python -c "import scorequant as sq; print(sq.__version__)"
```

Then publish for real:

```bash
git tag -a v0.1.0 -m "ScoreQuant 0.1.0"
git push origin v0.1.0
```

The workflow re-runs the full handoff gate, checks the tag matches the packaged version, runs
`twine check` so the README cannot render as raw text on the project page, and only then publishes.
Bumping a version means editing `pyproject.toml` alone — `scorequant.__version__` is read from
installed metadata — plus a `CHANGELOG.md` entry and re-running the portal's `prepare:runtime`,
since `website/static/runtime/manifest.json` pins the wheel by filename.

## Before handing work off

```bash
uv run ruff check . && uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

Plus `corepack pnpm validate` in `website/` when the portal changed.
