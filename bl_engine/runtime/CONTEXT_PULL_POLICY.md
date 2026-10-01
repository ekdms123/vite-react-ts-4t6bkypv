# Pull-based Context Policy

Default writer context:

1. current event / requested scene
2. current canonical narrative state relevant to the scene
3. current voice checkpoint
4. previous verified scene delta
5. active relevant open loops and recurrences
6. current serial pressure dimensions that can change a choice
7. optional cognition artifact only if routed
8. compact `author_intelligence` payloads only for cards selected by current evidence

Author Intelligence manifests never enter writer context. Each selected card may pull only fields declared in its context requirements; the writer sees only the compiled `id + guidance` payload.

Do not send full source analyses, full card manifests, source excerpts, full history, rejected prose, verifier diagnostics, trigger/suppression metadata, failure history, or unrelated world state. Pull older history only when a current decision, recurrence, reveal, promise, knowledge boundary, or selected intelligence card explicitly requires it.
