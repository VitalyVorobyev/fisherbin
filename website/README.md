# ScoreQuant learning portal

A Docusaurus site with an in-browser ScoreQuant runtime (Pyodide + the NumPy backend). It is
deliberately isolated from Python packaging: Node and pnpm are pinned here, `uv` owns everything
Python.

```bash
corepack pnpm install --frozen-lockfile
corepack pnpm start        # http://localhost:3000/scorequant/portal/
```

Two things that are not obvious and will stop a first run:

- **Node >= 20** (`engines` in `package.json`); `.node-version` pins `24.19.0`, which is what CI
  builds on. A mismatch is not a hard failure — pnpm prints `[WARN] Unsupported engine` and runs
  the command anyway — so match `.node-version` when a build difference would matter.
- **`corepack` is not bundled with Node 25 and later.** Every command below invokes `corepack pnpm`
  so that pnpm's version comes from `packageManager` rather than from your machine. On a current
  Node, install it once with `npm install -g corepack@latest`, or the commands fail with
  `command not found: corepack`.
- **`start` shells back into `uv`.** It runs `generate` first, which executes
  `uv run python website/scripts/generate_data.py` from the repository root and needs the `portal`
  dependency group. Run `uv sync --all-extras --all-groups --locked` at the root first.

`corepack pnpm build` additionally downloads the pinned Pyodide release and builds the ScoreQuant
wheel, so it needs network access.

Full instructions, including the generated files you must not hand-edit and the checks CI runs, are
in [`docs/playbook.md`](../docs/playbook.md). The design contract is
[ADR 0019](../docs/adr/0019-react-learning-portal.md); the backend contract is
[ADR 0018](../docs/adr/0018-explicit-multi-backend-execution.md).
