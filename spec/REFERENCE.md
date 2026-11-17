# RSOS Language 0.2: reference (generated from the code; do not edit by hand)

## Statements


### header

| Statement | Register | Signature | Example |
|---|---|---|---|
| `LANGUAGE` | U49, U79, U80 | name:word, version:value → effect | `LANGUAGE RSOS 0.2` |

### declare

| Statement | Register | Signature | Example |
|---|---|---|---|
| `WORLD` | — | name:name → world | `WORLD lab` |
| `HOST` | U18, U20 | name:name, KIND?:word, CHANNELS?:list, STATES?:list → host | `HOST person KIND human CHANNELS visual, auditory, kinesthetic STATES eagle, owl` |
| `PROFILE` | — | name:name → profile | `PROFILE owner` |

### context

| Statement | Register | Signature | Example |
|---|---|---|---|
| `USE` | — | scope:enum:state/host/world/profile, name:word → effect | `USE HOST person / USE STATE eagle / USE PROFILE owner (sets the context for what follows)` |

### declare

| Statement | Register | Signature | Example |
|---|---|---|---|
| `OBJECT` | U16, U70 | name:name, KIND?:word, DOMAIN?:word, IN?:path, REPRESENTS?:value → object | `OBJECT couch KIND furniture IN eagle REPRESENTS langgraph` |
| `PART` | U45 | path:word, KIND?:word → part | `PART car.seat KIND module` |
| `PROPERTY` | U17 | path:path, value:value → effect | `PROPERTY sol.frequency = 392` |
| `RELATION` | U60 | a:path, verb:word, b:path → effect | `RELATION brain regulates heart` |

### mental

| Statement | Register | Signature | Example |
|---|---|---|---|
| `HOUSE` | U63 | name:name, FOR?:path → house | `HOUSE mind FOR person` |
| `ROOM` | U64 | name:name, PERSPECTIVE?:word, IN?:path → room | `ROOM eagle PERSPECTIVE above IN mind` |
| `MODEL` | U63, U72 | part:path, components:comp, IN?:path, FOR?:word → effect | `MODEL robot.head = associated + confidence + analogical_reasoning IN eagle FOR decision` |
| `DEDICATE` | U65 | object:path, TO:word → effect | `DEDICATE couch TO hypothesis_testing` |
| `FORM` | U66 | object:path, DIRECTIONS:cases → effect | `FORM couch DIRECTIONS forward -> hypothesis ; backward -> contradiction ; up -> framing ; down -> operational_test` |
| `MATERIAL` | U67 | object:path, level:value → effect | `MATERIAL couch = user_interface` |
| `ANCHOR` | U14, U68 | symbol:path, TO:path, CHANNEL?:word → effect | `ANCHOR eagle_calculator TO robot.head CHANNEL kinesthetic` |
| `FUTUREPACE` | U68 | symbol:path, SCENARIOS?:int → effect | `FUTUREPACE eagle_calculator SCENARIOS 3` |
| `SELECTMODEL` | U69 | part:path, BY?:enum:trigger/choice → effect | `SELECTMODEL robot.head BY choice (the control panel)` |

### scene

| Statement | Register | Signature | Example |
|---|---|---|---|
| `SCENE` | U48, U23 | name:name, ORDER?:list, IN?:path, LIGHT?:word → scene | `SCENE painting ORDER mountains, sky, house, grass, car, road LIGHT engineering` |

### state

| Statement | Register | Signature | Example |
|---|---|---|---|
| `COLOUR` | U4, U55 | target:path, colour:word, STATE?:word → effect | `COLOUR sol red STATE drive` |
| `SHIFT` | U4 | target:path, FROM?:word, TO:word → effect | `SHIFT planet.surface FROM black TO grey (a state transition that changes the repertoire)` |
| `HEAL` | U1, U8 | target:path, BY?:path, SCOPE?:enum:node/network/container/higher → effect | `HEAL country BY white_dragon.light SCOPE container` |
| `BEAM` | U2 | source:path, DIRECTION?:enum:vertical/horizontal/outward/inward/down/up/across, TO?:path, BY?:path → effect | `BEAM identity DIRECTION down (lands on all lower layers)` |
| `FLOW` | U3, U22 | source:path, DIRECTION:enum:vertical/horizontal/outward/inward/down/up/across, TO?:path → effect | `FLOW heart DIRECTION horizontal TO body` |
| `ROUTE` | U5 | object:path, BY:cases → effect | `ROUTE tv BY slumped -> problems ; agency -> communication_strategy` |
| `RESONATE` | U6 | a:path, WITH:path → effect | `RESONATE bones WITH rocket_heart` |
| `BALL` | U7 | trigger:word, COLOUR?:word → object | `BALL family_sounds AS ball1 COLOUR orange` |
| `COMPRESS` | U8 | items:list → object | `COMPRESS s1, s2, s3 AS lion_symbol` |
| `WEIGHT` | U9 | target:path, w:num → effect | `WEIGHT pinky 0.9` |
| `RESCRIPT` | U11, U12, U13 | target:path, WITH?:path, WHEN?:word → effect | `RESCRIPT earlier_self WITH lion.paw WHEN tension` |

