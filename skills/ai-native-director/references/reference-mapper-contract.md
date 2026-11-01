# Mapping handoff

Return human-readable tables by default; JSON when the Director requests it. Omit unrelated context. This schema records source binding, not a visual-generation guarantee.

Envelope:
```json
{
  "run_id": "run-id",
  "scene_version": "scene-v1",
  "artifact_id": "plan-v1",
  "stage": "mapping",
  "reviewer": "reference-mapper",
  "execution": "independent",
  "mapping": {
    "status": "PENDING",
    "entities": [{
      "entity_id": "character-1",
      "role": "character",
      "tags": ["@exact-approved-tag"],
      "approval": "APPROVED",
      "approval_evidence": "specific user instruction/source",
      "asset_id": "asset-version-id",
      "inspection": "PENDING",
      "inspection_evidence": [],
      "ownership": "actual anatomical hand/hip/contact",
      "scope": ["shot-id"]
    }],
    "shots": [{"shot_id": "shot-id", "entity_ids": ["character-1"], "tags": ["@exact-approved-tag"], "input_bindings": [], "status": "PENDING"}],
    "conflicts": [],
    "pending": ["asset bytes unavailable"]
  }
}
```

Use execution `independent` only for a distinct worker; `self_review` for a sequential role pass. Entity inspection `VERIFIED` requires actual evidence; source-reported inspection is not this worker's inspection. Exclude provisional entities from active bindings until authorized. Partial reference mapping can be useful while overall status remains PENDING.

For each input binding record the exact entity/asset identity and its tool input role or slot when known. A tag with the wrong asset is a binding failure. Missing bytes do not authorize a fallback asset. Derive each shot's visual inventory from its actual approved frame/source; the global scene register resolves exact identities but is not a per-shot allow-list. Reject stale other-frame/global cast, props, crowd and location variants even when globally valid. Retain actually visible partial/reflection owners and explicitly on-frame crowd. Include offscreen ownership only in separate continuity notes; explicitly requested audio-only speaker/source bindings belong in an audio handoff, never visual Refs/attachments. Do not bind a hidden character/bag merely to state absence. Preserve canonical state for the Director to update after resolving conflicts.

Actual binding entry: `{"entity_id": "character-1", "asset_id": "asset-version-id", "bound": true, "binding_evidence": ["actual tool input manifest/attachment identifier"], "input_role": "identity reference", "input_slot": "supported slot if known"}`. Record actual attached sources in `input_bindings`; keep planned but unattached sources in a separate `proposed_bindings` list. An empty input list is honest when source bytes/tool bindings are unavailable. PASS requires inspected sources and completed bindings for each scoped shot; use NOT_APPLICABLE for a scope with no reference-dependent entities. FAIL requires an identified conflict or failed shot. Do not return an empty PASS register.

Keep story context and the full scene register outside each cell/clip's executable payload. Bind each board cell independently, including the exact existing visible location view and any soft partial shoulder/head owner. For video use the current frame plus only explicitly authorized progression. A strict frame cannot gain another edge figure or scene tag through a composition experiment.
