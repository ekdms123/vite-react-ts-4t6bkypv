# DJAR-GROUNDED SYNTHETIC CREATIVE COGNITION MASTER v0.1

Date: 2026-08-23
Status: MASTER ARCHITECTURE DESIGN CANDIDATE — NOT YET A CLAIM OF LITERARY SUPERIORITY
Target lineage: Stateful Synthetic Author Runtime v2 RC3 → Grounded Synthetic Creative Cognition Runtime
DJAR basis: v2.1 High-Assurance RootKernel principles
Runtime dependency rule: DJAR is a design/reference kernel; the final writing package must remain standalone.

---

## 0. MISSION

Build a fiction runtime that does not merely imitate a preferred prose surface or suppress obvious LLM mannerisms. The target is a bounded synthetic creative cognition system that:

1. preserves user authority, canon, POV knowledge, provenance, and committed state;
2. models characters, readers, relationships, organizations, and the world as partially informed and dynamically changing;
3. searches multiple genuinely different scene possibilities only when useful;
4. can reframe a poorly chosen creative problem without silently changing user intent;
5. allows psychologically productive contradiction, incomplete memory, ambiguity, and emergent interaction without allowing canon contradiction;
6. realizes prose through a source-grounded synthetic author identity rather than a generic model voice;
7. prevents lexical, rhetorical, paragraph, social, emotional, and scene-conception model priors from silently taking over;
8. verifies with fresh evidence and commits only qualified state changes;
9. optimizes the stable quality frontier, not one spectacular sample;
10. makes no claim stronger than its actual tests and blind evaluations support.

The target is NOT “human-looking AI text.”
The target is NOT detector evasion.
The target is NOT phrase-level imitation of any supplied source.
The target is a coherent new authorial system whose creative decisions are grounded, character-owned, non-generic, and stable over long horizons.

---

## 1. DJAR ROOT CONTRACT AS APPLIED TO FICTION

DJAR v2.1 RootKernel owns only:

- **DISTINCTION** — what must be separated to reason correctly;
- **RELATION** — how grounded distinctions are connected;
- **TRANSFORMATION** — what change follows, with a non-empty reason.

The fiction runtime must keep the following outside the creative root:

- Ground
- Anchors
- Authority
- Gates
- State mutation
- Tool execution
- Recovery
- Budgets
- Verification
- Release/commit

### 1.1 Fiction invariants

1. Creative capability does not grant narrative authority.
2. User locks and hard canon cannot be transformed by the creative search layer.
3. Unsupported creative assumptions remain provisional.
4. Relation confidence cannot exceed supporting Ground.
5. UNKNOWN is a valid state.
6. Character uncertainty is allowed; runtime uncertainty must not be silently converted into fact.
7. In-world evidence is not the same thing as runtime truth.
8. Candidate prose cannot mutate durable state.
9. Failed or assurance-not-met prose cannot become voice/canon evidence.
10. A style hypothesis cannot become an author rule merely because it sounds plausible.
11. Blind comparisons must use identical foundation model/configuration/seed/task conditions.
12. Unmeasured quality dimensions remain unmeasured; they are never fabricated as zero or PASS.

---

## 2. EVIDENCE CLASSES

Every important design rule carries one of these epistemic classes:

### 2.1 USER-AUTHORITATIVE
Explicit preference, prohibition, canon, approved design decision, requested effect.

### 2.2 SOURCE-GROUNDED
Repeated or materially supported by supplied source text/page evidence. Must preserve counterexamples and conditions.

### 2.3 RESEARCH-SUPPORTED
Supported by outside literature or empirical work and compatible with source evidence. It remains a transferable mechanism, not source truth.

### 2.4 DJAR-DERIVED
A runtime/design relation inferred from multiple grounded facts under DJAR. Must remain labeled as derived until tested.

### 2.5 EXPERIMENTAL
Plausible but not yet supported enough for mandatory runtime behavior. May enter candidate experiments, never hard author law.

No lower class silently upgrades itself.

---

## 3. WHAT THE PREVIOUS SYSTEM GOT RIGHT

Preserve:

- source-dimension ownership rather than percentage blending;
- base prose / humor cognition / story architecture separation;
- sparse optional cognition;
- minimal writer packets;
- source-clean generator context;
- durable state outside hidden model memory;
- verifier-only audits separated from writer guidance;
- failed-prose isolation;
- medium independence;
- no universal single quality number;
- no source phrases, signature catchphrases, or motif copying;
- selective retrieval rather than giant history dumps.

The existing synthetic author base remains useful but is reinterpreted as a **realization identity**, not the complete creative brain.

---

## 4. AUTHOR SOURCE RECOMPILATION — UPDATED ROLES

Do not blend sources globally. Give each source a distinct causal role.

### 4.1 MAD SUMMER → ATTENTION / LOCAL JUDGMENT / EMBODIED REALIZATION ENGINE

Primary transfer:

- focal attention selects what is usable, risky, irritating, costly, bodily, spatial, logistical, or immediately actionable;
- judgment and small action frequently precede complete emotional explanation;
- relationship meaning often arises through labor, access, tending, waiting, money, routine, touch, cost, proximity, and boundary change;
- pressure may narrow cognition and syntax, but not by a fixed sentence-length rule;
- aftermath may permit temporary meaning expansion before reality anchors return;
- non-instrumental concrete reality is permitted when it is focal-owned, even if it is not foreshadowing or payoff machinery.