### contact

| Statement | Register | Signature | Example |
|---|---|---|---|
| `TOUCH` | U26 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, ON:path → descendant | `TOUCH sol ON remote AT top` |
| `ATTACH` | U27 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, TO:path → descendant | `ATTACH sensor TO robot AT edge AS robot2` |
| `PIERCE` | U28, U29, U30, U31, U84 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, THROUGH:path → descendant | `PIERCE sol THROUGH remote FROM top DEPTH 3 AS remote_sol` |
| `PASS` | U32, U84 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, THROUGH:path → descendant | `PASS virus.particles THROUGH wall INTO langgraph.node2` |
| `WRAP` | U33 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, AROUND:path → descendant | `WRAP shell AROUND agent AS guarded_agent` |
| `MERGE` | U35 | source:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, DEPTH?:int, INTO?:path, MODE?:enum:view/system, WITH:path → descendant | `MERGE regulator WITH agent.controller AS controller2` |
| `SPLIT` | U34 | target:path, INTO:list → effect | `SPLIT remote INTO a, b` |
| `DOT` | U36, U84 | function:path, INTO:path → descendant | `DOT immune_memory INTO langgraph.router AS dot1 (adds; does not replace)` |
| `MOVE` | U42, U37 | source:path, ONTO:path, AT?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center → descendant | `MOVE painting_b ONTO painting_a` |
| `ROTATE` | U38 | target:path, BY?:num, RELATIVE?:path → descendant | `ROTATE painting_b BY 90 RELATIVE painting_a` |
| `FLIP` | U39 | target:path → descendant | `FLIP painting_b` |
| `OVERLAY` | U40 | source:path, ON:path, SHOW?:enum:half/full/part → descendant | `OVERLAY painting_b ON painting_a SHOW half` |
| `PROTRUDE` | U41 | target:path, INTO:path → effect | `PROTRUDE painting_ab.middle INTO room` |
| `FUSE` | U60 | a:path, WITH:path → descendant | `FUSE bacterium WITH liver AS guardian` |

### select

| Statement | Register | Signature | Example |
|---|---|---|---|
| `SELECT` | U43 | target:path, extent:enum:whole/part → descendant | `SELECT house.door WHOLE / SELECT house.door.middle PART` |
| `REGION` | U44 | name:name, SHAPE:enum:triangle/square/circle/point, CENTER:path, SIZE?:num, INCLUDES?:list → region | `REGION r1 SHAPE triangle CENTER car SIZE 0.4 INCLUDES engine, seat, window` |
| `ENTER` | U45, U58 | target:path, DEPTH?:int, MODE?:enum:view/system → effect | `ENTER car.seat DEPTH 2 (goes 3D: inside and hidden parts)` |
| `ZOOM` | U46 | direction:enum:in/out, target:path, MODE?:enum:view/system → effect | `ZOOM in couch.spring` |
| `LINE` | U47, U53 | name:name, THROUGH:list, FROM?:enum:top/bottom/left/right/front/back/side/surface/edge/interior/inside/outside/centre/center, PACE?:list, PAUSE?:list, IN?:path → line | `LINE l1 THROUGH mountain.top, house.door.middle, car.seat PAUSE car.seat` |
| `WIDEN` | U54 | line:path, TO:enum:tube/volume, RADIUS?:num → effect | `WIDEN l1 TO tube RADIUS 0.2` |
| `TIME` | U50, U52, U56 | target:path, action:enum:play/pause/slow/fast/rewind/tempo/cut/branch, AT?:value, RATE?:num, MODE?:enum:view/system → descendant | `TIME workflow_video slow RATE 0.25 MODE system` |

### host

| Statement | Register | Signature | Example |
|---|---|---|---|
| `TRANSPLANT` | U17, U84 | bundle:path, TO:path → descendant | `TRANSPLANT rocket TO body.heart AS rocket_heart (the whole property bundle travels)` |
| `REHOST` | U18 | bundle:path, IN:path → descendant | `REHOST rocket_heart IN planet AS planet_core` |
| `EXTERNALISE` | U19 | bundle:path, TO?:path → effect | `EXTERNALISE rocket_heart TO society` |
| `TRANSFER` | U84, U85 | source:path, TO:path → descendant | `TRANSFER bacterium.mobility TO guardian.mobility` |

