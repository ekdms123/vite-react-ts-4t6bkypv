# Grounded Synthetic Creative Cognition Runtime v0.2 — DJAR Executable-Contract Redesign

Date: 2026-08-23  
Target lineage: Stateful Synthetic Author Runtime v2 RC3 → Grounded Synthetic Creative Cognition Runtime v3 → v0.2 redesign  
Status: **APPROVED DESIGN CONSOLIDATION — IMPLEMENTATION NOT YET STARTED**  
Design basis: DJAR v2.1 High-Assurance RootKernel principles + approved Sections 1–5 + prior 69-defect hardening + source re-analysis + model-prior audit

---

## 0. Purpose

This redesign addresses a specific structural failure discovered after the v3 structural release: the documentation could state a high-level creative contract correctly while the executable path either bypassed it, represented it only as a dormant type, or enforced only a shallow approximation.

The redesign therefore changes the primary engineering target from **more writing rules** to **executable contract alignment**.

The governing thesis is:

> **A rule written in documentation has no runtime authority. Only a rule enforced through a typed boundary, executable transformation, verification receipt, or commit gate is an implemented rule.**

A second invariant governs prose quality:

> **MODEL DEFAULT HAS ZERO AUTHORIAL AUTHORITY.**

A foundation model may naturally prefer one-line paragraph staircases, rhetorical contrast templates, early emotional closure, explanatory restatement, omniscient interpretation, over-connected causality, generic social-role priors, or other recurrent behaviors. None of those behaviors are automatically forbidden. They are simply not authorized by model preference alone. Their legitimacy must come from user authority, source-conditioned author identity, character ownership, relationship ritual, scene function, pressure state, or another grounded local cause.

This is not an AI-detector evasion system and does not attempt to imitate human error. Its aim is to prevent generic model priors from silently overriding the synthetic author's grounded creative decisions.

---

## 1. Design Status and Claim Boundary

### 1.1 What is already supported by evidence

The preceding project work established:

- a 69-item integrity defect set in the earlier RC3 runtime;
- a source-dimension split that avoids percentage blending;
- source re-analysis identifying distinct roles for the four supplied works;
- a useful master architecture covering partial cognition, creative search, reader models, strategic ecology, model-prior control, and stable-frontier evaluation;
- a v3 structural release whose test suite and package integrity passed its then-current checks;
- a later adversarial audit showing that green tests did not prove all master contracts were executable.

### 1.2 Newly confirmed architectural failure class

The post-release audit identified a broader class of defects:

**DOCUMENTATION–EXECUTION DIVERGENCE**

Examples included:

- qualification paths capable of accepting externally supplied failure lists rather than mandatorily executing the verifier registry;
- writer-packet paths capable of carrying omniscient or raw state despite the NO-ORACLE design;
- state commits insufficiently bound to content hashes and exact delta namespaces;
- paragraph verification detecting only narrow surface forms rather than paragraph topology;
- model-prior checks existing as shallow regex or caller-supplied booleans while the master described richer behavioral control;
- creative, interaction, reader, and affordance types existing without end-to-end runtime integration.

This redesign makes that failure class itself release-blocking.

### 1.3 Non-claims

This design does **not** establish:

- literary superiority;
- human preference gain;
- universal elimination of recognizable model habits;
- exact author reproduction;
- universal genre optimality;
- AI-detector invisibility;
- long-horizon superiority without controlled generation tests.

Those remain `ASSURANCE_NOT_MET` until external experiments support them.

---

# PART I — EXECUTABLE ARCHITECTURE

## 2. Nine Top-Level Invariants

All implementation decisions must reduce to these invariants.

1. **Truth never comes from creativity.**
2. **Capability never grants authority.**
3. **The prose writer never sees knowledge it cannot legitimately realize.**
4. **Model default has zero authorial authority.**
5. **Every material durable transformation requires grounded provenance and explicit authority.**
6. **Every PASS requires evidence that every required check actually executed.**
7. **Failed or assurance-not-met prose never mutates durable state.**
8. **Generated behavior never teaches itself into durable author identity without authorized evidence.**
9. **No implementation claim exists without executable contract coverage.**

These are release-blocking contracts.

---

## 3. Eight Execution Planes

The runtime is reorganized into eight executable planes.

```text
0 AUTHORITY / GROUND
        ↓
1 CANONICAL REALITY
        ↓
2 PARTIAL-WORLD MODELING
        ↓
3 CREATIVE CONCEPTION
        ↓
4 REALIZATION PROJECTION COMPILER
        ↓
5 PROSE REALIZATION
        ↓
6 MANDATORY VERIFICATION
        ↓
7 TRANSACTIONAL COMMIT / RECOVERY
        ↓
8 LONG-HORIZON / HOLDOUT / LITERARY EVALUATION
```

Plane transitions are typed interfaces, not descriptive prose. A downstream plane cannot obtain upstream-only state except through its declared projection.

---

# PART II — TYPED STATE AND AUTHORITY BOUNDARIES

## 4. SceneContract

Every scene begins from a required `SceneContract`.

Required conceptual fields:

```text
SceneContract
- scene_id
- focal_character_id
- narrator_mode
- requested_effect
- required_events
- prohibited_events
- locked_facts
- creative_freedom
- continuity_requirements
- parent_state_version
- parent_state_hash
```

### 4.1 Contract rules

- `focal_character_id` and `narrator_mode` are mandatory and survive every projection into realization.
- `requested_effect` may not be silently replaced by a creative reframe.
- `required_events` cannot be deleted by a candidate conception.
- `prohibited_events` cannot be reintroduced through specialist cognition or repair.
- `creative_freedom` explicitly defines transformable space.
- parent version and parent semantic hash are both required for later commit.

---

## 5. GroundClaim and Provenance

Material runtime claims use a typed record rather than rank names or caller booleans.

```text
GroundClaim
- claim_id
- value
- source_class
- confidence
- evidence_refs
- scope
- authority
- dependencies
```

### 5.1 Evidence requirements

