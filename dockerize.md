# Containerizing the DSSAT Multi-Agent Pipeline

## Objective

Move the multi-agent pipeline — currently a set of Python functions running in a
single process — into independent Docker containers, one per agent, so each agent
runs, scales, and fails independently instead of as one monolithic script.

## Why

Right now every agent (the chatbot's decision-making agents, and the agents that
build each section of a DSSAT experiment file) runs in-process and passes data to the
next agent as an in-memory Python object. That works for a single-user prototype, but
it means:
- Every agent shares the same dependencies, the same failure domain, and the same
  scaling behavior — a slow or crashing agent takes the whole pipeline down with it.
- There's no clean boundary for testing, deploying, or replacing one agent without
  touching the rest.
- It can't be distributed across machines or scaled per-agent (e.g. running many
  parallel fertilizer-design agents while keeping a single shared weather-data agent).

Containerizing each agent turns the pipeline into a set of independent services that
communicate over HTTP, matching how the system was already diagrammed conceptually.

## Two layers of agents

The system has two tiers of agents, and both are being containerized:

**1. The chatbot-decision agents** — the ones that understand the farmer's question,
design an experiment, and check its quality:
- **Orchestrator** — decides whether a question needs a full simulation or can be
  answered directly.
- **Experiment Designer** — extracts what the farmer is asking about and proposes
  experimental treatments to test it.
- **Quality Check** — critiques the proposed experiment and sends it back for
  revision if it doesn't meet a scientific-rigor bar.
- **Analytics** — turns the final results into a plain-language answer for the
  farmer.
- **(Planned) AWS Agent** — will eventually upload generated files and run the
  actual crop simulation model in the cloud. Not built yet; the pipeline currently
  stops at file generation.

**2. The file-generation agents** — once an experiment design is approved, a second
set of agents builds the actual DSSAT input file, one agent per section of that file:
Field, Weather, Planting, Fertilizer, Irrigation, Residue, Initial Conditions,
Simulation Control, and a final Assembler agent that combines everything into one
file.

The two tiers connect at one handoff point: once the Quality Check agent approves a
design, it's handed to the file-generation agents to actually build the file.

## Approach

Each agent becomes its own lightweight web service (a small container exposing one
API endpoint: "here's my input, here's my output"). A shared base container image
carries the common dependencies so each individual agent's image stays small. The
agents are then wired together with Docker Compose, replacing today's direct
function calls with HTTP requests between containers — the logical flow of the
pipeline doesn't change, only how the steps are connected.

## Phased plan

| Phase | Agent(s) | Status |
|---|---|---|
| 0 | Shared base image (common dependencies) | Planned |
| 1 | Weather agent | **In progress** |
| 2 | Residue, Initial Conditions, Simulation Control agents | Planned |
| 3 | Field agent | Planned |
| 4 | Planting, Fertilizer, Irrigation agents | Planned |
| 5 | Assembler agent | Planned |
| 6 | Connect the file-generation agents together | Planned |
| 7 | Quality Check agent | Planned |
| 8 | Orchestrator agent | Planned |
| 9 | Experiment Designer agent | Planned |
| 10 | Analytics agent | Planned |
| 11 | Connect the full pipeline end-to-end | Planned |
| Future | AWS Agent + running the actual simulation model | Not started |

The rollout is intentionally incremental: start with the simplest, most
self-contained agent (Weather — no external dependencies besides a public weather
API), prove the containerization pattern works end-to-end, then apply the same
pattern to each remaining agent in order of increasing complexity.

## Current status

Actively containerizing the **Weather agent** — the first and simplest agent in the
file-generation tier, since it has no dependency on the shared modeling library or
any credentials, only a public weather data API.