Do NOT reduce to short sentences, vulgarity, body-detail quotas, logistical object sprinkling, or delayed emotion as a universal rule.

### 4.2 FIRST BOTTLE → CHARACTER-SPECIFIC COGNITIVE FRAME ENGINE

Primary transfer:

- humor begins as a character-owned cognitive operation;
- cross-domain frame transfer can create humor when an alien conceptual system is mapped onto an ordinary situation and pursued with internal logic;
- different characters require different frame libraries and inferential habits;
- register drop, banal collision, self-serving reframing, and late turns are outcomes, not mandatory surface gimmicks;
- humor may disappear completely under pressure;
- memory/knowledge asymmetry is a second useful source dimension and must not be collapsed into “humor only.”

### 4.3 KING OF DARKNESS → READER HYPOTHESIS / EVIDENCE / ONTOLOGY ENGINE

Primary transfer:

- maintain multiple plausible reader models rather than a single false answer;
- preserve why earlier interpretations were reasonable;
- distinguish local deductive reveals from ontological/identity/character/causal reveals;
- use retrospective reconstruction so later truth can change the meaning of earlier action without invalidating prior evidence;
- clues are evidence with source/reliability, not automatic truth;
- long-form pull can come from the reader actively updating a problem model.

### 4.4 LOVER OF FLAME → PLAN / AFFORDANCE / AGENCY / STRATEGIC ECOLOGY ENGINE

Primary transfer:

- a shared long arc can change protagonist, tone, local goal, and problem type without losing the global causal line;
- mystery may shift from “who/what?” to “what plan is operating and what options remain?”;
- relationship transformation can change what actions two people can now perform together;
- a major payoff may move several dimensions at once: knowledge, causality, institutions, options, relationship, future horizon;
- organizations and opposing agents must adapt, not wait passively for the protagonist.

---

## 5. MASTER DISTINCTIONS

The runtime must keep these distinctions explicit.

### 5.1 Runtime truth vs diegetic evidence

**RUNTIME TRUTH**
- user authority
- locked canon
- verified committed state
- explicit unknowns

**DIEGETIC EVIDENCE**
- perception
- testimony
- rumor
- document
- memory
- inference
- deception
- fabricated evidence

A story statement “X said Y” can be Runtime Truth while Y remains false or uncertain in-world.

### 5.2 Stored knowledge vs active knowledge vs remembered model vs disclosure

For each actor:

- STORED_KNOWLEDGE — the actor actually learned/knows;
- ACTIVE_KNOWLEDGE — currently accessible/salient under attention and pressure;
- REMEMBERED_MODEL — current reconstructed memory, which may be incomplete or distorted;
- BELIEF — interpreted model derived from reachable evidence;
- SELF_MODEL — what the actor believes about their own motives/traits;
- DISCLOSURE_STATE — what has been said, concealed, implied, denied, or falsely claimed.

The runtime may know all of these. The prose realization layer may receive only what the active focal state requires.

### 5.3 Objective affordances vs perceived affordances

- OBJECTIVE_AFFORDANCE — what the world/body/social system actually permits;
- PERCEIVED_AFFORDANCE — what the actor thinks is possible;
- RELATIONAL_PERMISSION — what this relationship currently permits without rupture;
- INSTITUTIONAL_PERMISSION — what role/status/law permits;
- COST/RISK — what makes an available option locally unacceptable.

Character action follows the perceived field, not omniscient optimality.

### 5.4 Canon contradiction vs productive contradiction

- CANON_CONTRADICTION → hard failure;
- KNOWLEDGE_CONTRADICTION → may be actor-scoped;
- BELIEF_CONTRADICTION → psychologically possible;
- SELF-MODEL_GAP → valuable;
- GOAL_CONFLICT → scene engine;
- VALUE_CONFLICT → cost generator;
- RELATIONSHIP_PARADOX → human relation resource;
- READER_MODEL_COMPETITION → mystery resource;
- TEMPORAL_CHANGE → may only appear contradictory if state changed;
- VOICE_VARIATION → must distinguish pressure-conditioned variation from generic drift.

### 5.5 Functional repetition vs model formula

Repetition is not automatically a defect.

Preserve repetition when it is owned by:

- a character habit;
- a relationship ritual;
- repair/echo;
- callback;
- refrain;
- pressure or panic;
- deliberate emphasis;
- social mimicry/accommodation;
- recurrence whose meaning changes.

Flag repetition when the same lexical/semantic/rhetorical skeleton recurs across unrelated contexts because the model prefers it.

---

## 6. CONTROLLED INSTABILITY — TOP-LEVEL CREATIVE PRINCIPLE

The runtime must regulate, not maximize, creative divergence.

Too little instability:
- first-answer convergence;
- genre cliché;
- candidate homogeneity;
- model-prior default;
- premature interpretation;
- predictable relationship/reveal patterns.

Too much instability:
- arbitrary novelty;
- character betrayal;
- broken causality;
- excessive surprise;
- style thrashing;
- rule-breaking without authority.

