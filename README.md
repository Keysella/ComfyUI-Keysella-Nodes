# ComfyUI-Keysella-Nodes

My Node pack for ComfyUI, containing nodes that I will use in my workflows.

## Structure

```
ComfyUI-Keysella-Nodes/
  __init__.py            # aggregates NODE_CLASS_MAPPINGS from all nodes/ modules
  nodes/
    prompt-nodes/         # nodes for writing/assembling prompts
      prompt_perfectionist.py
  web/                    # frontend (.js) extensions, auto-loaded by ComfyUI (currently empty)
```

To add a new node: create/reuse a category folder under `nodes/`, add a
module there exposing `NODE_CLASS_MAPPINGS`/`NODE_DISPLAY_NAME_MAPPINGS`,
and register its relative path in `_NODE_MODULES` inside `__init__.py`.

## Nodes

### PromptPerfectionist Node (`Keysella/prompt`)

Combines several labeled text fields into a single positive prompt
(joined with `, `), encodes it and a separate negative prompt through the
supplied CLIP model, and outputs `model`, `positive`, `negative` ready for
`KSampler`.

Additionaly, it outputs the assembled positive and negative prompts as strings to use elsewhere.

Fields: `base prompt`, `background description`, `character and view`,
`character` (free-form; describe one or several characters yourself),
`actions`, `extra`, `negative prompt`. Hover any field label for a
tooltip with an example.