Claims classified as `TEXT_OBSERVED`, `STATE_DERIVED`, `DERIVED`, or external evidence cannot become verified Ground without appropriate evidence references.

A confidence label such as `DERIVED_HIGH_CONFIDENCE` is not itself evidence.

Derived confidence cannot exceed the minimum/appropriate support confidence under the chosen derivation policy.

### 5.2 Unknown

Unknown remains first-class:

```text
UNKNOWN != FALSE
UNKNOWN != FAILURE
UNKNOWN != PERMISSION TO INVENT
```

A critical unknown blocks only transformations that depend on it.

---

## 6. CanonicalReality

`CanonicalReality` is the only durable truth store.

Conceptual namespaces:

```text
CanonicalReality
├── facts
├── diegetic_evidence
├── actors
├── relationships
├── world
├── institutions
├── open_loops
├── recurrences
├── reader_state
├── serial_state
├── voice_state
└── provenance
```

Direct mutation is unsupported.

The only supported durable transition is:

```text
CanonicalReality
+ Verified Typed StateDelta
→ Commit Gate
→ New CanonicalReality
```

---

## 7. Runtime Truth vs Diegetic Evidence

The runtime must distinguish truth from in-world evidence.

`X said Y` may be verified runtime truth while proposition `Y` remains false, uncertain, manipulated, or deceptive.

```text
DiegeticEvidence
- evidence_id
- proposition
- evidence_type
- source_actor
- reliability
- observed_by
- timestamp
- provenance_refs
```

Permitted evidence types include:

- PERCEPTION
- TESTIMONY
- DOCUMENT
- RUMOR
- MEMORY
- INFERENCE
- DECEPTION
- FABRICATED

This distinction is mandatory for mystery, unreliable memory, deception, and dramatic irony.

---

## 8. ActorCognitiveState and ActorView

Durable actor state and scene realization state are separate.

### 8.1 Durable actor state

```text
ActorCognitiveState
├── stored_knowledge
├── beliefs
├── remembered_models
├── self_model
├── disclosure_state
├── goals
├── values
├── competence
├── risk_model
├── body_state
├── affective_state
└── history
```

### 8.2 Scene-specific projection

```text
ActorView
- focal_id
- reachable_facts
- active_knowledge
- active_beliefs
- relevant_memory
- relevant_unknowns
- active_goals
- suppressed_goal_pressure
- current_body
- affective_residue
- perceived_options
- perceived_risks
- relationship_permissions
- attention_bias
- local_judgment_policy
- current_blind_spots
```

The prose writer receives `ActorView`, never raw `ActorCognitiveState`.

### 8.3 Stored knowledge is not active knowledge

The runtime must not treat `actor knows X` as `actor is currently thinking about X`.

Retrieval uses scene relevance and accessibility rather than insertion-order truncation.

If context budgets force omission, the control plane records truncation internally. The writer is not told token-management metadata.

---

## 9. Objective vs Perceived Affordances

The runtime distinguishes:

- objective world affordances;
- bodily affordances;
- institutional permissions;
- relationship permissions;
- perceived affordances;
- cost and risk.

A focal character acts from perceived affordances and reachable knowledge, not planner omniscience.

If the world has a secret exit unknown to the focal actor, that exit cannot appear in the focal `RealizationPacket`.

---

## 10. Self-Model Gap and Affective Hysteresis

When relevant, keep separate:

- declared motive;
- believed motive;
- behavior-policy evidence.

The narrator must not automatically resolve discrepancies.

Affective state is path-dependent:

```text
current response
= f(prior affect, body state, interpretation history, current event)
```

Scene boundaries do not reset emotion to baseline.

Habituation and sensitization are conditional possibilities, not universal curves.

---

# PART III — CREATIVE CONCEPTION EXECUTION

## 11. PreparedScene as Orchestration Output

The official preparation root is conceptually:

```text
prepare_scene(SceneContract, CanonicalReality) -> PreparedScene
```

`PreparedScene` contains:

```text
PreparedScene
- contract
- parent_state_identity
- grounded_distinctions
- focal_view
- relevant_other_actor_views
- reader_view
- search_receipt
- selected_conception
- specialist_artifacts
- realization_packet
- required_verifier_set
```

Only `realization_packet` is generator-facing.

---

## 12. SceneDistinction

The runtime should not route scenes through raw boolean tags.

```text
SceneDistinction
- scene_id
- dominant_problem
- current_scene_function
- consequence_level
- knowledge_pressure
- relationship_pressure
- causal_pressure
- strategic_pressure
- affective_pressure
- reader_uncertainty_pressure
- major_reveal
- irreversible_choice
- relationship_phase_change
- identity_sensitive
- canon_sensitive
- evidence_refs
- confidence
- unresolved_conflicts
```

Contradictory high-impact distinctions must be represented explicitly rather than silently suppressing one another.

---

## 13. Scene Metabolism

The following remain verifier/control vocabulary rather than mandatory writer labels:

- TRANSFORM
- CONSOLIDATE
- INHABIT
- RECOVER
- CALIBRATE
- INCUBATE
- RELEASE

A scene need not create a durable state delta to be valid.

Commercial or serial evaluation must not treat legitimate `INHABIT`, `RECOVER`, or `INCUBATE` scenes as false progress merely because they lack transformation tags.

---

## 14. Creative Search Decision

Every scene chooses one search path:

```text
SearchDecision
- path: DIRECT | LIGHT_EXPLORE | HIGH_ASSURANCE
- reason
- search_budget
- allowed_modes
```

### 14.1 DIRECT

Use when the scene problem is already clear, low-risk, and does not justify expensive alternative search.

### 14.2 LIGHT_EXPLORE

Use for bounded alternatives where two structurally different options are enough.

### 14.3 HIGH_ASSURANCE

Use for high-value/high-risk scenes such as:

- consequential choice;
- major reveal;
- relationship phase change;
- defining first impression;
- climax;
- repeated genericity failure;
- same-basin collapse;
- major canon consequence;
- explicit request for unusual/high-peak conception.

High-assurance search is sparse, not default.