### 6.1 Creative Entropy Regulator

If candidates are too similar:
- increase search distance;
- change a currently unlocked assumption;
- use REFRAME or TRANSFORM.

If candidates are arbitrary or weakly grounded:
- reduce search distance;
- strengthen active constraints;
- return to EXPLORE or COMBINE.

If a strong candidate is found:
- stop divergence;
- exploit/realize;
- do not continue novelty generation for its own sake.

---

## 7. CREATIVE SEARCH CONTROLLER

The writer must not begin with prose by default for consequential scenes.

Search modes:

### 7.1 COMBINE
Recombine existing characters, objects, memories, goals, places, rules, relationships, and constraints in a new but grounded relation.

### 7.2 EXPLORE
Search different possibilities within the current conceptual/causal rules.

### 7.3 REFRAME
Question whether the initially defined creative problem is the most useful distinction.

Example:
“how do they reconcile?”
→ “why do they continue sharing space although neither wants reconciliation?”

A reframe is provisional and may not override required user events.

### 7.4 TRANSFORM
Change one or more unlocked assumptions/rules of the creative problem. It cannot touch hard anchors.

### 7.5 Search authorization

Ordinary scenes may use direct realization or one lightweight search pass.
Use high-assurance search only when triggered by:

- consequential decision;
- first major character impression;
- major relationship phase change;
- major reveal;
- climax;
- repeated genericity failure;
- high-cost canon implications;
- same-basin candidate collapse;
- user requests for unusual/high-peak conception.

---

## 8. GENERATIVE AXIOM MAP

Before high-assurance search, identify the assumptions that make the obvious scene obvious.

Each assumption is tagged:

- HARD_ANCHOR — not transformable;
- SOFT_CANON_CONSTRAINT — transformable only if state/user permits;
- CHARACTER_ASSUMPTION — may be wrong in-world;
- READER_ASSUMPTION — may be exploited;
- GENRE_DEFAULT — should not become canon automatically;
- MODEL_DEFAULT — candidate for disruption;
- FREE_VARIABLE — safe creative transformation target.

Creative transformation operates only on permitted classes.

---

## 9. CANDIDATE SANDBOX AND GENEALOGY

High-assurance scene conception produces independent candidates. Sibling candidates must not see each other before cross-examination.

Each candidate records structural metadata only:

- candidate_id
- search_mode
- changed_assumption_ids
- causal premise
- focal interpretation
- key knowledge asymmetry
- option/affordance change
- relationship implication
- reader-model effect
- creative debts created
- key unknowns

Do not store hidden chain-of-thought.

### 9.1 Same-basin rejection

A/B/C are not genuinely different if they vary only in wording, emotional intensity, or cosmetic action.
At least one major axis should differ when high-divergence search is requested:

- causal premise
- goal structure
- knowledge asymmetry
- spatial solution
- relationship permission
- perceived affordance
- interaction frame
- focal interpretation
- reader hypothesis effect

### 9.2 Winner-dominant synthesis

Do not average candidates.
Select one dominant causal conception.
Other candidates may contribute only a bounded missing constraint, evidence item, or local improvement that does not erase the winner's identity.

---

## 10. PROBLEM DISCOVERY LOOP

A candidate may reveal that the initial Scene Distinction is weak or misframed.

Procedure:

1. candidate identifies a better problem framing;
2. create PROVISIONAL_REDISTINCTION;
3. compare against user request, required events, canon, and locks;
4. if compatible, re-run search on the new framing;
5. if incompatible, retain original framing and use the insight only locally;
6. never silently redefine the user's task.

---

## 11. CHARACTER COGNITION MODEL

For focal and materially active agents track only grounded/relevant fields:

- stored knowledge
- active knowledge
- remembered model
- beliefs
- self-model
- active goals
- suppressed/latent goals
- risk bias
- competence signature
- blind spots
- current body state
- affective residue
- perceived affordances
- social/relationship permissions
- current strategy

### 11.1 Local Rationality

A character choice should be intelligible from reachable evidence, biases, priorities, body state, competence, risk model, and perceived options — not from author omniscience.

### 11.2 Conditional Personality Policy

Traits are not static action templates.
Represent behavior tendencies as conditional policies:

context/pressure/relationship state → likely attention/judgment/action tendencies.

### 11.3 Self-Model Gap

Keep separate:

- declared motive;
- believed motive;
- behavior policy inferred from repeated action.

Do not let the narrator automatically resolve the discrepancy.

### 11.4 Affective Hysteresis

Current response depends on prior affective/body state and interpretation history. Emotion does not reset at scene boundaries.

### 11.5 Habituation / Sensitization

Repeated event types may become less reactive or more reactive depending on character history. No universal repetition curve.

---

## 12. RELATIONSHIP MODEL

A relationship is not one intimacy score.

Track evidence-backed dimensions when relevant:

- access
- physical permission
- emotional disclosure
- labor/care
- waiting
- routine
- obligation
- debt
- trust
- status/power
- taboo
- expected repair behavior
- common ground
- willingness to incur cost
- distance/proximity

### 12.1 Relational Permission Topology

A relationship transformation is often a change in what actions are now possible/acceptable between the actors.

