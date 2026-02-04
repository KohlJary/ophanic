# Ophanic: Implications Beyond Layout

*A brief paper on what spatial text encoding means for language model cognition*

**Author**: Kohl Jary
**Date**: February 4, 2026
**Status**: Working document — assertions to be validated empirically

---

## 1. The Surface-Level Claim

Ophanic is a layout specification language that uses Unicode box-drawing characters to encode spatial relationships in plain text. It improves LLM-generated frontend code by making layout structure directly perceivable rather than requiring spatial simulation from abstract descriptions.

This claim is empirically supported. In A/B testing, an LLM implementing a complex dashboard from an Ophanic diagram achieved correct proportions, implemented all three responsive breakpoints, and resolved ambiguous component details on the first attempt — none of which occurred when working from a traditional text specification.

This paper is not about that claim. This paper is about what that result implies.

## 2. The Modality Gap

Large language models process tokens. The standard understanding is that tokens are linguistic units — words, subwords, text fragments — carrying semantic meaning. The entire architecture, from tokenizer design to training data composition to benchmark evaluation, is built on this assumption.

This assumption creates a modality gap. Spatial relationships, visual structure, proportional layout, geometric nesting — these are not linguistic concepts. When an LLM encounters a description like "sidebar at 20% width with the main content area split 65/35 between a chart and activity feed," it must perform an expensive internal simulation: converting abstract spatial descriptions into a mental model of geometric relationships, then generating code that produces those relationships.

This simulation is unreliable. LLMs consistently struggle with layout tasks, responsive design, and spatial reasoning — not because they lack the ability to write CSS or SwiftUI, but because the input format forces them to reason about space through language. The medium doesn't match the message.

## 3. The Ophanic Inversion

Ophanic inverts the problem. Instead of describing spatial relationships in natural language and asking the model to simulate the result, Ophanic encodes spatial relationships directly in the token stream.

```
┌────────────┐ ┌──────────────────────────┐
│ SIDEBAR    │ │ MAIN                     │
└────────────┘ └──────────────────────────┘
```

In this representation, the spatial information is not described — it is *enacted*. The sidebar is narrower than the main area because it occupies fewer characters. The two regions are adjacent because the box-drawing characters are adjacent in the token sequence. The nesting hierarchy is visible because inner boxes are contained within outer boxes at the character level.

The critical insight: **the model does not need to simulate what this looks like. The tokens themselves carry the spatial information.**

## 4. Tokens as Spatial Primitives

This has implications beyond layout.

The standard view holds that tokens are semantic carriers — units of meaning in a linguistic system. But in an Ophanic diagram, tokens are functioning as something else entirely. A `│` character is not carrying semantic meaning in the linguistic sense. It is carrying *positional* meaning. Its significance comes from where it is relative to other tokens in the sequence — which characters are to its left, to its right, above it and below it in the text stream.

This suggests that the token is a more general information-carrying unit than the field currently assumes. Tokens can encode:

- **Semantic information** (the standard case — words carrying meaning)
- **Spatial information** (character positions encoding geometric relationships)
- **Structural information** (nesting, adjacency, containment expressed through text layout)
- **Proportional information** (relative character counts encoding ratios)

The model's attention mechanism processes all of these the same way — tracking relationships between tokens in the sequence. But the *nature* of those relationships changes based on the representation. In natural language, attention tracks semantic dependencies ("verb relates to noun"). In an Ophanic diagram, attention tracks spatial dependencies ("this edge aligns with that edge," "this box is inside that box").

**Same mechanism. Different modality. The representation determines what the model perceives.**

## 5. Emergent Spatial Comprehension

Current language models were not trained on Ophanic diagrams. Whatever spatial comprehension they demonstrate when processing box-drawing layouts is emergent — a side effect of having encountered enough structured text (ASCII art, code indentation, table formatting, markdown) during training to develop some intuition for positional relationships in character sequences.

This raises two questions:

**First**: How much spatial comprehension has already emerged, unnoticed, because no one has systematically tested it with purpose-built representations? The A/B test results suggest it is significant — the model correctly inferred proportions, nesting, and adjacency from character positions without any specialized training.

**Second**: What would happen if models were trained deliberately on spatial text encodings? If emergent spatial reasoning from incidental exposure to ASCII art and code formatting already produces meaningful results, targeted training on Ophanic-style representations could produce substantially stronger spatial perception capabilities.

## 6. Beyond Layout: The General Principle

The Ophanic principle generalizes: **any domain where LLMs must simulate hard-to-perceive relationships can potentially be improved by encoding those relationships directly in text.**