### compile

| Statement | Register | Signature | Example |
|---|---|---|---|
| `CUE` | U82, U83, U15 | state:word, CODE:string, CHANNEL:word, LAYER?:word → effect | `CUE eagle CODE "-.." CHANNEL kinesthetic` |
| `MESSAGE` | U82 | sender:word, TO:word, STATE:word, CHANNEL?:word → effect | `MESSAGE owl TO architect STATE needs_input CHANNEL kinesthetic` |
| `PERSPECTIVE` | U51, U64 | target:path, view:word → effect | `PERSPECTIVE guardian eagle` |

### meaning

| Statement | Register | Signature | Example |
|---|---|---|---|
| `MEANING` | — | key:word, value:value, IN:word, SCOPE:enum:state/host/world/profile → effect | `MEANING contact.top = local_contact SCOPE state IN eagle` |
| `SEARCH` | U62 | key:word, OVER:list, METRIC?:word → effect | `SEARCH contact.bottom OVER lateral, local_contact, multi_layer METRIC task_success` |

### test

| Statement | Register | Signature | Example |
|---|---|---|---|
| `SNAPSHOT` | U68 | target:path, BEFORE?:int, DURING?:int, AFTER?:int → effect | `SNAPSHOT guardian BEFORE 100 DURING 100 AFTER 100` |
| `COMPARE` | U87 | target:path, AGAINST:list, METRIC?:word → effect | `COMPARE guardian AGAINST bacterium, liver METRIC safety` |
| `TEST` | — | target:path, METRIC?:word, IN?:path, SEEDS?:int → effect | `TEST guardian METRIC hazard_avoidance IN street SEEDS 20` |
| `REVERSE` | U87 | relation:word, IN?:path → effect | `REVERSE distress_raises_spending IN economy` |
| `ABLATE` | U87 | target:path, REMOVE:list → effect | `ABLATE guardian REMOVE legs` |
| `BASELINE` | U76 | target:path → effect | `BASELINE person (return to baseline, always available)` |

### paint

| Statement | Register | Signature | Example |
|---|---|---|---|
| `LAYER` | U59 | painting:path, action:enum:add/reveal/foreground/background/repaint, NAME?:word → descendant | `LAYER painting reveal NAME sketch` |
| `CUTPLACE` | U59, U60 | element:path, TO:path → descendant | `CUTPLACE painting_a.engine TO painting_b AS painting_b2 (cut out and place in another painting)` |
| `ENCODE` | U61 | system:path, MODE?:enum:exact/controlled/generative → descendant | `ENCODE car AS car_painting MODE controlled` |
| `DECODE` | U61 | painting:path, DOMAIN:word → descendant | `DECODE car_painting DOMAIN thermal_engineering AS new_design` |
| `EXTRACT` | U57 | source:path → descendant | `EXTRACT workflow_video AS recovery_rule (a function inferred from observed transitions)` |

### mental

| Statement | Register | Signature | Example |
|---|---|---|---|
| `RELATE` | U71 | a:path, TO:path → descendant | `RELATE kidney TO agent_filter AS analogy` |

### state

| Statement | Register | Signature | Example |
|---|---|---|---|
| `LOCATE` | U10 | output:path, MECHANISM?:path → effect | `LOCATE clock.hands MECHANISM clock.gears (fix the mechanism and the output follows)` |

### host

| Statement | Register | Signature | Example |
|---|---|---|---|
| `UPGRADE` | U25 | target:path, WITH?:path → descendant | `UPGRADE body WITH rocket_heart AS superhero_body` |
| `INPUT` | U24 | target:path, FROM?:enum:movement/position/gaze/touch, VIEW?:enum:front/side/back → effect | `INPUT painting_ab FROM movement VIEW front (human movement as input; view-dependent reading)` |
| `HOSTLOOP` | U21 | host:path, OBSERVE?:list, INTERVENE?:list, MEASURE?:list → effect | `HOSTLOOP bacteria OBSERVE light, nutrients INTERVENE light MEASURE movement, contraction` |

### govern

