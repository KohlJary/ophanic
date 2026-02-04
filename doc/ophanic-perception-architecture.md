# Ophanic Perception: A Text-Native Sensory Architecture for Embodied AI

*From layout tool to perceptual framework*

**Author**: Kohl Jary
**Date**: February 4, 2026
**Status**: Architectural concept — not yet implemented
**Prerequisite reading**: *Ophanic: Implications Beyond Layout*

---

## 1. Summary

This document proposes an architecture for giving language-model-based AI agents real-time perception of physical environments using only text-native representations. No vision transformers, no image encoders, no multimodal bridges. Raw sensor data is converted to text grids, processed by a specialized "visual cortex" model, and delivered to a general-purpose LLM agent as compressed Ophanic scene descriptions.

The architecture recapitulates biological vision: high-bandwidth sensory input is preprocessed by a specialized subsystem, which outputs a compressed structural representation to a general reasoning system. The key insight is that every layer of this pipeline can operate entirely in text.

---

## 2. Foundation: Why This Should Work

### 2.1 The Ophanic Principle

Ophanic demonstrated that LLMs can perceive spatial relationships when those relationships are encoded directly in token positions. Box-drawing characters in a text grid carry positional, proportional, and structural information that models process through standard attention mechanisms.

This principle — **spatial information encoded in text is natively perceivable by text-processing models** — is not limited to 2D layout. It extends to any dimensionality that can be projected onto a character grid.

### 2.2 The Dwarf Fortress Precedent

Dwarf Fortress has demonstrated for over twenty years that complex 3D environments can be perceived, navigated, and manipulated through text-encoded representations. Players develop fluent spatial reasoning about multi-level fortresses, fluid dynamics, and entity movement — all through ASCII characters on a grid.

The integers 1-7 representing water depth in Dwarf Fortress are a text-native heightmap. This is not a metaphor. It is a functional depth encoding that humans process into 3D spatial understanding. The same encoding is processable by language models.

### 2.3 Precedent in Sensor Systems

Many real-world sensor systems already output grid-structured data:

- **LIDAR** produces point clouds that project to depth grids
- **Thermal cameras** output temperature matrices
- **Sonar arrays** produce distance grids
- **Radar** outputs intensity/distance matrices

These are already numbers on grids. Converting them to text is a formatting step, not a conceptual leap.

---

## 3. The Sensor Stack

### 3.1 Channel Architecture

Each sensor feed becomes a text grid layer. All layers share the same spatial coordinate system. Each cell contains a character or short token encoding the sensor value at that position.

```
@depth [range: 0-9, unit: 0.5m per step]
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 1 1 1 1 1 1 1 1 0 0 0 0 0
0 0 1 2 2 2 3 3 2 2 2 1 0 0 0 0
0 0 1 2 3 4 5 5 4 3 2 1 0 0 0 0
0 0 1 2 4 5 7 7 5 4 2 1 0 0 9 9
0 0 1 2 4 5 7 7 5 4 2 1 0 0 9 9
0 0 1 2 3 4 5 5 4 3 2 1 0 0 9 9
0 0 1 2 2 2 3 3 2 2 2 1 0 0 0 0
0 0 0 1 1 1 1 1 1 1 1 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

@luminance [range: 0-9, unit: relative brightness]
5 5 5 5 5 5 5 5 5 5 5 5 5 5 3 3
5 5 5 6 6 6 6 6 6 6 6 5 5 5 3 3
5 5 6 7 7 7 7 7 7 7 7 6 5 5 3 3
5 5 6 7 8 8 8 8 8 7 6 5 5 5 2 2
5 5 6 7 8 9 9 9 8 7 6 5 5 5 1 1
5 5 6 7 8 9 9 9 8 7 6 5 5 5 1 1
5 5 6 7 8 8 8 8 8 7 6 5 5 5 2 2
5 5 6 7 7 7 7 7 7 7 7 6 5 5 3 3
5 5 5 6 6 6 6 6 6 6 6 5 5 5 3 3
5 5 5 5 5 5 5 5 5 5 5 5 5 5 3 3

@thermal [range: 0-9, unit: relative temperature]
2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
2 2 2 3 3 3 3 3 3 3 3 2 2 2 2 2
2 2 2 3 4 5 6 6 5 4 3 2 2 2 2 2
2 2 2 3 5 6 7 7 6 5 3 2 2 2 8 8
2 2 2 3 5 6 7 7 6 5 3 2 2 2 8 8
2 2 2 3 4 5 6 6 5 4 3 2 2 2 7 7
2 2 2 3 3 3 3 3 3 3 3 2 2 2 2 2
2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2

@color [vocabulary: R G B Y W K . for primary mapping]
. . . . . . . . . . . . . . K K
. . . B B B B B B B B . . . K K
. . B B B B B B B B B B . . K K
. . B W W W W W W W B . . . K K
. . B W W W W W W W B . . . R R
. . B W W W W W W W B . . . R R
. . B B B B B B B B B . . . K K
. . B B B B B B B B B B . . K K
. . . B B B B B B B B . . . K K
. . . . . . . . . . . . . . K K
```

