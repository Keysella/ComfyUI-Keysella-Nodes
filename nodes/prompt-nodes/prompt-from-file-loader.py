import os
import pathlib

_DATA_DIR = pathlib.Path(__file__).resolve().parents[2] / "nodes-data" / "prompt-from-file-loader-data"
_ALLOWED_EXTENSIONS = {".txt", ".md"}


def _list_prompt_files():
    if not _DATA_DIR.exists():
        return []
    files = []
    for path in sorted(_DATA_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in _ALLOWED_EXTENSIONS:
            files.append(path.relative_to(_DATA_DIR).as_posix())
    return files


class PromptFromFileLoader:
    """
        Loads a ready-made prompt from a text file stored under
        nodes-data/prompt-from-file-loader-data/ and outputs it as a STRING.
        Files should contain nothing but comma-separated tags. Organize files
        into subfolders (e.g. pose/, background/, misc/) to keep them tidy -
        the dropdown shows each file's path relative to the data folder.
    """
    @classmethod
    def INPUT_TYPES(cls):
        files = _list_prompt_files()
        return {
            "required": {
                "prompt_file": (files if files else ["<no files found>"], {
                    "tooltip": "Prompt file to load, relative to nodes-data/prompt-from-file-loader-data/.\n"
                               "Create .txt or .md files there (optionally inside subfolders like pose/, "
                               "background/, misc/) containing a single comma-separated tag prompt.",
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = "Keysella/prompt"

    def execute(self, prompt_file):
        path = _DATA_DIR / prompt_file
        if not path.is_file():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        prompt = path.read_text(encoding="utf-8").strip()
        return (prompt,)

    @classmethod
    def IS_CHANGED(cls, prompt_file):
        path = _DATA_DIR / prompt_file
        try:
            return os.path.getmtime(path)
        except OSError:
            return float("nan")


NODE_CLASS_MAPPINGS = {
    "PromptFromFileLoader": PromptFromFileLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptFromFileLoader": "PromptFromFileLoader Node",
}