| Statement | Register | Signature | Example |
|---|---|---|---|
| `SPINE` | U73 | action:path, CHECK?:list → effect | `SPINE pierce_remote CHECK gi, jin, rei (every agent acts through the Spine)` |
| `WATCHDOG` | U74 | host:path, SWITCH:word, WHEN?:word → effect | `WATCHDOG person SWITCH bear WHEN overload` |
| `ARCHITECT` | U75 | action:enum:strategy/lock/hybrid/retire/reset, TARGET?:list → descendant | `ARCHITECT hybrid TARGET lion, eagle AS lion_eagle` |
| `OVERRIDE` | U77 | host:path, TYPE:enum:drive/calmness/regulation → effect | `OVERRIDE person TYPE calmness` |
| `GATE` | U78 | operator:word, REQUIRES:list → effect | `GATE autonomous_cue REQUIRES evidence, consent` |

### meta

| Statement | Register | Signature | Example |
|---|---|---|---|
| `INDUCE` | U81, U62 | name:name, FROM:path → operator | `INDUCE aperture_rule FROM gate_trials` |
| `REENTER` | U86 | node:path, WITH:word → effect | `REENTER ai_room WITH aperture_rule` |

## Core meanings (tier 1, fixed; D80)

| Key | Meaning | Source |
|---|---|---|
| `contact.surface` | `interface_only` | c2 T35.3 touch the surface; D80 |
| `contact.edge` | `dependency` | c2 T35.3 attach to an edge; D80 |
| `contact.top` | `supervisory_entry` | c2 T35.3 enter through the top; D80 |
| `contact.side` | `lateral` | c2 T35.3 enter through the side; D80 |
| `contact.left` | `lateral` | alias of contact.side (c2 T35.3); D80 |
| `contact.right` | `lateral` | alias of contact.side (c2 T35.3); D80 |
| `contact.front` | `lateral` | alias of contact.side (c2 T35.3); D80 |
| `contact.back` | `lateral` | alias of contact.side (c2 T35.3); D80 |
| `contact.interior` | `nested_state` | c2 T35.3 penetrate into the interior; owner c2 T35 surface→body→sub-code |
| `contact.inside` | `nested_state` | alias of contact.interior |
| `contact.through` | `multi_layer` | c2 T35.3 pass completely through; owner c2 T33 through the wall |
| `flow.vertical` | `hierarchy` | owner c1 T44, T88 |
| `flow.down` | `lands_on_all_lower` | owner c1 T47 beams land on the lower layers |
| `flow.up` | `towards_higher_order` | owner c1 T44, T55 |
| `flow.horizontal` | `spread_across` | owner c1 T95 pulse moves horizontally to others |
| `flow.across` | `spread_across` | alias of flow.horizontal |
| `flow.outward` | `to_environment` | owner c1 T66, T95 outside the body, others perceive |
| `flow.inward` | `into_host_subsystems` | owner c1 T66 extension inside affects the brain |
| `select.whole` | `full_module` | owner c1 T108 the whole door |
| `select.part` | `partial_function` | owner c1 T108 the middle of the door |
| `colour.black` | `destructive_only` | owner c1 T95 |
| `colour.grey` | `good_and_bad_with_protection` | owner c1 T95 black → grey, evolution |
| `colour.white` | `soothing_healing` | owner c1 T14 White Dragon light |
| `colour.gold` | `strength_agency` | owner c1 T14 Golden Lion light |
| `colour.red` | `drive` | owner c2 T35 |
| `colour.black_and_white` | `state_change_of_selection` | owner c2 T53 |

Keys with no core meaning (for example `contact.bottom`, `contact.centre`, `contact.outside`) must be bound with `MEANING` or left open with `SEARCH`; otherwise the compiler stops with E017.

## Diagnostics

| Code | Meaning |
|---|---|
| `E001_HEADER` | Language header missing or wrong version |
| `E002_WORLD` | Missing or duplicate world declaration |
| `E003_UNKNOWN_ENTITY` | Object, part, host, room or line not declared |
| `E004_PATH` | Path absent, empty or malformed |
| `E005_SYNTAX` | Statement does not match its grammar |
| `E006_CONTRACT` | A required property is absent |
| `E007_VALUE` | Value out of range or of the wrong kind |
| `E008_OPERATOR` | Unknown statement or operator |
| `E009_DUPLICATE` | Name declared twice |
| `E010_AMBIGUITY` | Two bindings give different meanings in the same scope |
| `E016_HOST` | Operator not defined for this host (kind or channel) |
| `E017_MEANING` | Meaning key unknown to the core and not bound or searched |
| `W001_OPEN_MEANING` | Meaning left open: resolved by search, not by the core |
| `W002_IMPLICIT_PART` | Sub-part used without a PART declaration (accepted, created implicitly) |
| `W003_NO_HOST` | Operator runs without a declared host; the core meaning is used |
