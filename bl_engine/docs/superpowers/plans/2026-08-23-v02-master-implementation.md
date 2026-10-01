# Grounded Synthetic Creative Cognition v0.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved v0.2 executable-contract redesign end-to-end, closing integrity/oracle/verification/state bypasses first and then integrating prose, creative, character/reader, and release truth contracts.

**Architecture:** Preserve the existing standalone Python runtime, but replace permissive dict/caller-authority boundaries with typed positive-construction interfaces. `prepare_scene()` becomes the orchestration root, the writer sees only a projected `RealizationPacket`, `verify_proposal()` owns mandatory check execution and proof receipts, and `commit_verified()` requires typed deltas plus current semantic hash/version. Executability/claim ledgers bind the design to reachable code and fresh release evidence.

**Tech Stack:** Python 3.11+, dataclasses/enums, jsonschema, pytest, stdlib hashlib/json/zipfile.

**Spec:** `docs/GROUNDED_SYNTHETIC_CREATIVE_COGNITION_v0.2_DESIGN_SPEC.md`

## Global Constraints

- DJAR is a design/reference kernel only; the final writing package remains standalone.
- Model defaults have zero authorial authority; suspicion alone is not a hard stylistic failure.
- Writer context is positive-constructed and no-oracle; raw canonical state is never writer input.
- Required verifier set is fixed before qualification; skipped required checks yield `ASSURANCE_NOT_MET`.
- Failed/assurance-not-met proposals never mutate durable state.
- Semantic state hash and version must both match at commit.
- Unknown StateDelta namespaces fail closed.
- No fixed paragraph length/sentence count rules and no universal one-line paragraph ban.
- Generated prose never self-promotes into durable author identity.
- Structural and literary validation remain separate claim gates.
- Repository has no git metadata; each subproject ends with a full regression checkpoint instead of a commit.

---

### Task 1: Subproject A — Integrity Gate Closure

**Files:**
- Create: `stateful_author/contracts.py`
- Modify: `stateful_author/runtime.py`, `stateful_author/verifier.py`, `stateful_author/provenance.py`, `stateful_author/receipt.py`
- Create: `tests/test_v02_integrity_gate.py`

**Interfaces:**
- Produces `StateDelta`, `TransformationRecord`, `CheckReceipt`, `VerificationRecord`, `verify_proposal()`, semantic `state_hash()` and strict `commit_verified()`.
- Later tasks consume `PreparedScene.required_verifier_set`, `VerificationRecord`, and typed `StateDelta`.

- [ ] Write regression tests for caller-forged verification, missing mandatory checks, evidence without refs, same-version state mutation, unknown delta namespace, and failed commit.
- [ ] Run `pytest tests/test_v02_integrity_gate.py -q` and confirm RED for missing v0.2 contracts.
- [ ] Implement typed verification/commit objects and mandatory registry execution.
- [ ] Run targeted tests until GREEN.
- [ ] Run full `pytest -q` and resolve compatibility failures without weakening new gates.

### Task 2: Subproject B — No-Oracle Projection Compiler

**Files:**
- Create: `stateful_author/projection.py`
- Modify: `stateful_author/epistemic.py`, `stateful_author/packet.py`, `stateful_author/runtime.py`, `runtime/WRITER_PACKET_SCHEMA.json`
- Create: `tests/test_v02_projection.py`

**Interfaces:**
- Consumes `SceneContract`, canonical state, selected conception/artifacts.
- Produces `ActorView`, `RelationshipView`, `RealizationPacket`; `PreparedScene.writer_packet` is derived only from this packet.

- [ ] Write oracle-leak tests covering hidden master plan, reader correct answer, objective-only affordance, narrator mode, focal identity, and unknown-key rejection.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement positive projection and writer schema; remove raw-state pass-through on official path.
- [ ] Run targeted tests until GREEN.
- [ ] Run full regression suite.

### Task 3: Subproject C — Prose / Model-Prior Control Plane