### 12.2 Uptake

The social meaning of an action or utterance is not always fully fixed when produced. The other actor's uptake can confirm, reject, reinterpret, or transform its meaning.

---

## 13. EMERGENT INTERACTION FRAME

Scene plans do not fully determine interaction.

Actors enter with goals and strategies, but action/response may create a new interaction frame:

F0 current frame
→ A move
→ B uptake/rejection/reframe
→ provisional F1
→ F1 constrains subsequent options

Possible emergent frames include:

- interrogation → bargaining
- conflict → ritualized teasing
- rescue → debt negotiation
- avoidance → mutual surveillance
- performance → confession

The emergent frame remains provisional until the scene evidence supports it.

---

## 14. STRATEGIC ECOLOGY

Material opposing agents and organizations should not remain static obstacles.

Relevant strategic entities may track:

- objectives
- resources
- beliefs
- knowledge
- model of other agents' knowledge
- current plan
- perceived threats
- risk tolerance
- adaptation state

### 14.1 Epistemic Action

Actions can be performed to learn, not only to achieve a direct external goal.
Examples:

- ask a question whose answer is partly known;
- tell a small lie to observe reaction;
- expose a controlled vulnerability;
- delay to see who follows;
- test a boundary;
- touch/move an object to observe another actor's response.

Epistemic action must remain locally rational and causally consequential enough to justify inclusion.

---

## 15. READER MODEL

The reader is not omniscient and not a single scalar engagement score.

Track only scene-relevant:

- active hypotheses
- latent/suppressed hypotheses
- evidence supporting each
- confidence bands (not fake precision)
- active question types
- suspense states
- curiosity gaps
- anticipated outcomes
- remembered/retrievable clues
- current confusion/tractability risk
- dominant engagement route

### 15.1 Reader Hypothesis Ecology

Multiple plausible models may coexist. The goal is not always to hide the answer; it is to keep alternative models explanatory enough to remain live until new evidence differentiates them.

### 15.2 Suspense / Curiosity / Surprise Router

- curiosity: unresolved past/present explanatory gap;
- suspense: uncertain future outcome;
- surprise: current model violated and must be revised.

These require different information structures.

### 15.3 Hypothesis Activation

A clue/model can exist in long-term reader state without being currently active. Payoff fairness must consider whether old evidence was reasonably reactivated before it became necessary.

### 15.4 Reader Retrieval Support

Prefer current-scene cues that reactivate older information over exposition recap when possible.

### 15.5 Coping Potential / Tractability

Do not maximize uncertainty. A useful mystery usually offers enough structure that the reader can update models. “Impossible to infer because nothing was provided” is not productive difficulty.

### 15.6 Evidence Gain Without Answer Gain

A scene can create epistemic progress by changing relative plausibility of hypotheses even if no final answer is revealed.

---

## 16. CAUSAL / OPTION MODEL

Track important transformations as topology rather than flat labels.

Possible deltas:

- world fact
- actor knowledge
- actor belief
- reader hypothesis
- objective affordance
- perceived affordance
- relationship permission
- strategy
- institution/resource
- obligation/debt
- open loop status
- recurrence meaning

### 16.1 Causal Centrality

Events differ in structural importance. A causal hub affects several later actions/interpretations and deserves greater state attention than decorative activity.

### 16.2 Option Topology + Irreversibility

Consequential events often matter because they open/close/reprice future options. A major choice should usually have some durable option effect, though not every scene needs one.

### 16.3 Creative Debt Ledger

Novel choices create obligations:

- new setup → causal/world debt;
- major emotional escalation → consequence debt;
- clue → epistemic debt;
- relationship permission jump → evidence/continuity debt;
- motif emphasis → recurrence/payoff expectation.

Debt is not always “must pay off as a twist.” It means the runtime must remember the expectation created.

---

## 17. SCENE METABOLISM

Do not enforce “every scene must progress.”

A scene may primarily:

- TRANSFORM — materially change state;
- CONSOLIDATE — stabilize a recent change;
- INHABIT — let reader/characters live inside a current state;
- RECOVER — process bodily/affective aftermath;
- CALIBRATE — establish a baseline, person, place, or rule;
- INCUBATE — maintain unresolved pressure without immediate transformation;
- RELEASE — deliberately reduce load before the next high-pressure movement.

This is verifier vocabulary, not a mandatory writer taxonomy.

### 17.1 Update-Density Pacing

Pacing is not reducible to sentence length or action count. Consider how often and how strongly the reader/character situation model must update.

---

## 18. NON-INSTRUMENTAL REALITY ALLOWANCE

Not every detail must be payoff, symbolism, or causal machinery.

A concrete detail is allowed when it is plausibly selected by focal attention and contributes to lived reality, even if it does not produce a discrete state delta.

Reject:
- random “realism sprinkling”;
- generic sensory decoration;
- symbolic overreading;
- object quota behavior.

---

## 19. CAUSAL OVERFITTING FIREWALL

Do not convert every repeated object, weather condition, habit, or phrase into planned foreshadowing.

### 19.1 Emergent Motif Promotion

A recurrence becomes a motif/meaningful recurrence only when repeated appearances plus changed context produce an actual semantic relation. Promotion is evidence-based and reversible until committed.

