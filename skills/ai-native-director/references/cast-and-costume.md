# Cast identity and costume reference sheets

## Contents
- Choose the scope
- Separate identity, look and scene state
- Develop the cast and outfit
- Design readable reference sheets
- Generate or revise from approved sources
- Compile usable prompts
- Inspect and repair
- Research basis and limits

## Choose the scope

Apply this branch to cast design, character sheets, costume/look sheets, turnarounds and relevant repairs. Use existing approved sources for micro-edits; do not restart casting, load the entire screenplay or regenerate a full sheet for a colour, age or missing-accessory correction.

| Request | Work needed |
|---|---|
| Costume colour/accessory repair | Inspect the selected sheet, preserve identity and all unrequested garment/state fields; repair affected cells |
| New look for an existing character | Resolve identity source, outfit brief, current look and intended scope; keep the old look available |
| Character identity sheet | Make face, hair, body and relevant profile views readable; do not introduce multiple outfits |
| Costume reference sheet | Show one wearer in one outfit, with actual front/back/side coverage and useful details |
| Ensemble/crowd design | Keep exact cast count and distinct approved identities; establish common world with individual variation |
| Action-ready wardrobe | Add only the seated/walking/reaching/drape checks required by the actual scene |

A costume sheet is a reference asset, not a nine-shot storyboard. Do not apply storyboard panel counts or fill nine cells by default. Respect the requested number of views, one-image delivery, aspect ratio and no-text preference. Costume work does not authorize media generation unless the user requests it; this enhancement alone does not generate a new cast.

## Separate identity, look and scene state

Keep three linked records rather than one mutable character image:

| Record | Preserve |
|---|---|
| Identity | Exact character tag/source revision, approved apparent age, facial structure/asymmetry, skin tone/texture, hairline, body proportions, relevant physical/perception traits |
| Costume look | Internal look/version ID, exact approved costume tag if one exists, garments/layers, construction, material, base colours, fit, accessories and normal wearing positions |
| Scene state | Script day/scene/shot, selected look, current fastening/drape, sleeves, wetness/dirt/tears, hair/makeup and prop/contact state with source/approval |

Changing the outfit must not silently change the individual. Preserve approved face details, including photorealistic skin/texture for realistic inputs; preserve an approved stylized identity/style rather than forcing realism. Allow no automatic de-ageing, slimming, beauty retouch, eye normalization, hairline restoration or invented marks. Requested age/hair/face changes apply only to their stated scope; keep costume unchanged when that is locked. A back view need not display the face, but hair/head/body still belong to the same person.

Link named character movement/speaking profiles using `performance-and-action.md`; costume does not define personality or movement by itself. Do not infer temperament, caste, religion or income from appearance. Use authored/scripted or approved context; design choices remain proposals until approved or covered by an explicit delegated design instruction.

Use `assets/cast-costume.template.json` only when a durable structured record helps. It is an empty schema example, not populated project canon. Store actual records in the project's existing authorized cast/wardrobe register or a supported extension after checking its schema; link the shared project context rather than replacing it. Do not create a competing cast bible or write real cast data into this reusable template.

## Develop the cast and outfit

For new design, derive the brief from period/place, age, role, daily activity, season, occasion, character arc and production style. Research unfamiliar regional or period details when they affect the design. Do not replace a supplied contemporary UP village look with generic bridal, royal, glamour or another region's dress. Modest income does not automatically mean dirt or torn clothing.

For an existing cast, verify each approved face before considering variation. For a new ensemble, give each person a distinct supported combination of apparent age, face/head shape, hair, body silhouette, posture and outfit construction within the same world. Preserve authored family resemblance without cloning identities. Exact cast count is independent of how many views of each person are shown. A lineup is a scale/ensemble aid, not a substitute for an individual identity reference; do not invent measured heights from images.

Record only the outfit facts needed to reproduce it:

- Silhouette and fit: garment length, looseness, waist/hem position, sleeve length, neckline and footwear.
- Construction and layers: under/outer garments, placket, collar, seams, borders, pockets, closures, pleats and overlap order.
- Material: approved fabric, weave/texture, thickness, matte/sheeny finish, weight and drape. Cotton must not silently become glossy silk.
- Colour and pattern: named base colours, trim and motif placement/scale; colour samples are source-relative guides, not calibrated physical truth or guaranteed generated RGB values.
- Wearing map: anatomical LEFT/RIGHT shoulder, wrist, hip and fastening direction; distinguish these from screen-left/right. A reverse does not swap the wearer's sides.
- Accessories: exact jewellery/footwear/headwear and attached cloth details. Record story-critical counts/locations only when supported; do not invent hidden buttons or embroidery as verified facts.
- Condition: stable wear/patches/tears and changing scene condition. Ordinary folds vary with pose and gravity; garment construction and an established tear do not jump sides.