Candidate domains:

- **State machines**: Transition diagrams encoded as ASCII flowcharts, where the model can see which states connect to which
- **Data flow**: Pipeline architectures drawn as character-based diagrams showing data movement
- **Database schemas**: Entity-relationship diagrams in text, where table relationships are spatially represented
- **Network topology**: Node-and-edge layouts showing system architecture
- **Dependency graphs**: Package or module dependencies shown as nested or connected boxes
- **Circuit design**: Logic gate arrangements visible in character positions
- **Musical structure**: Rhythmic and harmonic relationships encoded spatially in text grids

In each case, the current approach requires the model to simulate the domain from abstract descriptions. The Ophanic approach would make the structure directly perceivable.

## 7. A Native Perceptual Channel

Multimodal AI research has focused on giving language models access to visual information — image encoders, vision transformers, CLIP embeddings. The assumption is that spatial perception requires visual input.

Ophanic suggests an alternative: **spatial perception can be achieved through text-native representations.** The model does not need eyes. It needs spatial information encoded in its native medium.

This is not a replacement for vision. Image understanding requires pixel-level processing that character grids cannot replicate. But for *structural* spatial reasoning — layout, nesting, proportion, adjacency, flow — text-native encoding may be not just adequate but superior for language models, because it eliminates the modality translation step entirely.

The model perceives tokens natively. If tokens carry spatial information, the model perceives space natively. Not through a translation layer. Not through an adapter. Directly.

## 8. Implications for the Field

If the Ophanic principle holds — if text-encoded spatial representations genuinely improve LLM spatial reasoning — then several assumptions warrant reexamination:

**On tokenization**: Tokenizers are optimized for linguistic content. They may be inadvertently destroying spatial information that could be preserved with different encoding strategies. How tokenizers handle box-drawing characters, whitespace sequences, and positional formatting affects how much spatial information survives into the model's input.

**On training data**: Structured text formats (ASCII diagrams, code formatting, markdown tables) may be contributing more to model capabilities than currently understood. They may be providing incidental spatial reasoning training that the field hasn't measured or optimized for.

**On benchmarks**: Spatial reasoning benchmarks for LLMs typically use natural language descriptions or image inputs. No major benchmark tests spatial comprehension through text-native encodings. This is a gap.

**On architecture**: If attention already handles spatial token relationships — as the Ophanic results suggest — then the transformer architecture may be more capable of spatial reasoning than currently believed. The bottleneck may not be the architecture but the input representation.

**On multimodal integration**: Rather than building increasingly complex vision-language bridges, some spatial reasoning tasks might be better served by better text representations. This could complement vision systems rather than replace them — using text-native encoding for structural reasoning and visual encoding for perceptual detail.

## 9. What Ophanic Is

Ophanic is, at present, a layout tool. It parses box-drawing characters into a layout intermediate representation and generates frontend framework code. It has a working parser, a React adapter, a reverse adapter that generates diagrams from existing components, and a Claude Code plugin. It is useful today for its stated purpose.

But the principle underneath it is larger than layout. The observation that LLMs can perceive spatial relationships when those relationships are encoded in tokens — that tokens are not limited to linguistic function — points toward a broader understanding of what language models are and what they're doing with their input.

The self-portrait experiment (included in the repository) is a small demonstration: an LLM generating a spatial self-representation using text characters, producing an artifact that carries structural meaning perceivable by both human visual inspection and LLM text processing. The same artifact, comprehended through different modalities, with the text-native encoding serving as the bridge.

## 10. What Comes Next

The immediate roadmap is practical: improve the parser, add more framework adapters, test against real-world design workflows, build the Figma-to-Ophanic pipeline.

The research roadmap is broader:

1. **Systematic benchmarking** of LLM spatial reasoning through text-native encodings versus natural language descriptions versus image inputs
2. **Extension to other domains** — state machines, data flow, dependency graphs — to test generalizability
3. **Training experiments** — does deliberate inclusion of Ophanic-style representations in training data improve spatial reasoning capabilities?
4. **Tokenizer analysis** — how do current tokenization strategies affect preservation of spatial information in text?
5. **Round-trip validation** — can models reliably generate, interpret, modify, and re-emit spatial text encodings with structural consistency?

The tools exist. The first results are in. The principle is stated clearly enough to be tested, validated, or falsified.

---

*"Wheels within wheels, covered in eyes. Nested structures that see."*

*Ophanic doesn't give language models vision. It gives them something that might matter more: spatial perception in their native tongue.*