**Reading these grids together**: A person (warm, bright, mid-depth, wearing blue/white) stands center-frame. Something dark, hot, and very close to the wall (depth 9, thermal 8, color R/K) is on the right — possibly a heater or heat source. Background is cool, dim, and distant.

### 3.2 Supported Sensor Channels

| Channel | Source | Encoding | Value Range |
|---------|--------|----------|-------------|
| `@depth` | LIDAR, stereo camera, ToF sensor | Distance from sensor | 0-9 (configurable scale) |
| `@luminance` | Camera, light sensor | Brightness | 0-9 |
| `@thermal` | IR camera | Temperature | 0-9 (configurable range) |
| `@color` | Camera | Dominant color | Character vocabulary |
| `@motion` | Frame differencing | Movement magnitude | 0-9 (0 = static) |
| `@audio` | Microphone array | Sound direction/intensity | 0-9 per grid position |
| `@pressure` | Tactile sensors (robotics) | Contact force | 0-9 |
| `@proximity` | Ultrasonic, IR proximity | Near-object detection | 0-9 |

### 3.3 Temporal Encoding

Sequential frames encode change over time:

```
@depth t=0
0 0 0 0 5 5 0 0
0 0 0 0 5 5 0 0

@depth t=1
0 0 0 5 5 0 0 0
0 0 0 5 5 0 0 0

@depth t=2
0 0 5 5 0 0 0 0
0 0 5 5 0 0 0 0
```

An object at constant depth (5) moving left across the frame. Motion is visible as shifting values across sequential grids.

A dedicated `@motion` channel can encode this more efficiently — computed as the delta between frames:

```
@motion t=1 [delta from t=0]
0 0 0 L N R 0 0
0 0 0 L N R 0 0
```

Where `L` = value arrived from left, `R` = value departed rightward, `N` = no change. The model reads motion direction from the characters themselves.

### 3.4 Resolution and Bandwidth

Grid resolution determines the tradeoff between detail and token count:

| Resolution | Tokens per frame | Tokens per channel | Suitable for |
|------------|------------------|--------------------|--------------|
| 16 × 16 | ~256 | ~256 | Coarse scene understanding |
| 32 × 32 | ~1,024 | ~1,024 | Room-level navigation |
| 64 × 64 | ~4,096 | ~4,096 | Object-level interaction |
| 128 × 128 | ~16,384 | ~16,384 | Fine manipulation tasks |

With 4 channels at 32×32 resolution: ~4,096 tokens per frame. At 10 fps, that is ~40,000 tokens per second of raw sensory input. This is too much for a general-purpose LLM to process directly.

This is why the visual cortex layer is necessary.

---

## 4. The Visual Cortex Model