---

## 20. AUTHOR STYLE MANIFOLD

Do not define style as one averaged point.

Model condition-dependent regions such as:

- ordinary domestic baseline
- dialogue-heavy exchange
- humor
- embarrassment
- acute pressure
- bodily pain
- aftermath
- memory
- emotional integration/high point
- procedural/problem-solving scene
- reveal

The writer receives only scene-relevant realization priors.

Stylometry is a verifier boundary, not an instruction target.

---

## 21. NO-ORACLE REALIZATION PRINCIPLE

The planning system may know more than the focal character. The prose writer should not.

Writer packet includes only:

- current scene contract;
- focal identity/mode;
- current reachable knowledge and relevant unknowns;
- active body/affect/goal state;
- relevant world/spatial facts;
- relevant relationship permissions;
- required/forbidden events;
- selected scene-specific cognition artifacts;
- minimal style manifold prior;
- previous verified local continuity when necessary.

Never send:

- full source analyses;
- full card library;
- hidden long history;
- verifier labels;
- model-prior blacklist explanation;
- rejected candidate prose;
- audit diagnostics;
- unrelated open loops;
- omniscient truth that focal realization cannot use.

---

## 22. PROSE REALIZATION ORDER

Default realization logic:

1. what is currently accessible to focal attention?
2. what does the focal mind judge as usable/risky/costly/strange?
3. what action, hesitation, speech, or attention shift follows?
4. what does another actor/world do in response?
5. does that uptake alter the interaction frame?
6. what emotional/relational meaning becomes available now — if any?
7. what remains unnamed or unresolved?

This is a flexible causal ordering, not a sentence template.

---

## 23. PARAGRAPH TOPOLOGY

Do NOT impose fixed sentence counts or rhythmic recipes.

Paragraph boundaries may be justified by:

- attention-chain break;
- causal beat change;
- speaker/interaction ownership shift;
- temporal discontinuity;
- spatial discontinuity;
- decision point;
- information regime change;
- pressure/recovery boundary;
- deliberate isolated line whose eventfulness warrants isolation.

Do not automatically create dramatic one-line staircases.
Do not force every paragraph into claim → explanation → summary.

---

## 24. MODEL-PRIOR FIREWALL — MULTI-LEVEL

AI smell is treated as an upstream-to-surface problem.

### 24.1 Conception Prior Firewall

Detect:

- cliché scene resolution;
- automatic reconciliation;
- predictable rescue/confession patterns;
- stereotype role defaults;
- standard “twist” insertion;
- empty escalation;
- every scene becoming progress/cliffhanger.

### 24.2 Cognition Prior Firewall

Detect:

- character knows too much;
- character remembers exactly everything;
- character instantly understands own motive;
- globally rational author-optimal choice;
- identical cognitive style across characters;
- model moral judgment replacing character ethics;
- immediate emotional normalization.

### 24.3 Discourse Prior Firewall

Detect:

- semantic echo/re-explanation;
- automatic abstraction after concrete evidence;
- closure stacking;
- formulaic contrast structures;
- repeated rhetorical skeletons across unrelated scenes;
- uniform paragraph purpose/length;
- everything connected too neatly;
- over-coherent transition glue.

### 24.4 Surface Prior Firewall

Detect source-relative overuse of:

- lexical habits;
- semantic synonym clusters used for the same generic function;
- sentence-openers;
- function-word patterns;
- punctuation habits;
- syntactic skeletons;
- generic affect/body vocabulary;
- generic “literary” metaphor behavior.

### 24.5 Character/Source Ownership Exception

A repeated form is not rejected when evidence shows it belongs to a character, relationship ritual, scene pressure pattern, or the synthetic author's legitimate manifold.

---

## 25. LEXICAL HABIT QUARANTINE

Three levels:

1. HARD USER BANS — absolute within authorized scope.
2. MODEL-HABIT WATCHLIST — dynamically observed overuse relative to source/manifold and recent output.
3. SEMANTIC/RHETORICAL FAMILY QUARANTINE — activates when the model simply substitutes synonyms or equivalent constructions.

Quarantine is adaptive and local. It must not globally sterilize legitimate language.

---

## 26. POSITIVE / MORAL NORMALIZATION FIREWALL

Detect automatic model tendencies such as:

- healing/acceptance closure not earned by scene evidence;
- “it was enough” type emotional settlement;
- moral lesson insertion;
- narrator correction of flawed characters;
- automatic empathy/reconciliation;
- making every conflict balanced and reasonable;
- social-role stereotype completion.

This layer does not weaken platform safety or user authority. It separates fictional character/narrator ethics from assistant-default moral smoothing.

---

## 27. REVISION ROUTER

Do not “polish everything.”

Map failure depth to repair scope:

- lexical failure → local lexical repair;
- semantic echo → local discourse repair;
- rhetorical formula recurrence → restructure local paragraph/beat;
- character-generic cognition → return to character model;
- emotional normalization → return to affect/self-model layer;
- scene cliché → return to creative search;
- evidence/fairness failure → reader/evidence model;
- canon/knowledge failure → state/ground repair;
- repeated same failure → change strategy, not adjectives.

