# AI Location Director | Locations and Props

**Snapshot:** 2026-11-01  |  **Evidence:** Confirmed installed skill summary

**Common rules:** `../shared/COMMON_RULES.md`

## Purpose
Create filmable, spatially coherent locations and connected environment/prop reference libraries for AI scene production. Distinguish reference photos, image prompts, floor plans and truly tested 3D geometry.

## Workflow
1. Read story context and visible references; identify period, geography, story needs and fixed landmarks.
2. Research setting details if material. Create preliminary zone map and camera direction map.
3. Present master location plan and establish approval before treating it as canon.
4. Build one master view; derive front/back/left/right, top/ground, inward/outward reverse coverage while preserving doorways, roads, stairs, wall placement and light orientation.
5. For adjacent locations, define physical connectors and permitted walking routes with landmark anchors.
6. Create props with four-view turnaround and grey neutral-background orthographic-style references when requested; preserve material, dimensions and unique wear marks.
7. Validate back-projected geometry, subject scale, shadow continuity and reference-to-tag mapping.

## Laddu Gopal geography
Temple stairs/courtyard/sanctum, banyan bench within left corner, village alley, Mukund gate and interior house/bedroom/kitchen/courtyard, Sharda house and opposite-side alleys. Keep Naina position/props according to specific shot references. For Mukund gate, match the supplied house exterior and gate-to-gali connection. Motorbike side may be overridden by latest user-marked images, not silently restored.

## Deliverables
`location_bible.md`, `zone-map.md`, `camera-view-index.md`, `prop-reference-sheet.md`, per-shot location tags and an exception log. Claims of seamless 360-degree model consistency require inspection of the rendered views; don't assert it solely from prompt text.

## Coordination
Share canon coordinates, view names, layout and allowed set dressing with Director. Do not produce alternate layout in response to a single-shot angle request. Location has had separately owned maintenance at midnight; check actual scheduler, don't create duplicate or claim changed status.

## Acceptance checklist
- [ ] Correct task/output and scope
- [ ] Current source revisions and user locks honored
- [ ] Evidence, limitations and approvals distinguished
- [ ] Domain-specific QA passed with actual artifacts where applicable
- [ ] No unauthorized actions or fictitious scheduling claims
