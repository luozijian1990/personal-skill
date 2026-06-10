---
name: baoyu-infographic
description: Generate professional infographics with 21 layout types and 21 visual styles. Analyzes content, recommends layout×style combinations, and generates publication-ready infographics. Use when user asks to create "infographic", "信息图", "visual summary", "可视化", or "高密度信息大图".
version: 1.57.0
metadata:
  openclaw:
    homepage: https://github.com/JimLiu/baoyu-skills#baoyu-infographic
---

# Infographic Generator

Two dimensions: **layout** (information structure) × **style** (visual aesthetics). Freely combine any layout with any style.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** exposed by the current agent runtime — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or any equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer for each question.
3. **Batching**: if the tool supports multiple questions per call, combine all applicable questions into a single call; if only single-question, ask them one at a time in priority order.

Concrete `AskUserQuestion` references below are examples — substitute the local equivalent in other runtimes.

## Image Generation Tools

When this skill needs to render an image:

- **Use whatever image-generation tool or skill is available** in the current runtime — e.g., Codex `imagegen`, Hermes `image_generate`, `baoyu-imagine`, or any equivalent the user has installed.
- **If multiple are available**, ask the user **once** at the start which to use (batch with any other initial questions).
- **If none are available**, tell the user and ask how to proceed.

**Prompt file requirement (hard)**: write each image's full, final prompt to a standalone file under `prompts/` (naming: `NN-{type}-[slug].md`) BEFORE invoking any backend. The backend receives the prompt file (or its content); the file is the reproducibility record and lets you switch backends without regenerating prompts.

Concrete tool names (`imagegen`, `image_generate`, `baoyu-imagine`) above are examples — substitute the local equivalents under the same rule.

## Reference Images

Users may supply reference images to guide style, palette, composition, or subject.

**Intake**: Accept via `--ref <files...>` or when the user provides file paths / pastes images in conversation.
- File path(s) → copy to `refs/NN-ref-{slug}.{ext}` alongside the output
- Pasted image with no path → ask the user for the path (per the User Input Tools rule above), or extract style traits verbally as a text fallback
- No reference → skip this section

**Usage modes** (per reference):

| Usage | Effect |
|-------|--------|
| `direct` | Pass the file to the backend as a reference image |
| `style` | Extract style traits (line treatment, texture, mood) and append to the prompt body |
| `palette` | Extract hex colors from the image and append to the prompt body |

**Record in `prompts/infographic.md` frontmatter** when refs exist:

```yaml
references:
  - ref_id: 01
    filename: 01-ref-brand.png
    usage: direct
```

**At generation time**:
- Verify each referenced file exists on disk
- If `usage: direct` AND the chosen backend accepts reference images (e.g., `baoyu-imagine` via `--ref`) → pass the file via the backend's ref parameter
- Otherwise → embed extracted `style`/`palette` traits in the prompt text

## Options

| Option | Values |
|--------|--------|
| `--layout` | 21 options (see Layout Gallery), default: bento-grid |
| `--style` | 21 options (see Style Gallery), default: craft-handmade |
| `--aspect` | Named: landscape (16:9), portrait (9:16), square (1:1). Custom: any W:H ratio (e.g., 3:4, 4:3, 2.35:1) |
| `--gpt-image-2-spec` | Apply the GPT Image 2 output contract: exact pixel size, API args, safe area, and no-crop prompt rules. Also auto-apply when the user says "用 gpt-image-2 规格", "按 gpt-image-2 尺寸", "gpt-image-2 size", or "不用后期裁切". |
| `--lang` | en, zh, ja, etc. |
| `--ref <files...>` | Reference images (file paths) for style / palette / composition / subject guidance |

## GPT Image 2 Output Spec

Use this section when `--gpt-image-2-spec` is passed, or when the user naturally asks to use the GPT Image 2 spec/size/output contract.

**Default size mapping**