---

## 15. Creative Search Modes

### COMBINE

Recombine already-grounded elements before inventing new ones.

### EXPLORE

Search alternative locally rational actions within current rules.

### REFRAME

Question the creative problem itself while preserving user-required outcomes and hard anchors.

### TRANSFORM

Alter an unlocked assumption of the conceptual space. Hard anchors are not transformable.

---

## 16. GenerativeAxiomMap

Before high-assurance search, identify why the obvious answer appears obvious.

```text
GenerativeAxiom
- axiom_id
- proposition
- class
- evidence
- transform_authority
```

Classes:

- HARD_ANCHOR
- SOFT_CONSTRAINT
- CHARACTER_ASSUMPTION
- READER_ASSUMPTION
- GENRE_DEFAULT
- MODEL_DEFAULT
- FREE_VARIABLE

`MODEL_DEFAULT` is explicitly transformable when no stronger authority supports it.

---

## 17. CandidateConcept and Genealogy

Candidates are structural conceptions, not prose drafts.

```text
CandidateConcept
- candidate_id
- search_mode
- dominant_causal_premise
- focal_interpretation
- initiating_action
- expected_uptake
- knowledge_asymmetry
- perceived_option_change
- relationship_permission_change
- reader_model_effect
- required_state_support
- debts_created
- unresolved_unknowns
- genealogy
```

Candidate genealogy records changed and preserved assumptions and the major structural axis changed.

### 17.1 Candidate independence

Sibling candidates do not see one another before cross-examination.

### 17.2 Same-basin rejection

Diversity is structural, not lexical.

At least one material axis must differ when high-divergence search is required:

- causal premise;
- goal structure;
- knowledge asymmetry;
- spatial solution;
- relationship permission;
- perceived affordance;
- interaction frame;
- focal interpretation;
- reader-model effect.

Paraphrases are one basin.

### 17.3 Grounded distance

A candidate must be sufficiently different **and** sufficiently grounded. Novelty alone is not quality.

---

## 18. Creative Entropy Regulator

The controller regulates divergence.

- high convergence + good grounding → increase search distance;
- high arbitrariness → reduce distance / strengthen constraints;
- repeated failure → change structural axis or search mode;
- a strong admissible candidate exists → stop generating novelty.

The runtime must not continue divergence for its own sake.

---

## 19. Cross-Examination and Winner-Dominant Synthesis

Each candidate is cross-examined on:

- Ground integrity;
- authority integrity;
- local rationality;
- causal legibility;
- reader tractability;
- novelty;
- arbitrariness;
- relationship continuity;
- option consequence;
- model-default dependence;
- creative debt;
- critical unknowns.

No universal quality scalar is required.

Synthesis is winner-dominant. One candidate owns the causal conception. Other candidates may contribute bounded constraints or evidence handling only. If imported material changes the winner's core conception, the result is a new candidate requiring verification.

---

## 20. Problem Discovery Loop

A candidate may expose a weak initial distinction.

```text
ProblemReframeProposal
- old_problem
- proposed_problem
- why_old_is_weak
- preserved_user_effect
- authority_conflicts
```

A reframe is provisional until checked against user request, required events, canon, and locks.

---

# PART IV — RELATIONSHIP, INTERACTION, STRATEGIC, AND READER EXECUTION

## 21. RelationshipView

Relationships are topology, not intimacy scores.

Scene-relevant projection:

```text
RelationshipView
- currently_normal_actions
- currently_costly_actions
- boundary_actions
- taboo_actions
- repair_expectations
- current_debts
- relevant_common_ground
```

Important changes may be represented as permission deltas rather than declaration tags.

---

## 22. Epistemic Action

Distinguish:

- instrumental action: acts to change the world;
- epistemic action: acts to improve the actor's model.

Epistemic-action specialists activate only when uncertainty is material, information has value, and probing is locally rational.

Do not inject psychological games into ordinary scenes by default.

---

## 23. Strategic Ecology

Only materially strategic agents receive strategic state.

```text
StrategicAgentView
- objective
- reachable_knowledge
- beliefs
- resources
- risk_tolerance
- current_strategy
- model_of_other_agent
- adaptation_state
```

A strategic agent can adapt when it can observe material protagonist actions.

Ordinary NPCs do not receive expensive strategic modeling by default.

---

## 24. Emergent Interaction Frame

Interaction frames are not fully pre-authored.

The conception may specify:

```text
starting_frame
possible_frame_shift
```

but cannot assert that the shift occurred before generated action and uptake support it.

Execution concept:

```text
F0
→ Actor A move
→ Actor B uptake / rejection / reinterpretation
→ provisional frame proposal F1
→ post-generation evidence check
→ frame delta candidate
```

An emergent frame becomes durable only after prose verification and state commit.

This prevents the planner from turning “emergence” into another hidden plot instruction.

---

## 25. Uptake

Utterance/action intent and received meaning are distinct.

```text
Action or Utterance Intent
↓
Partner Uptake
↓
Relational / Interaction Meaning
```

Uptake may confirm, reject, distort, overread, underread, or strategically exploit the original act.

Misunderstanding must be grounded in common ground, attention, bias, relationship state, or strategic interest; random misunderstanding is prohibited as fake humanization.

---

## 26. ReaderView

Reader state is planner-facing only.

```text
ReaderView
- active_hypotheses
- latent_hypotheses
- retrievable_evidence
- current_questions
- anticipated_outcomes
- tractability
- dominant_engagement_route
```

The writer does not receive the correct answer, desired reader hypothesis, manipulation target, or full hypothesis graph.

### 26.1 Hypothesis status

Avoid fake precision. Use bands such as:

- DOMINANT
- PLAUSIBLE
- WEAK
- LATENT
- DISCONFIRMED

### 26.2 Reader evidence activation

Distinguish stored, active, retrievable, and stale evidence.

A payoff may require natural reactivation of old evidence when it has become stale.

### 26.3 Tractability

Useful uncertainty permits model updating. Lack of evidence is not automatically mystery difficulty.

