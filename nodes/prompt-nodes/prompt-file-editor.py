import pathlib

from aiohttp import web
from server import PromptServer

_DATA_DIR = pathlib.Path(__file__).resolve().parents[2] / "nodes-data" / "prompt-file-editor-data"
_ALLOWED_EXTENSIONS = {".txt", ".md"}
_API_PREFIX = "/keysella/prompt_file_editor"


def _list_prompt_files():
    if not _DATA_DIR.exists():
        return []
    files = []
    for path in sorted(_DATA_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in _ALLOWED_EXTENSIONS:
            files.append(path.relative_to(_DATA_DIR).as_posix())
    return files


def _resolve_safe_path(rel_path: str) -> pathlib.Path:
    rel_path = (rel_path or "").strip().replace("\\", "/").lstrip("/")
    if not rel_path:
        raise ValueError("Empty path")
    base = _DATA_DIR.resolve()
    candidate = (base / rel_path).resolve()
    if base != candidate and base not in candidate.parents:
        raise ValueError("Path escapes data directory")
    return candidate


routes = PromptServer.instance.routes


@routes.get(_API_PREFIX + "/list")
async def _list_files(request):
    return web.json_response(_list_prompt_files())


@routes.get(_API_PREFIX + "/read")
async def _read_file(request):
    rel_path = request.query.get("path", "")
    try:
        target = _resolve_safe_path(rel_path)
    except ValueError:
        return web.json_response({"error": "Invalid path"}, status=400)
    if not target.is_file():
        return web.json_response({"error": "Not found"}, status=404)
    return web.json_response({"content": target.read_text(encoding="utf-8")})


@routes.post(_API_PREFIX + "/save")
async def _save_file(request):
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON body"}, status=400)

    rel_path = (data.get("path") or "").strip()
    content = data.get("content", "")

    if not rel_path:
        return web.json_response({"error": "Filename is required"}, status=400)

    if pathlib.Path(rel_path).suffix.lower() not in _ALLOWED_EXTENSIONS:
        rel_path += ".txt"

    try:
        target = _resolve_safe_path(rel_path)
    except ValueError:
        return web.json_response({"error": "Invalid path"}, status=400)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return web.json_response({"path": target.relative_to(_DATA_DIR.resolve()).as_posix()})


class PromptFileEditor:
    """
        Pick a prompt file from nodes-data/prompt-from-file-loader-data/, edit
        its content directly in the node (auto-loaded via the frontend
        extension), and optionally save changes back to disk - to the same
        file or a new one/subfolder - using the Save button. Outputs the
        current text as a STRING.
    """
    @classmethod
    def INPUT_TYPES(cls):
        files = _list_prompt_files()
        default_file = files[0] if files else ""
        return {
            "required": {
                "prompt_file": ("STRING", {
                    "default": default_file,
                    "tooltip": "Path (relative to nodes-data/prompt-from-file-loader-data/) of the currently "
                               "loaded prompt file. Set via the Choose file button; not manually editable.",
                }),
                "prompt_text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Editable prompt text. Auto-filled when you pick a file above; edit freely, "
                               "then use the Save button to write it back (to the same file, or type a new "
                               "name/subfolder path to save as a new file).",
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = "Keysella/prompt"

    def execute(self, prompt_file, prompt_text):
        return (prompt_text,)


NODE_CLASS_MAPPINGS = {
    "PromptFileEditor": PromptFileEditor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptFileEditor": "PromptFileEditor Node",
}