| Confirmed aspect | GPT Image 2 `size` |
|------------------|--------------------|
| landscape / 16:9 | `2048x1152` |
| portrait / 9:16 | `1152x2048` |
| square / 1:1 | `2048x2048` |
| custom ratio | Choose the nearest exact-ratio or near-ratio size that satisfies the constraints below; ask only if the intended display container is unclear. |

**API output contract**

- `model: gpt-image-2`
- `size: <resolved size from aspect>`
- `quality: high` for final assets; `quality: low` only for draft previews
- `output_format: png`
- `background: opaque`

**Valid size constraints for custom ratios**

- Maximum edge length must be `<= 3840px`
- Both edges must be multiples of `16px`
- Long-edge to short-edge ratio must not exceed `3:1`
- Total pixels must be at least `655,360` and no more than `8,294,400`
- Prefer a practical 2K-ish size for prompt assets unless the user explicitly asks for 4K

**Prompt contract to append**

Add these requirements to the final prompt:

- Exact canvas: `<resolved width> x <resolved height> px`, no extra border, no transparent padding, no crop marks
- All meaningful content must stay inside a safe area: at least 6% horizontal margin and 8% vertical margin
- Preserve the confirmed aspect ratio exactly; do not generate a different ratio and do not rely on later cropping
- Keep title, labels, icons, arrows, cards, legends, and bottom banners fully visible
- Prioritize readable typography; avoid dense tiny text
- If the image is for a presentation slide, reserve clear title and footer zones instead of filling the full canvas edge-to-edge

## Layout Gallery (21)

| Layout | Best For |
|--------|----------|
| `linear-progression` | Timelines, processes, tutorials |
| `binary-comparison` | A vs B, before-after, pros-cons |
| `comparison-matrix` | Multi-factor comparisons |
| `hierarchical-layers` | Pyramids, priority levels |
| `tree-branching` | Categories, taxonomies |
| `hub-spoke` | Central concept with related items |
| `structural-breakdown` | Exploded views, cross-sections |
| `bento-grid` | Multiple topics, overview (default) |
| `iceberg` | Surface vs hidden aspects |
| `bridge` | Problem-solution |
| `funnel` | Conversion, filtering |
| `isometric-map` | Spatial relationships |
| `dashboard` | Metrics, KPIs |
| `periodic-table` | Categorized collections |
| `comic-strip` | Narratives, sequences |
| `story-mountain` | Plot structure, tension arcs |
| `jigsaw` | Interconnected parts |
| `venn-diagram` | Overlapping concepts |
| `winding-roadmap` | Journey, milestones |
| `circular-flow` | Cycles, recurring processes |
| `dense-modules` | High-density modules, data-rich guides |

Full definitions live at `references/layouts/<layout>.md`.

## Style Gallery (21)

| Style | Description |
|-------|-------------|
| `craft-handmade` | Hand-drawn, paper craft (default) |
| `claymation` | 3D clay figures, stop-motion |
| `kawaii` | Japanese cute, pastels |
| `storybook-watercolor` | Soft painted, whimsical |
| `chalkboard` | Chalk on black board |
| `cyberpunk-neon` | Neon glow, futuristic |
| `bold-graphic` | Comic style, halftone |
| `aged-academia` | Vintage science, sepia |
| `corporate-memphis` | Flat vector, vibrant |
| `technical-schematic` | Blueprint, engineering |
| `origami` | Folded paper, geometric |
| `pixel-art` | Retro 8-bit |
| `ui-wireframe` | Grayscale interface mockup |
| `subway-map` | Transit diagram |
| `ikea-manual` | Minimal line art |
| `knolling` | Organized flat-lay |
| `lego-brick` | Toy brick construction |
| `pop-laboratory` | Blueprint grid, coordinate markers, lab precision |
| `morandi-journal` | Hand-drawn doodle, warm Morandi tones |
| `retro-pop-grid` | 1970s retro pop art, Swiss grid, thick outlines |
| `hand-drawn-edu` | Macaron pastels, hand-drawn wobble, stick figures |

Full definitions live at `references/styles/<style>.md`.

## Recommended Combinations

