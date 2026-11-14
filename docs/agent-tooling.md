# Skills and rules for Codex + Cursor

Selection reviewed on 2026-11-14 for the project's actual stage. Priorities were stack
fit, identifiable provenance, portability, and narrow scope. This is not a universal
ranking or a guarantee of scientific quality.

## Repository skills

| Skill | Source | When to use |
| --- | --- | --- |
| vercel-react-best-practices | Vercel | Implement/review React and Next.js loading, rendering, and fetching |
| web-design-guidelines | Vercel | Review UI, accessibility, and navigation experience |
| cosmic-spherex-pipeline | Project-authored | IRSA, FITS, WCS, compatibility, and apparent motion |
| cosmic-api-contracts | Project-authored | FastAPI, contracts, jobs, persistence, and copilot limits |
| cosmic-reproducible-experiments | Project-authored | Notebooks, evaluation, baseline, and labeled injections |

The three project skills derive from team architecture and requirements; they are
not official NASA or Astropy skills. A skill guides work: it does not install a
scientific library, implement a detector, or prove accuracy by itself.

The available catalog was inspected with skill-installer.
[openai/skills](https://github.com/openai/skills) declares itself deprecated and points
to [openai/plugins](https://github.com/openai/plugins). Older notebook, CI, and security
skills were therefore not installed from that catalog. Current options inspected
included other plugin dependencies; this setup favors local workflows without requiring
additional services.

The two external skills come from
[vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills), pinned to commit
`1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62`. `.agents/skills-sources.json` records source
paths and revision. Preserve authorship/license metadata; do not attribute these guides
to the Cosmic Hunter AI team. To update, inspect the upstream diff before deliberately
changing the manifest revision. Do not automatically download and execute third-party
code whenever the project opens.

`web-design-guidelines` fetches current remote guidance during interface reviews. The
package revision is pinned, but that remote content can change. Record the consulted
URL/revision when an audit needs to be reproducible.

## Activation

[Codex customization](https://learn.chatgpt.com/docs/customization/overview) supports
AGENTS.md and repository skills in `.agents/skills`. The
[Cursor documentation](https://cursor.com/docs/skills) recognizes that directory too,
allowing one copy per skill. Open this repository root in both tools. Skills should
be discoverable in a new turn/session after the repository is rediscovered. Check
the editor list; loading in a local Cursor session has not yet been verified.

Codex: invoke by name, for example `$cosmic-spherex-pipeline`.
Cursor: type `/` and search for the skill name. If an older version does not discover
it, ask the agent to read its SKILL.md directly without duplicating files. Update the
editor when native discovery is required.

## Rules

AGENTS.md is the central guide for both assistants: architecture boundaries, scientific
integrity, security, verification commands, coordination, and the English language default.
[Cursor rules](https://cursor.com/docs/rules) live in `.cursor/rules`:

- project.mdc: always active; points to the central guide.
- science.mdc: attached when working on astronomy, detection, or notebooks.
- backend.mdc: API, workers, AI, SQL, and contracts.
- frontend.mdc: Next.js interface and scientific visualizations.

Vercel guidance does not override project decisions: keep TanStack Query when an
example recommends SWR. Check version compatibility before applying performance advice.
Rules and skills guide the model; they do not replace CI, authorization, network
restrictions, or branch protection.

## Suggested work allocation

Codex can handle backend, pipeline, contracts, and evaluation; Cursor can handle the
interface and contract integration. Either tool can perform either role. Assign
different files and a shared-contract owner. See docs/team-plan.md for the three-person
allocation covering the full project.

Use separate branches/worktrees after a base commit exists; otherwise work in turns
until the first commit. Inspect actual Git state before choosing the workflow. Avoid
two agents writing the same file or uv.lock.

Each handoff should state the outcome, changed files, generated contract, checks run,
and limitations. The next editor must inspect status/diff before continuing. Distinguish
local changes, commits, and published content.

## Example requests

```text
Codex: use $cosmic-spherex-pipeline to implement a bounded IRSA query.
Read AGENTS.md. Preserve provenance and test archive failures. Do not download
large regions or invent results if the service is unavailable.
```

```text
Cursor: read AGENTS.md and use vercel-react-best-practices to implement the
explorer in apps/web against the existing OpenAPI contract. Show actual empty
states and errors; do not populate observations with fabricated data.
```

```text
Codex: use $cosmic-reproducible-experiments to evaluate the available baseline.
Declare data and splits, execute from scratch, and separate synthetic results
from recovery of known objects. Do not claim metrics without execution.
```
