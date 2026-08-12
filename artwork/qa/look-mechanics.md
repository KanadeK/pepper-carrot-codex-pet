# Pepper look mechanics

## Natural motion

Pepper is a humanoid witch with a separate head and neck, expressive drawn eyes,
soft hair, and a rigid worn hat. Her feet, boots, skirt, lower torso, scale, and
baseline stay planted and centered. The eyes lead each gaze change, with the
irises, pupils, eye whites, eyelids, and brows redrawn together inside the
original eye construction. The head and neck follow with restrained yaw or
pitch, then the shoulders follow by a smaller amount. Her hands remain in the
quiet idle stance so look direction is not confused with another task state.

The hat stays attached to the skull. Its brim, crown, and curled tip follow the
head as one worn object and change perspective or occlusion naturally; they do
not float, lag, or rotate independently. Hair follows the head with only a very
small coherent shift. No part of the face is stretched or replaced.

## Cardinal pose families

- `000 up`: body stays frontal; eyes and eyelids point toward the top edge;
  chin lifts slightly; the hat follows the head pitch while both feet remain
  fixed. This must read as up rather than neutral.
- `090 screen-right`: nose tip and both pupils cross to the screen-right side
  of the head center; head and neck yaw right; the screen-right side of the face
  becomes more occluded while the opposite cheek and hair gain visibility.
- `180 down`: body stays frontal; eyes and eyelids point toward the bottom edge;
  chin tucks; the brim overlaps the upper face slightly more without hiding the
  eyes. This must read as down rather than sadness or failure.
- `270 screen-left`: inverse of `090`; nose tip and both pupils cross to the
  screen-left side; head and neck yaw left; occlusion and visible hair sides
  reverse naturally.

## Motion budget and continuity

Each 22.5-degree step advances the same gaze family by roughly the same visual
amount. At final 192x208 size, eye landmarks move about 1 to 2 pixels per step,
head and hair landmarks about 2 to 4 pixels, shoulders no more than 2 pixels,
and the lower-body anchor does not move. Apparent body height and head size stay
within about 2 percent.

Row 9 advances continuously from `000` through `157.5`. Row 10 begins exactly
one step after `157.5`, passes through `180` and `270`, and ends at `337.5`,
exactly one step before `000`. No adjacent pair may reverse, recenter, flip the
hat curl, change hand pose, or jump scale.

Do not rotate, skew, mirror, or warp the whole sprite. Do not add new eyes,
floating pupils, labels, arrows, clocks, props, shadows, glows, or detached
effects.
