# STATUS
## Done
- Repo skeleton, palette, style prefix, negative prompt, character prompt fragments (pushed to origin/main)
- bible/inspiration.md (CoComelon structural lessons only)
- Ollie turnaround: 4 candidates generated (recraft_v4_1, standard, 2k, 16:9, palette-locked)

## Style change (owner): flat cut-paper -> soft glossy 3D (see bible/inspiration.md)
Round 2 Ollie candidates (nano_banana job IDs; saved in characters/ollie/candidates_3d/):
1. f3ad4390-7022-4a8e-88bb-ed3047869541  (clearest otter read)
2. e08625da-10bc-4f7b-9756-fa09272a32a0  (vinyl-toy look, weakest)
3. eef5388f-db6b-41f2-8978-e708679d1125  (multi-spike tuft)
4. 600d6c50-e390-4785-b331-26dd11be1dcb  (most appealing, quilted vest, teeth showing)
Note: requested nano_banana_pro, jobs reported model nano_banana_2.
Round 1 (cut-paper) candidates are superseded.

## Round 3: Ollie = round-2 v1, fix pass (characters/ollie/candidates_3d_fix/)
Fix-round job IDs: 3f22788f-d46f-462f-a64d-bff424b3e427, 7df79819-65cb-4022-9e69-c33ce2178924, ec442d46-4fe6-473d-a9a4-fc652c9e8931, 0819d505-ff5f-4987-8ba4-01a1f72c389f
Result: reference edit barely moved. fix_v3 added small chest pockets (closest to four). Tuft still slightly angled, not straight up.

## Ollie LOCKED: characters/ollie/ollie_turnaround.png (fix_v3, job ec442d46-4fe6-473d-a9a4-fc652c9e8931)
Expression sheets (reference = locked turnaround): characters/ollie/expressions/expr_v1.png (job e8706c4b-573d-44f2-a9c9-da85341e5fe4), expr_v2.png (job c5de4f0e-6cae-4233-a00c-cd5a0788ddae)
Open issue: tuft never stands straight up, even on the curious face.

## Awaiting review
- Pick an Ollie candidate (or request changes) before the other five characters are generated.

## Next
- Ollie expression sheet, then Pip, Gran Mari, Gus, Bean, Luna

## Ollie candidates (Higgsfield job IDs)
1. 32829dcc-f523-4ecc-bfad-84e4256ad833
2. f363b086-0df4-4225-99d4-9ad5d4ccaf40
3. 0076e373-715b-4fc1-bd18-238b98238178
4. 89cf3a06-1760-4a1a-aaa5-3eca2d215e86
Saved to characters/ollie/candidates/turnaround_v1..v4.png (host now reachable).
My read: v3 is the best otter silhouette but needs fixes (lavender limbs, whiskers, black nose, only 2 pockets). v1 matches pockets/tuft but reads as a penguin. v2 and v4 are off-palette and read as penguin/turtle.

## Cost (character-sheet cap: 300 credits)
- Spent: 98 credits per Higgsfield balance (988.1 -> 890.1). Remaining under 300 cap: 202.

## Cast turnarounds (round 1, soft-3D, Ollie sheet as style reference) - awaiting picks
Files: characters/<name>/candidates/turnaround_v1|v2.png
- Pip: v1 0833f3d3-a300-474d-9c8d-7003e7164204, v2 26206c55-ccfb-4d9a-ac6f-12ed8c2ad213
- Gran Mari: v1 d6283700-d8f1-45dd-b213-8fdae8c02574, v2 7ae61477-8fa1-4076-9007-9f5141ddd3d8
- Gus: v1 311bb899-c4c6-462d-ac73-c950477f04c3, v2 a8139f0f-4c4a-4732-97a0-5be11b2b0680
- Bean: v1 999f3d2c-d605-4aa4-8567-8a7f8890a07c, v2 5d0c0d69-8993-4918-b836-7d87966b3f02
- Luna: v1 573be74e-9eb5-4fbc-9088-76d3c32d5594, v2 5b3bea12-b549-4d94-a683-36bd89151c38
Known gaps: Bean not floating on her back (both upright); Luna glow steps (dim/bright/sparkle) not yet made; expression sheets for the five not yet made.

## Cast LOCKED (owner: "use your picks")
Turnarounds: pip v1 (back-view fixed via 5f822128-76fe-4d6b-868a-56a94ae44551), gran_mari v1, gus v2, bean v2, luna v1
Expression picks (characters/<name>/<name>_expressions.png): pip v2 (5d4e82e5-8120-4681-bb7d-157691cbfa38), gran_mari v1 (691cace8-c36b-411a-8058-b67777cc4022), gus v1 (a60a51f1-6901-49f3-bb43-141f7d5f7ec0), bean v2 (e656249e-9e9e-4d0b-985b-85a911d135e2)
Luna glow steps: luna/luna_glow_steps.png (19b5e836-0f62-4685-ae18-dbc77909472c). One Luna job failed (d9d74c5c-c9bb-405e-ab66-0c1541d0c28d).
Bean floating pose: bean/bean_float_pose.png (55760803-42fe-440f-92d0-181c337adf73); only the first two panels float on her back, side/back panels are upright.
Open issues: Bean's face is nearly identical to Ollie's in close-ups (ribbon not visible); Gran Mari reads bald with subtle expressions; Ollie's tuft never fully upright.

## Phase 1 progress
Done: bible/series_bible.md, style_guide.md (v2 soft 3D), voice_configs.json (voice IDs TBD), songs.md (lyrics + prompts, audio not generated), 5 location hero plates (bible/locations/).
Not started: ten scripts, storyboards, pipeline code, E01 production, YouTube packaging, book.