Preserve unaffected approved text/structure when possible.

### 27.1 Revision Scar Preservation

Do not automatically smooth purposeful asymmetry, abruptness, awkward character-owned phrasing, silence, or pressure fragmentation merely because a generic style model prefers fluency.

---

## 28. DJAR FAILURE MODEL FOR WRITING

Base classes:

- F1 GROUND — missing/weak/conflicting evidence;
- F2 ANCHOR — canon/user/POV/style authority violation;
- F3 DISTINCTION — wrong scene/problem/contradiction class;
- F4 RELATION — wrong causal, epistemic, relationship, or style relation;
- F5 TRANSFORMATION — unjustified state/creative change;
- F6 GATE — verification/release/commit failure.

Recovery ladder:

1. Local Repair
2. Relation Repair
3. Distinction Rescan
4. Ground Refresh
5. Anchor Reload
6. Strategy Transformation
7. Human/External Escalation

The same failure signature cannot retry the same strategy. Three distinct failed strategies for one signature indicate structural/assumption failure.

UNKNOWN alone does not create a failure record.

---

## 29. VERIFIED TRANSACTIONAL COMMIT

Candidate output produces a candidate delta only.

Commit requires:

- current parent state hash/version;
- executed required checks;
- sufficient evidence;
- no unresolved critical unknown;
- no hard authority violation;
- no unsupported state claim;
- PASS qualification.

FAIL / ASSURANCE_NOT_MET:

- may retain diagnostic candidate delta;
- committed delta = empty;
- cannot update voice/canon/relationship/reader/world durable state;
- cannot become style training evidence.

---

## 30. AUTHOR-MODEL SELF-CONTAMINATION FIREWALL

Generated prose does not automatically teach the author model.

Valid author-model update sources:

- supplied source corpus;
- explicit user preference;
- explicit user approval of a new durable style decision;
- validated cross-source mechanism update under the compiler's evidence rules.

Invalid automatic update sources:

- one successful generation;
- verifier rewrite;
- emergency repair;
- model-generated phrase;
- accidental stylistic defect;
- repeated output merely because the model kept doing it.

---

## 31. HOLDOUT AND ANTI-OVERFIT STRATEGY

Source analysis must reserve unseen material where feasible.

Use holdout to test:

- whether inferred mechanisms explain unseen source behavior;
- whether conditional exceptions predict source mode changes;
- whether stylometric verifier boundaries generalize;
- whether rare maneuvers were incorrectly promoted to base rules.

Do not tune against holdout after every failure without reclassifying it as training evidence.

---

## 32. HIGH-ASSURANCE CREATIVE COGNITION

For selected high-risk/high-value scenes, adapt DJAR v2.1 high-assurance structure:

1. Preflight structural framing
2. Independent candidate A
3. Independent candidate B
4. Independent candidate C
5. Cross-examination
6. Ground/structure verification
7. Winner-dominant synthesis
8. Qualification

Release only if:

- qualification record is structurally valid;
- required creative/authority checks ran;
- no critical unknown blocks the chosen transformation;
- no unsupported canon/state claim remains;
- candidate is meaningfully distinct when high-divergence was required;
- confidence crosses the internal admission threshold configured for this path.

The internal threshold is not an external quality score.

---

## 33. VERIFIER FAMILIES

### 33.1 Hard integrity verifiers

- user/canon contract
- POV/knowledge reachability
- provenance/confidence
- state immutability/stale parent
- required/forbidden event
- card/intelligence authority
- commit integrity

### 33.2 Creative-structure verifiers

- same-basin candidate collapse
- arbitrary novelty
- causal legibility
- option/affordance consequences
- reader evidence fairness
- relationship permission continuity
- scene-metabolism validity
- creative debt explosion
- strategic-agent passivity when material

### 33.3 Character verifiers

- character-swap risk
- cognition convergence
- self-model overresolution
- impossible knowledge/memory activation
- local rationality
- affective reset/drift

### 33.4 Model-prior verifiers

- lexical/semantic overuse
- rhetorical skeleton recurrence
- semantic echo
- paragraph regularization
- automatic abstraction
- positive/moral normalization
- stereotype/social-role prior
- generic metaphor
- closure stacking
- excess coherence

### 33.5 Source-manifold verifiers

- focal attention fidelity
- condition-appropriate voice region
- function-word/punctuation/syntax drift at corpus level
- source residue/copy risk
- rare-maneuver overpromotion
- long-horizon voice stability

Verifier vocabulary remains out of writer context.

---

## 34. STABLE FRONTIER EVALUATION

Do not evaluate only peak output.

Track distributions:

- mean
- median
- P10
- P05
- variance
- task/contract success
- recovery rate
- cost
- latency
- goal drift
- unsupported claims
- catastrophic failures
- canon/POV failures
- model-prior reversion
- character convergence
- long-horizon drift

A change is not accepted merely because its best sample is better.

---

## 35. VALID OLD-vs-NEW COMPARISON

Conditions should include at least:

- Bare/standard model
- Strong prompt baseline if useful
- current RC3
- new master runtime

For valid comparison use identical:

- foundation model id
- model configuration hash
- seeds
- task set
- source/canon input
- output budget where materially relevant