Keep a worn shoulder cloth, dupatta, sari pallu or turban tail explicit when it is an identity/look anchor. Separate portable props such as a bag or basket from the outfit, while recording strap/support when visible. If the user removes a bag from the sheet, remove its visible strap in every affected view; do not delete the story prop from other scenes.

## Design readable reference sheets

Choose the smallest pack that covers the intended use. These are defaults, not fixed quotas:

| Component | Purpose and framing |
|---|---|
| Approved master | A clear face/identity source and, when outfit detail needs it, a full-body look anchor |
| Core costume views | Front, anatomical left profile, back, anatomical right profile; head-to-foot with small margins, comparable scale and consistent camera perspective |
| Face supplement | Front/three-quarter/profile portrait only when face detail in the full-body sheet is insufficient or a new identity needs it |
| Garment details | Only necessary neckline/closure, border/hem, shoulder cloth, jewellery, footwear, print or fabric closeups |
| Movement supplement | Only needed sitting, walking, folded-leg or reaching posture; keep base construction/ownership while cloth responds naturally |
| Ensemble lineup | Approved relative scale and identity differentiation, with no duplicate people or invented exact measurements |

For an existing requested layout, retain it; add missing evidence through the smallest permitted repair. If only one image is requested, deliver one readable sheet and keep any technical map outside it. Do not add free-floating face cutouts, loose garments, palette cards, labels or accessories as extra cells unless useful and requested/within the approved layout. Do not turn a costume sheet into a product catalogue.

Use an evenly lit neutral reference presentation by default: plain neutral-grey background, soft natural-looking light, consistent exposure/white balance, natural skin texture, readable fabric and gentle support shadow. A provided approved tone/background overrides this default. Keep cinematic colour and dramatic lighting for a separate scene look test when needed; neutral reference lighting does not authorize recolouring a locked scene.

Use a neutral, unforced expression and relaxed posture with enough arm separation to read garment sides and hands. Preserve character-specific constraints, including lowered/unfocused eyes; neutral is not mandatory direct eye contact or a forced T-pose. Avoid perspective that elongates limbs, changes head/body proportion or hides footwear. Front/back/profile labels must describe actual orientation, not repeated three-quarter images.

Choose enough depth of field for face and garments, without portrait bokeh hiding construction. Check crop, fingertips, hair/headwear and feet. Maintain useful scale across full-body cells; detail cells may intentionally use a different magnification. A sheet is not a geometric scan, sewing pattern or reconstructed 3D asset.

Resolution belongs to the actual output. A 3840-pixel-wide four-column sheet provides about 960 pixels per view before gutters, not four independent 4K images. If face/material detail is insufficient, propose a simpler layout or separate high-detail views within the user's scope. Preserve one-file delivery when requested, and never claim native 4K from prompt text or an upscale alone.

## Generate or revise from approved sources

1. Inspect the actual selected identity/costume images before reference-dependent work. Bind source roles explicitly: identity, outfit, garment detail, pose/layout and optional lighting. Names/tags alone do not attach images. A mood/style reference must not replace the wearer's face or approved costume.
2. Reuse an approved identity/look master. If none exists, create one candidate only when generation/design is authorized. Do not mark a generated candidate approved merely because it exists. Reuse earlier design approvals; ask only for a material unresolved design choice or an essential missing source.
3. Resolve whether a new sheet replaces an asset version, adds views of the same look or introduces a distinct outfit. Keep the identity tag stable. Reuse an already approved mapping; ask once only if variant/tag application is genuinely unresolved. An internal look/version ID is not permission to invent a production @tag.
4. Derive required views from the approved master, keeping original identity and outfit as anchors. Use additional verified views/details where useful. Do not rely exclusively on a chain of unchecked generations; validate a new view before promoting it to an additional source.
5. If a multi-view generation drifts, repair the faulty view(s) or generate missing views from the anchors within authorized scope. Separate-view generation is a fallback, not a proven universally better method. Do not rebuild accepted views simply to make one grid uniform.
6. Treat unseen back/side construction as unknown when reproducing an existing garment. A plausible proposal is allowed in authorized new design; an exact replica needs essential missing detail resolved. Never claim hidden details were visually verified.
7. Run cross-view identity/look checks before reusing the pack. Optional scene tests check the actual relevant movement or lighting, not a mandatory battery of poses. Use current verified model/tool input rules; no assumed slot counts, seed guarantees, native resolution or unsupported edit controls.