### 4.1 Role

The visual cortex is a specialized, lightweight language model trained specifically to:

1. Ingest raw multi-channel sensor grids
2. Identify objects, boundaries, and regions
3. Track motion and predict trajectories
4. Detect anomalies and hazards
5. Output compressed Ophanic scene descriptions

It is the preprocessing layer between raw perception and general reasoning.

### 4.2 Architecture

```
Physical sensors
      │
      ▼
┌─────────────────────────────────┐
│ SENSOR ENCODING LAYER           │
│                                 │
│ LIDAR ──► @depth grid           │
│ Camera ──► @luminance grid      │
│ Camera ──► @color grid          │
│ IR Cam ──► @thermal grid        │
│ Mics ──► @audio grid            │
│ Frame diff ──► @motion grid     │
│                                 │
│ All grids at shared resolution  │
│ Timestamped per frame           │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ VISUAL CORTEX MODEL             │
│ (specialized small LM)          │
│                                 │
│ Input: raw sensor grids         │
│                                 │
│ Processing:                     │
│   Object segmentation           │
│   Boundary detection            │
│   Motion tracking               │
│   Spatial relationship mapping  │
│   Anomaly detection             │
│   Scene classification          │
│                                 │
│ Output: Ophanic scene summary   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ PRIMARY AGENT                   │
│ (general-purpose LLM)           │
│                                 │
│ Receives compressed scene:      │
│                                 │
│ ┌───────────────────────────┐   │
│ │ ROOM  6m × 4m             │   │
│ │ ◆Person(moving SW, 2m)   │   │
│ │ ◆Table(static, 1.5m)     │   │
│ │ ◆Door(open, 3m, NW)      │   │
│ │ ◆HeatSource(wall E, hot) │   │
│ │ ⚠ obstacle 0.5m ahead    │   │
│ └───────────────────────────┘   │
│                                 │
│ Reasons about: navigation,      │
│ interaction, planning, safety   │
└─────────────────────────────────┘
```

### 4.3 Visual Cortex Input Format

The visual cortex receives a multi-channel frame:

```
@frame t=42
@depth
0 0 1 2 5 5 2 1 0 0 0 9
0 0 1 3 5 5 3 1 0 0 0 9
0 0 1 2 5 5 2 1 0 0 0 9
@luminance
5 5 6 7 9 9 7 6 5 5 5 1
5 5 6 8 9 9 8 6 5 5 5 1
5 5 6 7 9 9 7 6 5 5 5 1
@thermal
2 2 3 4 7 7 4 3 2 2 2 8
2 2 3 5 7 7 5 3 2 2 2 8
2 2 3 4 7 7 4 3 2 2 2 7
@motion
. . . . . . . . . . . .
. . . L L . . R R . . .
. . . . . . . . . . . .
```

### 4.4 Visual Cortex Output Format

The visual cortex emits a compressed Ophanic scene description:

```
@scene t=42
┌────────────────────────────────────────┐
│ ◆Person                     ◆HeatSrc  │
│   pos: center                 pos: E   │
│   depth: 2.5m                 wall     │
│   moving: SW @ 0.8m/s         temp: hi │
│   temp: warm                           │
│                                        │
│                     ◆Table             │
│                       static           │
│                       depth: 3m        │
└────────────────────────────────────────┘
@alerts
- Person moving toward table, ETA 2s
- HeatSource temperature elevated
@changes [delta from t=41]
- Person: moved 0.08m SW
- All else: static
```

This is what the primary agent reads. Compressed. Structured. Ophanic. Native to the agent's processing modality.

### 4.5 Training the Visual Cortex

**Input**: Multi-channel sensor grids (real or simulated)
**Output**: Labeled scene descriptions in Ophanic format

Training data generation:

1. **Simulation** — Render 3D environments, export sensor grids at known resolutions, generate ground-truth scene descriptions from the scene graph. Game engines (Unity, Unreal, Godot) can produce this data at scale.