### 26.4 Evidence gain without answer gain

A scene may make epistemic progress by changing relative support among hypotheses without revealing a final answer.

---

## 27. Hierarchical Prediction Error

Surprise may occur at different levels:

- word/local phrasing;
- action;
- scene;
- relationship;
- causal model;
- ontology;
- arc.

Do not maximize surprise at every level simultaneously. Large high-level revisions may require stable lower-level realization for tractability.

---

# PART V — REALIZATION PROJECTION AND PROSE

## 28. Realization Projection Compiler

This is the central architectural correction.

The writer packet is **not** a sanitized subset of canonical state.

It is a positively constructed independent object produced from authorized projections.

Conceptual schema:

```text
RealizationPacket
├── scene
│   ├── scene_id
│   ├── focal_id
│   └── narrator_mode
├── authority
│   ├── required_events
│   └── prohibited_events
├── focal_now
│   ├── reachable
│   ├── unknown
│   ├── active_goals
│   ├── body
│   ├── affect
│   ├── perceived_options
│   └── attention
├── relationship_now
├── world_now
├── conception
├── cognition_artifacts
├── realization_prior
└── continuity
```

The schema is positive allow-list only. Unknown keys fail construction rather than being silently stripped.

---

## 29. NO-ORACLE Writer Boundary

The following cannot appear in `RealizationPacket`:

- raw `CanonicalReality`;
- objective secret truth unreachable to focal realization;
- correct mystery answer;
- desired reader answer or manipulation target;
- hidden master plan;
- unreachable actor knowledge;
- rejected candidates;
- verifier diagnostics;
- failure history;
- source excerpts;
- source author names;
- source-analysis documents;
- stylometric statistics;
- model-prior blacklist explanations;
- full open-loop registry;
- full recurrence registry;
- full relationship graph;
- full biography/history dumps.

This boundary is release-blocking.

---

## 30. Specialist Intelligence Contract

A specialist is executable only if it transforms grounded scene state into a small typed concrete artifact.

Generic advice is not a specialist output.

Examples:

```text
RevealArtifact
- current_focal_model
- available_evidence
- newly_visible_evidence
- recoded_assumption
- remaining_unknown
```

```text
RelationshipArtifact
- current_permission
- pressure_on_boundary
- observable_cost
- newly_possible_action
- still_forbidden_action
```

```text
FrameTransferArtifact
- character_owned_source_frame
- current_target_situation
- plausible_mapping
- suppression_reason_if_unavailable
```

Writer payloads should favor scene-specific conclusions over theoretical guidance.

Specialists cannot invent events outside SceneContract/SceneConception authority.

---

## 31. Base Craft vs Specialist Cognition

Ordinary competent craft is always available.

The absence of a specialist means only that no high-resolution specialist optimization is authorized. It does not prohibit normal dialogue, spatial awareness, relationship behavior, or humor when naturally available.

---

## 32. Style Manifold

Style is a condition-dependent manifold rather than one averaged target.

Possible regions include:

- ordinary domestic;
- dialogue-heavy;
- humor;
- embarrassment;
- acute pressure;
- pain;
- aftermath;
- memory;
- reveal;
- emotional integration;
- procedural/problem-solving.

The writer receives a minimal `RealizationPrior` such as conditional permissions/tendencies, not corpus statistics.

Stylometric profiles remain verifier/evaluation-side boundaries.

---

## 33. Realization Causality

The default causal ordering for prose is flexible but grounded:

```text
accessible focal attention
→ local judgment
→ action / hesitation / speech
→ world / other-person response
→ updated attention
→ emotional/relational interpretation if now accessible
```

This is not a sentence template.

The verifier may analyze observable transitions to detect recurrent model-default discourse patterns.

---

## 34. Paragraph Topology

### 34.1 Core rule

> **CONTINUE UNLESS BOUNDARY.**

A sentence is not a paragraph by default.

Paragraph continuation is preferred while the same attention, action, causal, or interaction chain remains active.

Potential boundary causes include:

- attention-target change;
- causal-phase change;
- meaningful action completion;
- speaker/interaction ownership shift;
- uptake shift;
- temporal discontinuity;
- spatial discontinuity;
- decision commitment;
- information-regime change;
- pressure/recovery phase change;
- justified dramatic isolation.

No fixed sentence-count or character-count quotas are allowed.

### 34.2 Isolation

A one-sentence paragraph is permitted when locally justified by a material event such as decision, shock, reversal, reveal, temporal break, interaction turn, pressure break, or rare rhythmic exception.

It is not automatically permitted merely because the sentence is emphatic.

### 34.3 Paragraph verifier requirements

The executable verifier must cover at least:

- single-newline and double-newline topology;
- isolated narrative-line density;
- rolling staircase patterns such as `1/1/2/1/1`;
- long one-sentence paragraph bypasses;
- no-period fragment chains;
- justified dialogue line behavior;
- justified decisive isolation;
- alternative regularization such as uniform `3/3/3/3` paragraph shapes;
- repeated terminal-function patterns.

The objective is not to maximize variation but to detect paragraph shape that is weakly explained by scene structure and strongly explained by recurrent model habit.

---

## 35. Terminal Function Analysis

Paragraph endings may be classified by observable discourse function, such as:

- action continuation;
- perception;
- question;
- open judgment;
- speech;
- transition;
- temporary resolution;
- abstract summary;
- emotional closure;
- thematic closure;
- dramatic stinger.

Repeated `ABSTRACT_SUMMARY → EMOTIONAL_CLOSURE → DRAMATIC_STINGER` style endings across unrelated contexts are model-prior candidates.

No individual terminal form is globally banned.

---

## 36. Semantic Echo and Abstract Restatement

A prose segment may be flagged when it restates an already available proposition without adding material fact, inference, action consequence, sensory evidence, or relational information.

Intentional repetition is protected when ownership/function evidence exists.

Concrete action followed by immediate abstract interpretation is not automatically wrong. It becomes suspicious when the abstraction merely explains an already legible meaning and recurs as a model-default discourse pattern.

---

