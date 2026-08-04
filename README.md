# ComfyUI-Keysella-Nodes

My Node pack for ComfyUI, containing nodes that I will use in my workflows.

## Structure

```
ComfyUI-Keysella-Nodes/
  __init__.py            # aggregates NODE_CLASS_MAPPINGS from all nodes/ modules
  nodes/
    prompt-nodes/         # nodes for writing/assembling prompts
      prompt_perfectionist.py
      prompt-from-file-loader.py
  nodes-data/
    prompt-from-file-loader-data/  # user-provided prompt .txt/.md files, see "Data folders" below
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

### PromptFromFileLoader Node (`Keysella/prompt`)

Loads a ready-made prompt from a `.txt`/`.md` file stored under
`nodes-data/prompt-from-file-loader-data/` and outputs it as a `STRING`.
Files should contain nothing but a single comma-separated tag prompt.

Files can be organized into subfolders (e.g. `pose/`, `background/`,
`misc/`) — the node's dropdown lists each file's path relative to the data
folder. See "Data folders" below for details.

## Data folders

### `nodes-data/prompt-from-file-loader-data/`

Drop prompt files here for the `PromptFromFileLoader` node to pick up.

- Allowed extensions: `.txt` or `.md`.
- Each file must contain **only** the prompt itself: comma-separated tags,
  nothing else (no headers, no extra formatting).
- You can freely organize files into subfolders, e.g.:
  ```
  prompt-from-file-loader-data/
    pose/
      standing-wave.txt
      sitting-crosslegged.txt
    background/
      office.txt
      forest.txt
    misc/
      lighting-rim.txt
  ```
- The node's dropdown lists every file here (recursively) using its path
  relative to this folder (e.g. `pose/standing-wave.txt`).
- Restart ComfyUI or refresh the node list to pick up newly added files.
- Actual prompt files (`.txt`/`.md`) under this folder are gitignored (only
  the folder structure and the `put_your_prompts_here` placeholder are
  tracked), so your personal prompts won't end up committed.