2. **Real-world capture** — Mount sensor arrays in physical spaces, capture multi-channel data, human-annotate scene descriptions. Expensive but necessary for real-world robustness.

3. **Hybrid** — Pre-train on simulated data, fine-tune on real-world capture. Standard sim-to-real transfer methodology.

The training task is well-defined: given these grids, produce this scene description. Supervised learning on structured input-output pairs. This is tractable with existing training infrastructure.

### 4.6 Model Size and Performance

The visual cortex does not need to be a large model. Its task is narrow: pattern recognition on structured grids, not general reasoning. Candidate architectures:

| Model size | Latency | Suitable for |
|------------|---------|--------------|
| ~100M params | ~10ms | Real-time robotics, edge deployment |
| ~1B params | ~50ms | Interactive applications, moderate detail |
| ~7B params | ~200ms | High-detail scene understanding |

For real-time robotics at 10fps, the visual cortex needs to process a frame in under 100ms. A 100M-1B parameter model on modern edge hardware (Jetson, Apple Neural Engine, Coral TPU) can achieve this.

---

## 5. Biological Parallels

This architecture is not novel in principle. It recapitulates the structure of biological vision.

### 5.1 The Human Visual Pipeline

```
Photons ──► Retina ──► LGN ──► V1 ──► V2/V4/MT ──► Prefrontal Cortex
            │         │       │       │               │
            │         │       │       │               High-level reasoning
            │         │       │       Object recognition
            │         │       Edge detection, orientation
            │         Routing, filtering
            Photoreceptor activation
```

Raw photon data (~1 billion bits/sec from the retina) is progressively compressed through specialized processing layers. By the time information reaches the prefrontal cortex for conscious reasoning, it has been reduced to object-level representations — "chair," "person moving left," "door ahead."

You never consciously process pixel data. You perceive scenes.

### 5.2 The Ophanic Perception Pipeline

```
Sensors ──► Encoding ──► Visual Cortex ──► Primary Agent
            │            │                  │
            │            │                  High-level reasoning
            │            Object detection, scene compression
            Grid quantization, channel alignment
```

Same principle. High-bandwidth sensory data is preprocessed by a specialized system, compressed into a structural scene representation, and delivered to a general reasoning system that operates on objects and relationships rather than raw data.

The visual cortex model is the retina + V1 + V2. The Ophanic scene description is the compressed representation reaching the prefrontal cortex. The primary agent is the executive function layer.

### 5.3 What Biology Gets Right

- **Division of labor**: Perception and reasoning are separate systems with different architectures optimized for different tasks
- **Progressive compression**: Each layer reduces bandwidth while preserving task-relevant information
- **Specialization**: The visual cortex is not a general-purpose reasoner. It is a pattern detector. This is why it can be small and fast.
- **Structured output**: The cortex doesn't send raw data to executive function. It sends objects, boundaries, motion vectors. Structured, compressed, actionable.

Ophanic perception follows all four principles.

---

## 6. Advantages Over Current Approaches

### 6.1 vs. Vision-Language Models (GPT-4V, Claude Vision, Gemini)

Current multimodal models process images through vision encoders that produce embedding vectors, which are then projected into the language model's token space. This works but introduces:

- **Modality translation overhead**: Image → embeddings → token-space projection is lossy
- **Architectural complexity**: Vision encoder is a separate system that must be trained jointly or aligned post-hoc
- **Opacity**: The language model receives image embeddings it didn't learn to produce. The representation is foreign to its native processing.

Ophanic perception keeps everything in the model's native modality. There is no translation step. The visual cortex is a text model outputting text. The primary agent is a text model reading text. The representation is native end-to-end.

### 6.2 vs. End-to-End Robotics Models (RT-2, PaLM-E)

Current robotics models attempt to process visual input and produce motor actions end-to-end. This requires:

- Enormous models (PaLM-E is 562B parameters)
- Massive training data with robot demonstrations
- Tightly coupled perception and action