## 37. Affective Normalization Firewall

The runtime checks for repeated patterns where conflict, pain, fear, shame, or relational rupture are too quickly converted into understanding, acceptance, resolve, empathy, or relief without sufficient scene evidence.

Direct emotional naming is not prohibited.

The relevant question is whether the emotional interpretation is available to the focal self-model at that point and supported by the current affective history.

`SELF_MODEL_OVERRESOLUTION` is distinct from simple emotional vocabulary.

---

## 38. Rhetorical Pattern Families

Do not detect only exact phrases such as `A가 아니라 B`.

Represent recurring relations such as:

- NEGATE → REFRAME → EXPLAIN;
- OBSERVE → ABSTRACT → CONCLUDE;
- QUESTION → SELF_ANSWER → RESOLVE;
- THREE_ITEM_ESCALATION;
- CONCRETE → METAPHOR → MORALIZE.

The same family repeated across unrelated scenes and characters may constitute model-prior evidence even when wording changes.

---

## 39. Metaphor and Character Ownership

Metaphor is evaluated through provenance rather than a forbidden-word list.

Relevant evidence can include:

- focal knowledge domain;
- local triggering perception;
- character-specific comparison habits;
- source-conditioned author manifold;
- recent-output novelty.

Generic literary metaphor shared by unrelated characters is a stronger model-prior signal than a single common image.

---

## 40. Character Lexical/Cognitive Policy

Character distinctness is not a phrase quota.

Possible conditional dimensions:

- preferred registers;
- known domains;
- avoided registers;
- compression tendency;
- comparison domains;
- profanity behavior;
- politeness behavior;
- repair behavior;
- attention priorities;
- inference style.

Character-swap verification compares attention, inference, affect, option perception, and rhetorical policy rather than only vocabulary.

---

## 41. Dialogue Model-Prior Firewall

Dialogue verification may inspect:

- over-perfect question answering;
- overly symmetrical turn-taking;
- immediate correct interpretation;
- premature repair;
- excessive explicit emotional disclosure;
- exposition violating common ground;
- every utterance carrying plot/relationship optimization;
- identical register/cognition across speakers.

Valid interactional phenomena include deflection, partial answer, silence, repair, echo, strategic ambiguity, topic shift, face-saving, and grounded misunderstanding.

These are not random irregularities; they must arise from local state.

---

## 42. Open-End Preservation

Scenes do not require mini-resolution.

At scene end the control/evaluation layer may distinguish:

- what resolved;
- what remained active;
- what changed without resolution;
- what remains misunderstood.

`INHABIT`, `INCUBATE`, `RECOVER`, or other low-transformation scenes may legitimately remain open.

Automatic meaningful-final-line behavior is not a default requirement.

---

## 43. Lexical Habit Quarantine

Three levels:

1. **HARD USER BANS** — absolute within authorized scope;
2. **MODEL-HABIT WATCHLIST** — repeated overuse relative to source/manifold and recent output;
3. **SEMANTIC/RHETORICAL FAMILY QUARANTINE** — detects synonym or construction rotation around the same generic function.

Possible state progression:

```text
NORMAL → WATCH → SUPPRESS → TEMP_BAN
```

Model-habit quarantine is reversible when character/source ownership evidence supports the form.

Hard user bans are not reversible by model inference.

---

## 44. Behavior Provenance — Scoped Use

A critical final cross-examination correction:

**Do not require provenance records for every sentence or every stylistic choice.**

That would create a new bureaucratic writing prior and convert prose into checklist compliance.

Behavior provenance activates for:

- repeated suspicious behaviors;
- high-impact rhetorical/paragraph choices;
- contested exceptions to a model-prior warning;
- cross-character/cross-scene recurrent patterns;
- user-banned or high-risk behaviors.

Conceptual record:

```text
BehaviorProvenance
- behavior_family
- owner
- evidence
- recurrence_scope
- confidence
```

Possible owners:

- USER
- SOURCE_AUTHOR
- CHARACTER
- RELATIONSHIP
- SCENE_FUNCTION
- PRESSURE_STATE
- MODEL_DEFAULT
- UNKNOWN

`UNKNOWN` is not automatically failure. Repeated unknown ownership may increase model-prior suspicion.

---

# PART VI — MANDATORY VERIFICATION

## 45. Official Verification Interface

The only supported qualification path is conceptually:

```text
verify_proposal(
    prepared_scene,
    prose,
    proposed_state_delta=None,
    external_observations=()
) -> VerificationRecord
```

The caller cannot provide an authoritative failure list, PASS flag, or executed-check assertion.

PASS is computed only inside this path.

---

## 46. Mandatory Verifier Registry

```text
VerifierDefinition
- check_id
- version
- family
- severity
- execution_mode
- trigger_rule
- required_inputs
- produced_observations
- blocks_pass_when_missing
```

Execution modes:

- DETERMINISTIC
- EVIDENCE_ASSISTED

Core checks always required may include authority, knowledge reachability, hard user bans, basic paragraph integrity, state-delta authority, and commit prerequisites.

Triggered checks are selected by scene risk and recent failures.

Once selected as required, a check is mandatory.

---

## 47. CheckReceipt and PASS Set Logic

```text
CheckReceipt
- check_id
- check_version
- proposal_hash
- prepared_scene_hash
- relevant_state_hash
- execution_status
- verdict
- evidence_refs
- observed_spans
- findings
- deterministic
- confidence
- dependency_receipts
```

PASS requires:

```text
required_checks - executed_valid_checks = ∅
```

If a required check is absent, incomplete, stale, or structurally invalid, qualification is `ASSURANCE_NOT_MET` even when no failure is recorded.

No synthetic evidence identifier may be created for an unexecuted check.

---

## 48. Evidence Classes for Verification

Evidence classes:

- DIRECT_DETERMINISTIC
- STATE_DERIVED
- GROUNDED_EXTERNAL
- MODEL_OBSERVATION
- UNSUPPORTED_ASSERTION

An unsupported boolean cannot suppress a verifier or create PASS.