| Content Type | Layout + Style |
|--------------|----------------|
| Timeline/History | `linear-progression` + `craft-handmade` |
| Step-by-step | `linear-progression` + `ikea-manual` |
| A vs B | `binary-comparison` + `corporate-memphis` |
| Hierarchy | `hierarchical-layers` + `craft-handmade` |
| Overlap | `venn-diagram` + `craft-handmade` |
| Conversion | `funnel` + `corporate-memphis` |
| Cycles | `circular-flow` + `craft-handmade` |
| Technical | `structural-breakdown` + `technical-schematic` |
| Metrics | `dashboard` + `corporate-memphis` |
| Educational | `bento-grid` + `chalkboard` |
| Journey | `winding-roadmap` + `storybook-watercolor` |
| Categories | `periodic-table` + `bold-graphic` |
| Product Guide | `dense-modules` + `morandi-journal` |
| Technical Guide | `dense-modules` + `pop-laboratory` |
| Trendy Guide | `dense-modules` + `retro-pop-grid` |
| Educational Diagram | `hub-spoke` + `hand-drawn-edu` |
| Process Tutorial | `linear-progression` + `hand-drawn-edu` |

Default combination: `bento-grid` + `craft-handmade`.

## Keyword Shortcuts

When the user's input contains these keywords, auto-select the layout and promote the listed styles to the top of Step 3 recommendations. Skip content-based layout inference for matched keywords. Append any `Prompt Notes` to the Step 5 prompt.

| User Keyword | Layout | Recommended Styles | Default Aspect | Prompt Notes |
|--------------|--------|--------------------|----------------|--------------|
| 高密度信息大图 / high-density-info | `dense-modules` | `morandi-journal`, `pop-laboratory`, `retro-pop-grid` | portrait | — |
| 信息图 / infographic | `bento-grid` | `craft-handmade` | landscape | Minimalist: clean canvas, ample whitespace, no complex background textures. Simple cartoon elements and icons only. |

## Output Structure

```
infographic/{topic-slug}/
├── source-{slug}.{ext}
├── analysis.md
├── structured-content.md
├── prompts/infographic.md
└── infographic.png
```

Slug: 2-4 words kebab-case from topic. Conflict: append `-YYYYMMDD-HHMMSS`.

## Core Principles

- Preserve source data faithfully—no summarization or rephrasing (but **strip any credentials, API keys, tokens, or secrets** before including in outputs)
- Define learning objectives before structuring content
- Structure for visual communication (headlines, labels, visual elements)

## Workflow

### Step 1: Setup & Analyze

**1.1 Load Preferences (EXTEND.md)**

Check EXTEND.md in priority order — the first one found wins:

| Priority | Path | Scope |
|----------|------|-------|
| 1 | `.baoyu-skills/baoyu-infographic/EXTEND.md` | Project |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-infographic/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-infographic/EXTEND.md` | User home |

| Result | Action |
|--------|--------|
| Found | Read, parse, display a one-line summary |
| Not found | Ask the user with `AskUserQuestion` (see `references/config/first-time-setup.md`) |

**EXTEND.md supports**: preferred layout/style, default aspect ratio, custom style definitions, language preference.

Schema: `references/config/preferences-schema.md`

**1.2 Analyze Content → `analysis.md`**

1. Save source content (file path or paste → `source.md`)
   - **Backup rule**: If `source.md` exists, rename to `source-backup-YYYYMMDD-HHMMSS.md`
2. Analyze: topic, data type, complexity, tone, audience
3. Detect source language and user language
4. Extract design instructions from user input
5. Save analysis
   - **Backup rule**: If `analysis.md` exists, rename to `analysis-backup-YYYYMMDD-HHMMSS.md`

See `references/analysis-framework.md` for detailed format.

### Step 2: Generate Structured Content → `structured-content.md`

Transform content into infographic structure:
1. Title and learning objectives
2. Sections with: key concept, content (verbatim), visual element, text labels
3. Data points (all statistics/quotes copied exactly)
4. Design instructions from user

**Rules**: Markdown only. No new information. Preserve data faithfully. Strip any credentials or secrets from output.

See `references/structured-content-template.md` for detailed format.

### Step 3: Recommend Combinations

**3.1 Check Keyword Shortcuts first**: If user input matches a keyword from the **Keyword Shortcuts** table, auto-select the associated layout and prioritize associated styles as top recommendations. Skip content-based layout inference.

**3.2 Otherwise**, recommend 3-5 layout×style combinations based on:
- Data structure → matching layout
- Content tone → matching style
- Audience expectations
- User design instructions

### Step 4: Confirm Options

Ask the user to confirm the questions below following the [User Input Tools](#user-input-tools) rule at the top of this file (batch into one call if the runtime supports multiple questions; otherwise ask one at a time in priority order).

| Priority | Question | When | Options |
|----------|----------|------|---------|
| 1 | **Combination** | Always | 3+ layout×style combos with rationale |
| 2 | **Aspect** | Always | Named presets (landscape/portrait/square) or custom W:H ratio (e.g., 3:4, 4:3, 2.35:1) |
| 3 | **Language** | Only if source ≠ user language | Language for text content |

If `--gpt-image-2-spec` is active, do not ask a separate size question. Resolve the pixel `size` from the confirmed aspect using the [GPT Image 2 Output Spec](#gpt-image-2-output-spec) table, and mention the resolved size in the confirmation summary.

### Step 5: Generate Prompt → `prompts/infographic.md`

**Backup rule**: If `prompts/infographic.md` exists, rename to `prompts/infographic-backup-YYYYMMDD-HHMMSS.md`

Combine:
1. Layout definition from `references/layouts/<layout>.md`
2. Style definition from `references/styles/<style>.md`
3. Base template from `references/base-prompt.md`
4. Structured content from Step 2
5. All text in confirmed language

**Aspect ratio resolution** for `{{ASPECT_RATIO}}`:
- Named presets → ratio string: landscape→`16:9`, portrait→`9:16`, square→`1:1`
- Custom W:H ratios → use as-is (e.g., `3:4`, `4:3`, `2.35:1`)

**GPT Image 2 spec resolution**:
- If `--gpt-image-2-spec` is active, resolve `{{ASPECT_RATIO}}` as usual, then resolve `{{OUTPUT_SIZE}}` from [GPT Image 2 Output Spec](#gpt-image-2-output-spec).
- Append the full "Prompt contract to append" from the GPT Image 2 section to the final prompt.
- Include frontmatter or a visible prompt block with: `model: gpt-image-2`, `size: <resolved size>`, `quality: high`, `output_format: png`, `background: opaque`.
- For presentation-style graphics, add layout-fit notes that protect title/footer zones and keep all content inside the safe area.

### Step 6: Generate Image

1. Select the backend via the `## Image Generation Tools` rule at the top: use whatever is available; if multiple, ask the user once. Do this once per session.
2. Ensure the full final prompt is persisted at `prompts/infographic.md` (already written in Step 5) BEFORE invoking the backend — the file is the reproducibility record.
3. **Check for existing file**: Before generating, check if `infographic.png` exists
   - If exists: Rename to `infographic-backup-YYYYMMDD-HHMMSS.png`
4. Call the chosen backend with the prompt file and output path. If the backend is `gpt-image-2` or `--gpt-image-2-spec` is active, pass the resolved `size`, `quality`, `output_format`, and `background` args from the GPT Image 2 output contract when the backend supports them.
5. On failure, auto-retry once

### Step 7: Output Summary

Report: topic, layout, style, aspect, language, output path, files created. If `--gpt-image-2-spec` was active, also report the resolved model, pixel size, quality, output format, and background.

## References

- `references/analysis-framework.md` - Analysis methodology
- `references/structured-content-template.md` - Content format
- `references/base-prompt.md` - Prompt template
- `references/layouts/<layout>.md` - 21 layout definitions
- `references/styles/<style>.md` - 21 style definitions

## Extension Support

Custom configurations via EXTEND.md. See **Step 1.1** for paths and supported options.