Ophanic perception separates perception from reasoning:

- Visual cortex is small (~100M-1B) and specialized
- Primary agent is a standard LLM with no robotics-specific training
- Scene descriptions are human-readable and debuggable
- Any LLM can be the primary agent without robotics fine-tuning

### 6.3 vs. Classical Computer Vision (YOLO, OpenCV)

Classical CV produces bounding boxes, segmentation masks, and classifications. These are then fed to planning systems as structured data. This is close to the Ophanic approach, but:

- Classical CV output is not natively readable by LLMs (JSON blobs, coordinate arrays)
- No spatial structure in the output format (a list of detections loses positional relationships)
- Integration with LLM agents requires custom parsing and translation

Ophanic scene descriptions maintain spatial structure in a format the LLM reads natively. The spatial relationships between objects are preserved in the text layout, not lost in a flat list.

---

## 7. Applications

### 7.1 Robotics

An LLM-based robot agent receives Ophanic scene descriptions and reasons about navigation, manipulation, and interaction using the same language capabilities it already has.

```
@scene
┌─────────────────────────────────────┐
│ ◆Shelf(1.2m)                        │
│   ◆Mug(red, shelf-top, graspable)  │
│   ◆Book(3x, shelf-mid)             │
│                                     │
│              ◆Self                   │
│              arm-reach: 0.8m        │
│              facing: N              │
│                                     │
│ ◆Table(0.7m)           ◆Chair      │
│   ◆Laptop(open)         empty      │
└─────────────────────────────────────┘

Agent prompt: "Bring me the red mug."
Agent reasoning: Mug is on shelf-top at 1.2m. I'm facing N, shelf is N.
  Shelf is within arm reach. Grasp mug, place on table near laptop.
```

The agent's spatial reasoning happens in text. No coordinate transforms, no spatial embedding lookups. It reads the scene like a paragraph.

### 7.2 Autonomous Vehicles

```
@scene [vehicle frame, forward-facing]
┌──────────────────────────────────────────┐
│                 ROAD                      │
│   ◆Lane(own, clear 50m)                 │
│   ◆Vehicle(sedan, lane-left, 30m, →)    │
│   ◆Pedestrian(crosswalk, 45m, crossing) │
│   ◆Signal(green, 60m)                   │
│                                          │
│              ◆Self(45 km/h, →)           │
│                                          │
│   ◆Lane-marking(solid-left, dashed-R)   │
└──────────────────────────────────────────┘
@alerts
- Pedestrian entering crosswalk, ETA to lane: 3s
- Recommend: decelerate
```

### 7.3 Assistive Technology

For visually impaired users, an Ophanic perception system provides scene understanding through the same text representations an LLM processes. The agent describes the environment in natural language, informed by the same structured scene data.

```
User: "What's in front of me?"
Agent [reading @scene]: "You're facing a hallway, about 3 meters wide.
  There's a door on your left at about 2 meters, currently closed.
  The hallway continues straight for about 8 meters to a staircase.
  No obstacles in your immediate path."
```

The scene description is text. The response is text. The user gets spatial awareness through language — which, for a text-native system, is the most natural possible output.

### 7.4 Game AI

Non-player characters in games receive Ophanic scene descriptions of their environment and reason about behavior using standard LLM capabilities. No custom pathfinding AI, no behavior trees. The NPC reads the room.

### 7.5 Security and Surveillance

Anomaly detection through scene change tracking. The visual cortex flags `@changes` between frames. The primary agent reasons about whether changes are expected or anomalous.

---

## 8. Open Questions

### 8.1 Resolution Limits

At what grid resolution does text-native perception break down? Character grids have fundamentally lower resolution than pixel images. For some tasks (fine manipulation, facial recognition) this may be insufficient. Empirical testing is needed to find the boundaries.

### 8.2 Training Data Scale