External semantic evaluators produce evidence, not verdict authority.

---

## 49. Model-Prior Suspicion vs Hard Failure

Another final cross-examination correction:

Not every model-prior suspicion is a hard failure.

The verifier distinguishes:

- **SUSPECT** — pattern evidence exists but ownership/function uncertainty remains;
- **SUPPORTED_FAILURE** — repeated or high-confidence evidence demonstrates unowned model-default behavior violating an active contract;
- **HARD_USER_VIOLATION** — deterministic violation of user ban/authority;
- **ASSURANCE_NOT_MET** — evidence required for a consequential judgment is insufficient or contradictory.

This prevents the firewall from becoming blanket prose censorship.

---

## 50. FailureRecord and Failure Depth

```text
FailureRecord
- failure_id
- family
- root_depth
- affected_spans
- evidence_refs
- repair_permissions
- protected_scope
```

Root depths:

- GROUND
- AUTHORITY
- DISTINCTION
- CONCEPTION
- COGNITION
- INTERACTION
- DISCOURSE
- PARAGRAPH
- SYNTAX
- LEXICON

The same visible symptom may escalate to a deeper root after repeated local repair failure.

---

## 51. Revision Router and RepairPacket

The firewall diagnoses; it does not rewrite prose itself.

```text
RepairPacket
- original_realization_packet_ref
- failing_spans
- root_depth
- failure_family
- allowed_changes
- protected_spans
- protected_events
- protected_voice_features
- required_effect
```

Global `make it more natural` rewrites are not a supported repair mode.

### 51.1 Strategy repetition

Record repair attempts by failure signature and strategy.

The same signature cannot retry the same strategy.

Three distinct failed strategies for one persistent signature trigger structural/assumption escalation rather than a fourth cosmetic repair.

### 51.2 Receipt invalidation

Repairs invalidate every check receipt whose dependency set intersects the modified dimensions.

Stale PASS receipts cannot be reused.

---

# PART VII — VERIFIED TRANSACTIONAL COMMIT

## 52. Typed StateDelta

Arbitrary dictionaries are not valid durable deltas.

```text
StateDelta
├── fact_delta
├── evidence_delta
├── knowledge_delta
├── belief_delta
├── memory_delta
├── self_model_delta
├── relationship_delta
├── affordance_delta
├── world_delta
├── open_loop_delta
├── recurrence_delta
├── reader_delta
├── serial_delta
└── voice_delta
```

Each material transformation includes reason, authority, provenance, evidence, and dependencies as appropriate.

Unknown top-level namespaces fail validation; they are not silently dropped.

---

## 53. Commit Gate

Official conceptual interface:

```text
commit_verified(
    current_state,
    prepared_scene,
    verification_record,
    candidate_state_delta
) -> CommitResult
```

Hard conditions include:

- qualification is PASS;
- proposal hash matches the verification record;
- current state version matches prepared parent version;
- current canonical semantic hash matches prepared parent hash;
- StateDelta validates exact schema;
- every changed namespace is authorized;
- every durable claim has sufficient provenance;
- dependencies remain current;
- no stale verification receipt is used;
- no unknown state namespace exists.

Version equality without hash equality is insufficient.

---

## 54. Canonical Hash

The semantic state hash includes durable narrative state while excluding ephemeral diagnostics, timestamps, caches, and other non-semantic operational metadata.

This allows meaningful stale-state protection without false conflicts from audit bookkeeping.

---

## 55. Self-Contamination Firewall

Generated prose does not automatically mutate durable author identity.

Permitted durable author-model evidence sources:

- supplied source corpus;
- explicit user preference;
- explicit user approval of a durable style decision;
- validated source/compiler update under evidence rules.

Prohibited automatic author-model sources:

- one successful generation;
- verifier rewrite;
- emergency repair;
- model-generated phrase;
- repeated defect merely because the model repeats it.

---

# PART VIII — EXECUTABILITY AND COMPLETION TRUTH

## 56. ExecutionLedger

Every material master concept receives an execution status.

```text
ExecutionLedgerEntry
- concept_id
- spec_section
- epistemic_class
- implementation_status
- module
- entrypoint
- schema_refs
- test_refs
- adversarial_probe_refs
- runtime_callers
- downstream_consumers
- criticality
- claim_boundary
```

Implementation statuses:

- HARD_GATE
- RUNTIME_PRIMITIVE
- SPECIALIST_EXECUTABLE
- VERIFIER_EXECUTABLE
- EVALUATION_ONLY
- EXPERIMENTAL
- DOCUMENTATION_ONLY
- PRIMITIVE_PRESENT_NOT_INTEGRATED

A class or file existing is not sufficient for `EXECUTABLE` status.

Executable status requires, as appropriate:

- schema/interface exists;
- entrypoint exists;
- runtime path reaches it;
- tests exercise the reachable path.

---

## 57. Criticality

Ledger entries are classified:

- RELEASE_BLOCKING
- REQUIRED
- OPTIONAL
- EXPERIMENTAL

Examples of release-blocking contracts:

- NO-ORACLE writer boundary;
- mandatory verification set logic;
- hash-bound transactional commit;
- failed-prose isolation;
- exact StateDelta namespace validation;
- execution-ledger integrity itself.

Experimental creative research does not block structural release merely because it is incomplete, but it cannot be claimed as implemented.

---

## 58. Contract Coverage

Release reports include contract coverage separate from code coverage.

Example categories:

```text
Hard invariants
Runtime primitives
Mandatory verifier families
Sparse specialists
Evaluation protocols
Experimental concepts
```

The runtime must report both:

- overall contract coverage;
- critical/release-blocking contract coverage.

A green test count does not substitute for contract coverage.

---

## 59. ClaimLedger

External release claims are evidence-gated.

```text
ClaimRecord
- claim_id
- claim_text
- required_evidence
- current_evidence_refs
- status
- expiration_condition
```

Statuses:

- SUPPORTED
- PARTIALLY_SUPPORTED
- ASSURANCE_NOT_MET
- REJECTED

Example:

`failed proposals cannot mutate durable state` may become supported by executable transactional tests.

`AI smell is significantly reduced` remains assurance-not-met until controlled live generation and blind evaluation support it.

---

## 60. Fresh Verification Artifacts

Verification artifacts record at least:

- code hash;
- schema hash;
- execution-ledger hash;
- runtime version;
- generation timestamp.

If code/schema/ledger identity changes, the artifact is stale and cannot support a new release claim.

---

# PART IX — ADVERSARIAL VERIFICATION

## 61. Adversarial Families

The test strategy treats bypass resistance as first-class behavior.

Required families include:

### Authority Escape

- prohibited-event injection;
- forged authority;
- unknown specialist/card authority;
- unauthorized state namespace.

### Oracle Leak

- hidden truth leakage;
- correct reader answer leakage;
- objective affordance leakage;
- narrator-mode loss;
- raw state leakage.

### Verification Forgery

- externally supplied empty failures;
- fake PASS;
- fake evidence IDs;
- skipped required checks;
- stale receipts.

### State Mutation

- same-version content mutation;
- stale semantic hash;
- unknown delta namespace;
- post-verification mutation.

### Model-Prior Evasion

- synonym rotation;
- rhetorical paraphrase;
- paragraph newline variants;
- long one-line bypass;
- semantic echo mutation;
- closure paraphrase mutation.

### Creative Collapse

- same-basin paraphrases posing as candidates;
- arbitrary novelty posing as diversity;
- candidate averaging.

### Repair Escape

- local repair modifies protected events;
- repair changes focal knowledge;
- repair smooths protected voice behavior;
- repair reuses stale check receipts.

### Self-Contamination

- generated prose promoted to durable author rule without authority.

---

## 62. Mutation Testing for Model-Prior Checks

A detector must not be considered robust merely because it matches the literal fixture that inspired it.

Tests should mutate lexical realization while preserving the rhetorical/semantic family.

Example contrast family variants:

```text
A가 아니라 B
A 때문은 아니었다. B였다.
처음에는 A라 여겼다. 남은 것은 B였다.
A라고 생각했다. 틀렸다. B였다.
```

Detection boundaries must remain explicit; no universal paraphrase-detection claim is permitted.

---

# PART X — SOURCE AND AUTHOR MODEL

## 63. Source-Dimension Ownership

The existing source split remains:

- **Mad Summer** → attention / local judgment / embodied realization;
- **First Bottle** → character-specific cognitive frame transfer and useful memory/knowledge asymmetry;
- **King of Darkness** → reader hypothesis / evidence / ontology reconstruction;
- **Lover of Flame** → plan / affordance / agency / strategic ecology.

Do not globally average these roles.

No source phrases, signature catchphrases, or source-specific motifs are inserted into the runtime.

---

## 64. Source Style Manifold and Holdout

Stylometric behavior is a verifier/evaluation boundary, not a writer target.

Holdout material should be reserved where feasible before tuning source mechanisms.

Holdout evaluates whether inferred mechanisms generalize to unseen source behavior and whether rare maneuvers were incorrectly promoted.

### 64.1 Mad Summer evidence limitation

The supplied Mad Summer PDFs are image-based. The project has strong visual/manual mechanism-level evidence but does not currently have a reliable full-text corpus suitable for precise Korean function-word/stylometric claims.

Therefore exact Mad Summer stylometric manifold claims remain `ASSURANCE_NOT_MET` unless a reliable text source/extraction path is later established.

---

# PART XI — RELEASE AND LITERARY EVALUATION

## 65. Structural Release vs Literary Validation

### STRUCTURAL_RELEASE

May claim only that specified executable contracts have been implemented and freshly verified.

### LITERARILY_VALIDATED_RELEASE

Requires additional controlled live-generation and blind-evaluation evidence.

Structural PASS does not imply literary superiority.

---

## 66. Stable-Frontier Evaluation

Do not evaluate only best samples.

Track distributions including:

- mean;
- median;
- P10;
- P05;
- variance;
- catastrophic failure rate;
- canon/POV failure;
- model-prior reversion;
- character convergence;
- repair success rate;
- long-horizon drift.

A new runtime is not accepted merely because its best output is better.

---

## 67. Controlled Old-vs-New Comparison

Use identical, recorded conditions where materially possible:

- foundation model identity;
- model configuration hash;
- sampling settings;
- seed set;
- task set;
- source/canon input;
- output budget.

Suggested conditions:

- strong ordinary baseline;
- current v3 runtime;
- v0.2 redesigned runtime.

Blind judges receive task/context and output only, never runtime labels or telemetry.

---

## 68. Blind Human Evaluation Dimensions

Do not ask only `human or AI?`.

Evaluate independently:

- prose formulaicity;
- character ownership;
- explanation pressure;
- lived presence;
- paragraph naturalness;
- surprising-but-grounded conception;
- relationship earnedness;
- reader pull;
- voice individuality.

Keep trade-offs visible instead of collapsing them into one universal score.

---

# PART XII — IMPLEMENTATION DECOMPOSITION

## 69. Required Implementation Subprojects

This redesign is too large to execute safely as one undifferentiated change. It must be implemented as multiple independently reviewable subprojects, each producing working/testable software.

### Subproject A — Integrity Gate Closure

Scope:

- mandatory verifier execution path;
- CheckReceipt and VerificationRecord;
- evidence classes;
- exact PASS set logic;
- semantic state hash;
- typed StateDelta;
- commit gate;
- regression tests for current P0 bypasses.

This subproject is first because all later creative-quality claims depend on it.

### Subproject B — No-Oracle Projection Compiler

Scope:

- ActorView projection;
- narrator-mode preservation;
- positive allow-list RealizationPacket;
- objective/perceived affordance separation;
- raw-state leak prevention;
- concrete specialist artifact transport;
- oracle-leak adversarial suite.

### Subproject C — Prose / Model-Prior Control Plane

Scope:

- structural parser;
- paragraph topology;
- terminal-function analysis;
- semantic echo/abstract restatement;
- affective normalization;
- rhetorical families;
- lexical habit quarantine;
- scoped behavior provenance;
- repair router and receipt invalidation.

