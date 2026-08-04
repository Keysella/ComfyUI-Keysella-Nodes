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
      prompt-file-editor.py
  nodes-data/
    prompt-from-file-loader-data/  # user-provided prompt .txt/.md files, see "Data folders" below
  web/                    # frontend (.js) extensions, auto-loaded by ComfyUI
    prompt-file-editor.js # powers PromptFileEditor's live text field + Save button
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

### PromptFileEditor Node (`Keysella/prompt`)

Same data folder as `PromptFromFileLoader`, but lets you view/edit and save
prompt files right from the node:

- **Choose file** button opens a nested folder-tree menu (same mechanic as
  ComfyUI's "Add Node" cascading submenus) built from the data folder's
  subfolders/files - no manual typing needed.
- Below it, a read-only line shows the currently selected file's path
  (e.g. `pose/arms-crossed/eyebrow-raised.txt`).
- Picking a file auto-loads its content into `prompt_text` below (via
  `web/prompt-file-editor.js`).
- `prompt_text` is freely editable; the node outputs its current content as
  a `STRING`, whether or not you've edited it.
- The **Save** button prompts for a filename (pre-filled with the currently
  selected file). Typing a path with slashes (e.g. `pose/new-pose.txt`)
  saves into that subfolder, creating it if needed - nested subfolders are
  supported (`pose/sitting/onchair.txt`). If the name has no `.txt`/`.md`
  extension, `.txt` is appended automatically. Saving does not require
  running the workflow (Queue Prompt) - it happens instantly, and the
  read-only path line updates to the new/renamed file.
- Backend API routes (`/keysella/prompt_file_editor/list|read|save`) are
  registered in `prompt-file-editor.py` and restrict reads/writes to the
  `nodes-data/prompt-from-file-loader-data/` folder.

`PromptFromFileLoader` is kept as a simpler, editor-less alternative.

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
