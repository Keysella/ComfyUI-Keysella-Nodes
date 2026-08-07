import { app } from "../../scripts/app.js";

const API_BASE = "/keysella/prompt_file_editor";
const NO_FILES_PLACEHOLDER = "<no files found>";

async function fetchFileList() {
    const res = await fetch(`${API_BASE}/list`);
    if (!res.ok) return [];
    return await res.json();
}

async function fetchFileContent(path) {
    const res = await fetch(`${API_BASE}/read?path=${encodeURIComponent(path)}`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.content ?? null;
}

async function savePromptFile(path, content) {
    const res = await fetch(`${API_BASE}/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, content }),
    });
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.error || "Save failed");
    }
    return data.path;
}

// Builds a { folders: { name: <node> }, files: [{ name, path }] } tree from
// a flat list of "a/b/c.txt" relative paths.
function buildFileTree(files) {
    const root = { folders: {}, files: [] };
    for (const relPath of files) {
        const parts = relPath.split("/");
        let node = root;
        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];
            if (!node.folders[part]) {
                node.folders[part] = { folders: {}, files: [] };
            }
            node = node.folders[part];
        }
        node.files.push({ name: parts[parts.length - 1], path: relPath });
    }
    return root;
}

// Recursively converts a tree node into LiteGraph.ContextMenu options,
// mirroring the nested "Add Node" style submenus.
function buildMenuOptions(node, onLeafClick) {
    const options = [];

    const folderNames = Object.keys(node.folders).sort((a, b) => a.localeCompare(b));
    for (const folderName of folderNames) {
        options.push({
            content: folderName,
            submenu: {
                options: buildMenuOptions(node.folders[folderName], onLeafClick),
                callback: onLeafClick,
            },
        });
    }

    const sortedFiles = [...node.files].sort((a, b) => a.name.localeCompare(b.name));
    for (const file of sortedFiles) {
        options.push({ content: file.name, path: file.path });
    }

    return options;
}

function openFileBrowser(event, onSelect) {
    fetchFileList().then((files) => {
        if (!files.length) {
            alert("No prompt files found under nodes-data/prompt-from-file-loader-data/.");
            return;
        }
        const tree = buildFileTree(files);
        const onLeafClick = (value) => {
            if (value && value.path) {
                onSelect(value.path);
            }
        };
        const options = buildMenuOptions(tree, onLeafClick);
        new LiteGraph.ContextMenu(options, {
            event,
            callback: onLeafClick,
            title: "Select prompt file",
        });
    });
}

app.registerExtension({
    name: "Keysella.PromptFileEditor",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "PromptFileEditor") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);
            const node = this;

            const fileWidget = node.widgets?.find((w) => w.name === "prompt_file");
            const textWidget = node.widgets?.find((w) => w.name === "prompt_text");
            if (!fileWidget || !textWidget) return;

            // prompt_file still exists as a real widget so its value persists in the
            // saved workflow, but it's no longer manually editable - hide it and show
            // a read-only display widget instead.
            fileWidget.type = "hidden";
            fileWidget.computeSize = () => [0, -4];

            const displayWidget = {
                name: "prompt_file_display",
                type: "keysella_readonly_text",
                value: "",
                computeSize(width) {
                    return [width, 20];
                },
                draw(ctx, _node, widgetWidth, y, H) {
                    const text = fileWidget.value || "(no file selected)";
                    ctx.save();
                    ctx.fillStyle = "#bbb";
                    ctx.font = "12px Arial";
                    ctx.textAlign = "left";
                    ctx.fillText(text, 10, y + H * 0.7, widgetWidth - 20);
                    ctx.restore();
                },
            };

            const loadSelectedFile = async () => {
                const selected = fileWidget.value;
                node.setDirtyCanvas(true, true);
                if (!selected || selected === NO_FILES_PLACEHOLDER) return;
                const content = await fetchFileContent(selected);
                if (content !== null) {
                    textWidget.value = content;
                    node.setDirtyCanvas(true, true);
                }
            };

            // Populate the text field with the initially selected file's content,
            // but only for brand-new nodes. When a workflow is loaded, ComfyUI
            // calls onConfigure right after this to restore the saved
            // prompt_file/prompt_text values - if that happens before this async
            // fetch resolves, skip it so we don't clobber the restored text with
            // the default file's content.
            node._promptFileEditorConfigured = false;
            setTimeout(() => {
                if (!node._promptFileEditorConfigured) {
                    loadSelectedFile();
                }
            }, 0);

            const chooseButton = node.addWidget("button", "Choose file", null, (_value, _widget, _node, _pos, event) => {
                openFileBrowser(event, (path) => {
                    fileWidget.value = path;
                    loadSelectedFile();
                });
            });

            node.addCustomWidget(displayWidget);

            const saveButton = node.addWidget("button", "Save", null, async () => {
                const suggested =
                    fileWidget.value && fileWidget.value !== NO_FILES_PLACEHOLDER
                        ? fileWidget.value
                        : "";
                const name = window.prompt(
                    "Filename (subfolders allowed, e.g. pose/newname.txt):",
                    suggested
                );
                if (!name) return;

                try {
                    const finalPath = await savePromptFile(name, textWidget.value ?? "");
                    fileWidget.value = finalPath;
                    node.setDirtyCanvas(true, true);
                } catch (err) {
                    alert(`Save failed: ${err.message}`);
                }
            });

            // Reorder widgets: Choose file button, read-only filename, prompt text, Save.
            const ordered = [chooseButton, displayWidget, textWidget, saveButton];
            const rest = node.widgets.filter((w) => !ordered.includes(w));
            node.widgets = [...rest, ...ordered];
        };

        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            onConfigure?.apply(this, arguments);
            this._promptFileEditorConfigured = true;
        };
    },
});