### Subproject D — Creative Search Integration

Scope:

- SceneDistinction;
- SearchDecision;
- GenerativeAxiomMap;
- CandidateConcept/Genealogy;
- structural same-basin gate;
- cross-examination;
- winner-dominant synthesis;
- high-assurance path integration into `prepare_scene()`.

### Subproject E — Character / Reader / Interaction Integration

Scope:

- active cognitive set;
- remembered model/self-model gap;
- RelationshipView;
- epistemic action;
- strategic ecology;
- ReaderView activation/retrieval/tractability;
- emergent interaction frame post-generation confirmation;
- scene metabolism integration.

### Subproject F — Executability / Release / Evaluation

Scope:

- ExecutionLedger;
- Contract Coverage;
- ClaimLedger;
- stale verification artifact checks;
- adversarial-family registry;
- release manifest linkage;
- clean-room structural release;
- benchmark protocol scaffolding.

Each subproject requires its own implementation plan and review gate. Later subprojects must not compensate for unresolved release-blocking defects in earlier ones.

---

# PART XIII — FINAL CROSS-EXAMINATION RESULTS

## 70. Resolved Design Tensions

### 70.1 Model-prior control vs prose overregulation

Resolution: model-prior behavior is not globally banned. Suspicion, ownership, recurrence, and scene function are distinguished. Behavior provenance is scoped to suspicious/high-impact cases rather than attached to every sentence.

### 70.2 Emergence vs hidden planning

Resolution: the planner may specify a possible frame shift, but actual emergent interaction is confirmed only from generated action/uptake evidence and becomes durable only after verification/commit.

### 70.3 Sparse verification vs proof-carrying PASS

Resolution: not every verifier runs every scene, but the required set is fixed before qualification. Every selected required verifier must execute validly for PASS.

### 70.4 Human-like imperfection vs fake humanization

Resolution: incomplete memory, misunderstanding, rough rhythm, or irregular interaction must arise from grounded state. Random error insertion is not authorized.

### 70.5 Style fidelity vs source mimicry

Resolution: source mechanisms determine conditional realization priors and verifier boundaries. Source phrases and exact statistical quotas are not writer instructions.

### 70.6 Causal coherence vs lived non-instrumental reality

Resolution: not every detail or scene needs payoff. Focal-owned lived detail and non-transformative scene metabolism remain valid.

### 70.7 Verification strictness vs literary freedom

Resolution: hard authority/state checks are strict. Model-prior quality checks distinguish suspicion from supported failure and do not turn generic stylistic preferences into hard bans.

---

## 71. Explicitly Rejected Designs

Do not implement:

- one giant prompt containing the full architecture;
- raw canonical state sent to the writer;
- blacklist sanitizer as the main no-oracle defense;
- caller-provided PASS/failure authority;
- arbitrary dict StateDelta;
- version-only stale-state checking;
- fixed paragraph lengths or sentence counts;
- one-line paragraph prohibition;
- `high pressure = short sentences`;
- `emotion must be delayed` as universal law;
- `every detail must pay off`;
- `every scene must progress`;
- `repetition is bad`;
- word-frequency targets sent to the writer;
- three candidates counted as creativity without genealogy;
- candidate averaging;
- semantic-distance maximization as creativity;
- random typos/errors for humanization;
- automatic moral/healing closure;
- generated prose self-training into author identity;
- AI-detector score as primary optimization target;
- one universal literary/commercial quality score;
- provenance bureaucracy attached to every sentence;
- firewall-generated full rewrites.

---

## 72. Completion Criteria for the v0.2 Structural Redesign

The structural redesign may be called `STRUCTURALLY_VERIFIED` only when:

1. all release-blocking invariants have executable ledger entries;
2. no official qualification path can bypass required verifier execution;
3. no writer packet can contain unauthorized omniscient/raw state under adversarial probes;
4. narrator mode and focal identity survive projection exactly;
5. state commit requires matching semantic hash and version;
6. unknown StateDelta namespaces fail closed;
7. failed/assurance-not-met prose cannot mutate durable state;
8. model-prior paragraph tests cover multiple newline/topology mutation families;
9. required repair invalidation prevents stale check reuse;
10. ExecutionLedger matches actual reachable code, schemas, and tests;
11. Contract Coverage reports critical and noncritical implementation truth separately;
12. verification artifacts are fresh against code/schema/ledger hashes;
13. final ZIP clean-room tests, validator, adversarial suites, manifest validation, ledger validation, and critical contract coverage all pass;
14. release claims do not exceed the ClaimLedger evidence state.

Literary improvement remains a separate gate requiring controlled generation and blind human evaluation.

---

## 73. Final Design Thesis

The new runtime is not a larger writing prompt and not a growing list of anti-AI rules.

It is a bounded creative cognition architecture in which:

- the planner may know the world, but the writer receives only a legitimate partial world;
- creative search may challenge model and genre defaults, but never user/canon authority;
- character uncertainty, incomplete memory, self-misunderstanding, and interactional emergence are allowed when grounded;
- model-default prose behavior has no automatic authority;
- paragraph, rhetoric, affect, metaphor, dialogue, and closure are evaluated by function and ownership rather than simplistic bans;
- specialist reasoning produces concrete scene artifacts rather than generic writing advice;
- every PASS carries receipts proving the required checks actually ran;
- every durable state mutation is hash-bound, typed, authorized, and provenance-backed;
- every claimed implementation is linked to an executable entrypoint and tests;
- every literary superiority claim remains unmade until controlled external evidence exists.

The governing paradox remains deliberate:

> **Open creative cognition, closed truth boundary.**  
> **Rich planning knowledge, limited realization knowledge.**  
> **Stable synthetic author identity, condition-dependent expression.**  
> **Surprise without arbitrariness.**  
> **Ambiguity without evidence fraud.**  
> **Repetition when owned, not when merely preferred by the model.**  
> **High peak ambition, judged by the stable frontier.**