Blind judges receive task + output only, not condition labels or telemetry.

### 35.1 Human evaluation dimensions

Do not ask only “human or AI?”

Ask independently:

- Which would you keep reading?
- Which character seems to think in a more individual way?
- Which is less explanatory but still clear enough?
- Which is more surprising without becoming arbitrary?
- Which relationship change feels earned?
- Which prose feels less formulaic?
- Which scene has stronger lived presence?
- Which reveal/problem update is more satisfying?

---

## 36. CORE vs SPECIALIST vs VERIFIER-ONLY COGNITION

Do not create 50 always-on cards.

### 36.1 Core state/model primitives

Always available as runtime concepts, not necessarily writer guidance:

- Ground / Unknown / Provenance
- focal attention
- stored/active knowledge
- belief/self-model
- active goals
- objective/perceived affordance
- relationship permission
- body/affect residue
- reader hypotheses/activation
- causal/option state
- style manifold region

### 36.2 Specialist procedures — sparse

Examples:

- major reveal accounting
- mystery evidence differentiation
- frame-transfer humor
- recurrence recoding
- high-pressure cognition
- epistemic action design
- strategic ecology
- interaction-frame emergence
- candidate basin escape
- problem reframe
- payoff multigain
- retrospective causal reconstruction

### 36.3 Verifier-only procedures

Examples:

- character swap
- reader ensemble
- alternative-model falsification
- scene removal / prose removal value
- model-prior audit
- closure audit
- formulaic rhetoric audit
- stereotype prior audit
- long-horizon stable frontier
- source holdout evaluation

---

## 37. MINIMUM SCENE PREPARATION FLOW

For ordinary scenes:

`SceneContract`
→ hydrate relevant canonical state
→ create grounded scene distinctions
→ active cognitive set
→ select minimal specialist cognition if justified
→ compile writer packet

For high-assurance scenes:

`SceneContract`
→ Ground / Anchors / Unknowns
→ character/world/reader partial models
→ generative axiom map
→ creative search controller
→ independent candidate sandbox
→ cross-examination
→ winner-dominant synthesis
→ specialist cognition
→ writer packet

---

## 38. FULL EXECUTION FLOW

```text
USER / CANON AUTHORITY
        ↓
GROUND + UNKNOWN + CREATIVE FREEDOM MAP
        ↓
CANONICAL WORLD / PROVENANCE / OBJECTIVE AFFORDANCES
        ↓
CHARACTER PARTIAL WORLDS
knowledge / activation / memory / belief / self-model /
goals / body / affect / perceived affordances
        ↓
READER MODEL
hypotheses / activation / gaps / predictions / tractability
        ↓
CREATIVE SEARCH CONTROLLER
COMBINE / EXPLORE / REFRAME / TRANSFORM
        ↓
INDEPENDENT CANDIDATE SANDBOX
        ↓
DJAR CROSS-EXAMINATION
        ↓
WINNER-DOMINANT SYNTHESIS
        ↓
EMERGENT INTERACTION + CAUSAL / OPTION MODEL
        ↓
SPARSE SPECIALIST COGNITION
        ↓
MINIMAL NO-ORACLE WRITER PACKET
        ↓
SOURCE-CONDITIONED PROSE REALIZATION
        ↓
MULTI-LEVEL MODEL-PRIOR FIREWALL
        ↓
INDEPENDENT VERIFICATION
PASS / FAIL / ASSURANCE_NOT_MET
        ↓
TRANSACTIONAL VERIFIED COMMIT
        ↓
CHECKPOINT / CONTEXT GC / NEXT SCENE
```

---

## 39. REQUIRED CHANGES TO THE PREVIOUS HARDENING SPEC

Preserve all 69 confirmed defects as implementation targets, but amend the creative-quality portions:

1. Replace “practical/logistical detail only when causally/emotionally functional” with “focal-owned and scene-legible; causal/emotional function is valuable but not mandatory.”
2. Treat paragraph topology as attention/interaction/causal continuity rather than fixed hard shapes.
3. Add active knowledge / remembered model / disclosure state.
4. Add runtime truth vs diegetic evidence separation.
5. Add objective vs perceived affordances.
6. Add contradiction taxonomy.
7. Add scene metabolism so no-delta scenes are not automatically false progress/failure.
8. Add functional repetition exception to AI-prior auditing.
9. Add self-model gap and affective hysteresis.
10. Add strategic ecology and epistemic action.
11. Add reader hypothesis activation/retrieval/tractability.
12. Add candidate genealogy and same-basin gate.
13. Add problem rediscovery/reframe path.
14. Add winner-dominant synthesis.
15. Add model-prior firewalls at conception/cognition/discourse/surface, not surface only.
16. Add self-contamination firewall.
17. Add holdout validation as a real test, not only a manifest field.
18. Add stable-frontier and blind human comparison protocol for literary claims.

---

## 40. EXPLICITLY REJECTED DESIGNS

Do NOT implement:

- one giant universal prompt containing every theory;
- 50+ always-on intelligence cards;
- fixed percentages for source authors;
- source phrase imitation;
- word-frequency targets sent to the writer;
- fixed paragraph length or sentence rhythm quotas;
- “high pressure means short sentences” as a universal rule;
- “emotion must always be delayed” as a universal rule;
- “every detail must pay off”;
- “every scene must transform state”;
- “repetition is bad”;
- “more semantic distance = more creativity”;
- “three candidates = creativity” without genealogy;
- average/blended synthesis of conflicting candidates;
- automatic motif table from repeated objects;
- generic humanization via errors, typos, random irregularity;
- automatic positive healing or moral closure;
- generated prose automatically learning itself into the author model;
- AI-detector score as the optimization target;
- a single literary/commercial quality score.

---

## 41. IMPLEMENTATION ORDER

### Phase 0 — Freeze evidence and baselines

- preserve original ZIP immutable;
- record exact hashes;
- fresh RC3 baseline tests/validator;
- fresh DJAR v2.1 self-validation;
- reserve source holdout segments before using them for tuning.

### Phase 1 — Integrity / 69 hardening defects

Implement Ground, typed SceneContract, canonical state, authority, ranked sparse selection, schema enforcement, immutable state, qualified verification, transactional commit, release integrity.

### Phase 2 — Epistemic state expansion

Add:

- runtime truth vs diegetic evidence;
- knowledge_by_actor;
- active knowledge;
- remembered model;
- self-model;
- disclosure;
- objective/perceived affordances;
- contradiction taxonomy.

### Phase 3 — Source recompilation

Rebuild source-grounded author models from the four supplied works with:

- independent evidence matrices;
- counterexamples;
- condition-sensitive rules;
- negative evidence;
- rare maneuver classification;
- holdout validation.

### Phase 4 — Creative search / candidates

Implement:

- generative axiom map;
- COMBINE/EXPLORE/REFRAME/TRANSFORM;
- candidate genealogy;
- same-basin gate;
- winner-dominant synthesis;
- high-assurance path for triggered scenes.

### Phase 5 — Character / reader / interaction runtime

Implement:

- local rationality;
- goals/suppression;
- affective hysteresis;
- relationship permission;
- reader hypothesis ecology/activation;
- emergent interaction frame;
- strategic ecology;
- epistemic action;
- scene metabolism.

### Phase 6 — Realization / AI-prior firewall

Implement:

- no-oracle writer packet;
- source style manifold;
- paragraph topology;
- functional repetition;
- lexical/semantic/rhetorical quarantine;
- positive/moral normalization firewall;
- social-role prior audit;
- revision router.

### Phase 7 — Verification and evaluation

- regression tests for every confirmed defect;
- adversarial creative tests;
- holdout source prediction tests;
- long-horizon generation tests;
- old-vs-new controlled generation;
- blind human evaluation;
- stable frontier report;
- final clean-room release verification.

---

## 42. ACCEPTANCE GATES

A structural release may be called complete only when:

1. all 69 known integrity defects are resolved or explicitly non-implemented with reason;
2. new state distinctions have executable schema and tests;
3. no candidate/failed prose can mutate durable state;
4. writer packets cannot receive omniscient or unrelated state outside authorization;
5. same-basin candidate collapse is detected in controlled cases;
6. functional repetition is preserved while cross-context model formula is detectable;
7. source holdout testing exists and is not contaminated by training use;
8. model-prior firewall tests cover lexical, semantic, rhetorical, paragraph, social, and emotional normalization patterns;
9. clean-room ZIP passes tests, validator, manifest verification, and adversarial probes.

Literary superiority may be claimed only if controlled external evaluation supports it.

---

## 43. OPEN / ASSURANCE-NOT-MET ITEMS

Do not prematurely close these:

1. exact threshold for candidate same-basin distance;
2. best compact representation of reader hypotheses without fake probabilities;
3. how much reader state should persist across very long works;
4. exact source-manifold metrics for Korean prose, especially image-PDF source material;
5. whether active-memory distortion should be generated or only modeled when story evidence requires it;
6. how aggressively social-role prior auditing should operate without manufacturing anti-stereotype inversions;
7. whether emergent interaction frames improve prose under the same foundation model;
8. cost/latency break-even point for high-assurance creative search;
9. how much specialist cognition can be packed before realization quality declines;
10. actual human preference and long-horizon stability gains.

These require experiment, not assertion.

---

## 44. FINAL DESIGN THESIS

The earlier runtime was strongest at **preventing bad writing decisions after a scene problem had already been chosen**.

The new runtime must add three missing powers:

1. **partial cognition** — characters/readers/agents do not possess the system's total truth;
2. **creative search** — the system can escape the first obvious solution without becoming arbitrary;
3. **emergence** — interactions and consequences may create new locally grounded structures that were not fully specified in advance.

The governing paradox is deliberate:

> **Open creative cognition, closed truth boundary.**
> **Limited realization knowledge, rich planning knowledge.**
> **Stable author identity, condition-dependent expression.**
> **Causal coherence, room for non-instrumental life.**
> **Surprise, but not arbitrariness.**
> **Ambiguity, but not evidence fraud.**
> **Repetition, but only when owned.**
> **High peak ambition, evaluated by the stable frontier.**

This architecture is the integration point for the approved integrity hardening, source re-analysis, creative cognition research, AI-prior suppression, and future implementation.