If an outfit photograph contains another wearer, designate it as a garment reference only. Do not blend faces or body identity. If the tool cannot separate those roles reliably, use an available approved garment-only reference or a supported bounded-edit workflow; missing assets remain pending rather than silently substituted. Follow the actual image-generation/edit tool's reference and inspection requirements.

## Compile usable prompts

Keep planning records separate from executable text. Use the user's requested format; a look sheet need not use storyboard shot IDs. Repeat critical identity/look constraints per independently executable view, and bind the same source versions across a combined sheet.

Portable sheet prompt structure:

```text
<requested ratio/style and exact view count/layout>. Same <approved identity tag/reference> wearing one <approved outfit/look reference>. <Actual front/back/anatomical side orientations and consistent full-body scale>. <Critical garment silhouette/layers/material/colour/side-specific anchors>. <Neutral relaxed pose and character-specific eye/posture constraints>. <Readable face/garments/footwear, useful focus and margins>. <Approved background/light/tone>. Preserve <identity and unrequested design/state>; <only requested details or supplements>. No rendered text unless requested.
```

Portable targeted revision:

```text
Edit <exact selected sheet/cells>. Change only <requested garment region, colour, identity-age correction or accessory>. Apply consistently to <affected views>. Preserve <approved face/age/hair/body unless specifically changed>, <unchanged garment construction, material, drape, accessories, pose/layout, background and tone>. Maintain <anatomical side and required contact/support>.
```

For frame prompts retrieve the exact look plus the relevant scene-state override, not the entire sheet description. Include critical visible wardrobe anchors and owned prop tags without forcing offscreen details into a crop.

## Inspect and repair

Keep text specification, actual reference attachment, visual fidelity and user approval separate. Text checks cannot certify generated identity or material fidelity.

| Check | Failure to catch |
|---|---|
| Identity across views | New face, age/hairline/body drift, smoothed skin, normalized eye reference, cloned cast members |
| View completeness | Repeated fronts/three-quarters presented as back/profile, missing requested view, wrong cast/view count |
| Outfit construction | Collar/neckline/sleeve/hem changes, cotton-to-silk drift, seam/print/closure mutation |
| Anatomical wearing map | Pallu/towel/jewellery switching sides in reverse, floating cloth, missing shoulder support |
| Accessories and props | Disappearing cloth, jewellery mutation, bag removed but strap retained, basket confused with bag |
| Presentation and detail | Cut feet/hair/hands, inconsistent scale, crushed black detail, blown fabric highlights, blur, text or extra cells |
| Scene continuity | Wetness/dirt/damage resets without cause, wrong look for script day, impossible drape in sitting/walking |
| Output evidence | Unverified native size, uninspected cells called approved, approved identity bound to wrong outfit asset |

For an actual sheet, inspect every requested view against the master; name the faulty cell and the observed mismatch. A useful score is not a substitute for evidence: do not invent similarity percentages or a universal pass threshold. Wrong identity, missing required look detail or unsupported essential anatomy blocks that affected asset's acceptance. Preserve accepted cells and fix the smallest cause. An unseen region is PENDING or outside scope, not an invented success or defect.

Use failure/boundary cases during workflow changes: recolour a sari without altering blouse/face; restore one shoulder cloth without redesigning the kurta; remove a bag without deleting the shoulder cloth; preserve a blind character's eye reference; distinguish an unprovided garment back from an authorized new back design; preserve identity across a requested age-only correction's other locks. Keep true render comparisons pending until the authorized outputs are inspected.

## Research basis and limits

Checked 2026-10-19; these are baseline practices, not newly announced capabilities:

- Runway, Creating with Gen-4 Image References: https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References — supports clear, evenly lit neutral character references, source-specific prompting and controlled iteration. Its documented controls apply to that interface only; do not copy limits into another model.
- ScreenSkills, Assistant Costume Designer checklist: https://www.screenskills.com/media/7620/draft-jd-ac-designer-final-180523.pdf — script-led wardrobe breakdown, material/accessory records, fitting photographs and approved costume-continuity records.
- ScreenSkills, Script Supervisor Trainee checklist: https://www.screenskills.com/media/7612/final-jd-ss-trainee-110523.pdf — well-lit continuity images that show costume, hair/makeup and relevant prop positions.

The specific sheet layout, identity/look/state split, anatomical map and AI repair workflow above are production adaptations. They are not vendor guarantees or a claim of measured improvement. Validate text behavior separately from visual/temporal results; no model is fine-tuned or trained by saving this guide.
