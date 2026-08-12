Create one coherent eight-pose look-direction strip for the Codex v2 pet `pepper-carrot`, atlas row 10.

Use the attached eight-slot layout guide, canonical Pepper base, approved standard contact sheet, approved four-cardinal strip, and completed row 9. The updated cardinal strip is authoritative for direction meaning, especially its open-eyed `180` DOWN pose. Row 9 is authoritative for identity, hat width, body and head scale, foot baseline, rendering, and the `157.5 -> 180` boundary.

Output exactly eight complete full-body poses from left to right in this order: `180`, `202.5`, `225`, `247.5`, `270`, `292.5`, `315`, `337.5`. Degrees are clockwise in viewer/screen coordinates: `000` up, `090` screen-right, `180` down, `270` screen-left.

Direction contract:

1. `180`: face broadly frontal; chin only slightly tucked; BOTH EYES OPEN; light sclera visible; green irises/pupils clearly low toward the bottom edge. It must read looking down, never sleeping, blinking, sad, or bowing.
2. `202.5`: open-eyed down-left, beginning the screen-left turn while retaining a strong downward cue.
3. `225`: unmistakable open-eyed down-left.
4. `247.5`: screen-left with a remaining downward cue.
5. `270`: unmistakable SCREEN-LEFT profile; nose, pupils, and facial direction point to the viewer's left edge, never right.
6. `292.5`: screen-left with a beginning upward cue.
7. `315`: unmistakable up-left.
8. `337.5`: nearly up while remaining subtly screen-left, one even step before the approved `000` up anchor.

COHERENT SYNTHESIS LOCK: draw all eight poses together as one animation family. Use the same face construction, hat silhouette, body proportions, line quality, palette, lighting, scale, baseline, and planted feet throughout. Do not paste independently styled cells, mirror a right-facing family, close the eyes to indicate down, enlarge the hat, shrink the row, or rotate/skew the whole sprite.

LAYOUT LOCK: one centered pose per invisible equal slot on pure flat `#0000FF`; eight separated connected pose groups; clear chroma-only gutters; generous outer padding; no overlap, merged groups, cropped foreground, or edge contact. The deterministic assembler will crop and register the groups, so do not resize individual poses or add guides.

BOUNDARY LOCK: `180` must flow directly from row 9's `157.5` with the same body size, hat width, baseline, expression construction, and planted anchor. `337.5` must flow directly into the approved `000` up pose with the same properties.

Reject the result before returning it if `180` closes either eye or lacks visible low pupils; `225` is not down-left; `270` faces screen-right; `315` is not up-left; the eight poses change scale or baseline; any groups touch; or any foreground reaches the canvas edge.

Do not add labels, numbers, degree text, arrows, clocks, grids, guide marks, shadows, scenery, detached effects, extra characters, replacement eyes, or chroma-key blue inside Pepper.