**Files:**
- Modify: `stateful_author/surface.py`, `stateful_author/model_prior.py`, `stateful_author/verifier.py`, `stateful_author/failure_router.py`
- Create: `stateful_author/repair.py`
- Create: `tests/test_v02_model_prior.py`

**Interfaces:**
- Produces structural prose observations, scoped behavior evidence, failure depth, `RepairPacket`, and receipt invalidation rules.

- [ ] Write mutation-family tests for single/double newline staircase, long one-sentence blocks, 1/2/1/2/1 topology, no-period fragments, legitimate dialogue, justified isolation, regularized 3/3/3/3, rhetorical paraphrases, semantic echo, closure/affective normalization, and functional repetition evidence.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement structural parsing, paragraph topology, model-prior families, suspicion-vs-failure, repair scope/invalidation.
- [ ] Run targeted tests until GREEN.
- [ ] Run full regression suite.

### Task 4: Subproject D — Creative Search Integration

**Files:**
- Modify: `stateful_author/creative.py`, `stateful_author/runtime.py`, `stateful_author/cognition.py`
- Create: `tests/test_v02_creative_search.py`

**Interfaces:**
- Produces `SceneDistinction`, `SearchDecision`, `GenerativeAxiom`, `CandidateGenealogy`, `CrossExamRecord`, and integrated `prepare_scene()` search receipt.

- [ ] Write tests for DIRECT/LIGHT/HIGH routing, structural same-basin paraphrases, transform authority, winner dominance, candidate independence metadata, and repeated-basin strategy shift.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement search controller and structural genealogy/cross-exam integration without generating prose candidates.
- [ ] Run targeted tests until GREEN.
- [ ] Run full regression suite.

### Task 5: Subproject E — Character / Reader / Interaction Integration

**Files:**
- Modify: `stateful_author/epistemic.py`, `stateful_author/reader.py`, `stateful_author/runtime.py`, `stateful_author/serial.py`, `stateful_author/commercial.py`
- Create: `stateful_author/interaction.py`
- Create: `tests/test_v02_partial_worlds.py`

**Interfaces:**
- Produces active cognitive sets, relationship views, reader activation/tractability records, epistemic action eligibility, strategic-agent projections, and post-generation interaction-frame confirmation.

- [ ] Write tests for active-vs-stored knowledge, grounded memory distortion, self-model gap preservation, perceived-vs-objective options, reader stale clue activation, evidence-gain-without-answer-gain, grounded uptake, and non-transformative scene metabolism.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement sparse partial-world/reader/interaction execution helpers and runtime integration.
- [ ] Run targeted tests until GREEN.
- [ ] Run full regression suite.

### Task 6: Subproject F — Executability / Release / Evaluation

**Files:**
- Create: `stateful_author/executability.py`
- Modify: `stateful_author/release.py`, `tools/validate_package.py`, `tools/run_master_soak.py`, `VERIFICATION_REPORT.md`, `README.md`, `START_HERE.md`, `VERSION`, `pyproject.toml`
- Create: `verify/EXECUTION_LEDGER.json`, `verify/CLAIM_LEDGER.json`
- Create: `tools/validate_execution_ledger.py`, `tools/run_v02_adversarial.py`
- Create: `tests/test_v02_executability.py`

**Interfaces:**
- Produces ledger validation, critical/noncritical contract coverage, claim status, freshness fingerprints, adversarial-family report, and release-linked verification bundle.

- [ ] Write tests for unreachable ledger entries, critical coverage, stale artifact fingerprints, claim overreach, and release manifest linkage.
- [ ] Run targeted tests and confirm RED.
- [ ] Implement ledgers, coverage, freshness and release linkage.
- [ ] Run targeted tests until GREEN.
- [ ] Run full tests, schema validation, validator, adversarial suite, master soak, ledger validator, compileall.
- [ ] Build final ZIP, extract to a new clean-room directory, rerun the entire structural verification set, and record hashes/results without making literary-superiority claims.