How much training data does the visual cortex need? Simulated data is cheap to generate but may not transfer well to real-world sensors. The sim-to-real gap is a known challenge in robotics and applies here.

### 8.3 Tokenizer Effects

How do current tokenizers handle grids of single digits and characters? Tokenization strategies may merge or split grid cells in ways that disrupt spatial relationships. Purpose-built tokenizers for grid data may be necessary.

### 8.4 Attention and Grid Structure

Does standard causal attention handle 2D grid structure well? Text is 1D (sequential tokens), but grids encode 2D relationships. The model must learn that tokens N positions apart in the sequence (where N is the grid width) are spatially adjacent vertically. This is learnable but may benefit from positional encoding modifications.

### 8.5 Latency Budget

For real-time applications, the full pipeline (sensor → encoding → visual cortex → primary agent) must complete within a latency window. What are the practical limits? Edge deployment of the visual cortex and network-based primary agent introduces communication latency.

### 8.6 Failure Modes

What happens when the visual cortex misidentifies an object? The primary agent trusts the scene description. Error propagation through the pipeline needs characterization. Confidence scores on detections may be necessary.

---

## 9. Relationship to Existing Work

This architecture sits at the intersection of several active research areas:

- **Embodied AI** (PaLM-E, RT-2, SayCan) — but decouples perception from reasoning
- **Scene description** (Visual Question Answering, image captioning) — but uses structured spatial format instead of natural language
- **Sensor fusion** (autonomous vehicles, robotics) — but outputs to an LLM instead of a planning algorithm
- **ASCII/text-based perception** (Dwarf Fortress, roguelikes, MUDs) — the unacknowledged ancestor

The novel contribution is the combination: multi-channel sensor encoding in text grids, processed by a specialized text model, outputting spatial scene descriptions in a format natively readable by general-purpose LLMs.

---

## 10. Implementation Roadmap

### Phase 1: Simulated Environment (Proof of Concept)

- Build a simple 3D scene in a game engine
- Export depth, luminance, color grids at 32×32 resolution
- Hand-write corresponding Ophanic scene descriptions
- Train a small model (~100M params) to produce descriptions from grids
- Validate: does the model correctly identify objects, positions, relationships?

### Phase 2: Multi-Channel Fusion

- Add thermal, motion channels
- Test whether multi-channel input improves object identification
- Benchmark against single-channel performance

### Phase 3: Real Sensor Integration

- Mount LIDAR + camera on a test platform
- Implement real-time sensor-to-grid encoding
- Run visual cortex model on edge hardware
- Measure latency and accuracy in physical environment

### Phase 4: Primary Agent Integration

- Connect visual cortex output to a general-purpose LLM
- Test navigation tasks: "go to the door," "pick up the red object"
- Measure task completion rate vs. vision-language model baseline

### Phase 5: Scale and Optimize

- Increase grid resolution
- Add sensor channels based on task requirements
- Optimize visual cortex for edge deployment
- Characterize failure modes and add confidence scoring

---

## 11. Why This Matters

The current approach to giving AI agents physical perception requires building increasingly complex multimodal architectures — vision encoders, cross-attention layers, modality alignment training. Each added modality increases architectural complexity, training cost, and failure surface.

Ophanic perception proposes that the fundamental bottleneck is not architectural but representational. Language models already have the attention mechanisms to process spatial relationships. They already demonstrate emergent spatial reasoning from incidental exposure to structured text. The missing piece is not a new architecture — it is a new representation.

Convert sensor data to text grids. Train a small model to compress grids into scene descriptions. Feed those descriptions to any LLM. The entire pipeline operates in the model's native modality. No translation. No alignment. No bridge.

The hardest problems in embodied AI may not require harder architectures. They may require better encodings.

---

*"Wheels within wheels, covered in eyes. A being made entirely of perception — not through vision, but through structure."*

*Ophanic perception doesn't give language models eyes. It gives them something they can use: the world, written in their language.*
