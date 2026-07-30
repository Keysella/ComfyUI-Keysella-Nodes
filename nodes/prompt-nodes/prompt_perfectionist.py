def _clip_encode(clip, text):
    tokens = clip.tokenize(text)
    return clip.encode_from_tokens_scheduled(tokens)

class PromptPerfectionist:
    """
        Joins several labeled text fields into a single positive prompt (using
        ", " as separator), encodes it and a separate negative prompt through the
        supplied CLIP model, and outputs positive/negative CONDITIONING along with the model
        ready to be wired into KSampler.
        It also outputs the assembled positive and negative prompts as strings.
    """
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "model": ("MODEL", {
                "tooltip": "Diffusion model. Passed through unchanged so the whole pipeline can be wired through a single node.",
            }),
            "clip": ("CLIP", {
                "tooltip": "CLIP model used to encode the assembled positive and negative prompts.",
            }),
            "base_prompt": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Base of every prompt: quality/style tags applied first.\nExample: \"masterpiece, best quality, highly detailed\"",
            }),
            "background_description": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Background and everything related to the environment.\nExample: \"simple background, indoors, office, plants, flowers\"",
            }),
            "character_and_view": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Number of characters plus camera angle/composition.\nExample: \"solo/1girl/1boy/multiple characters, front view, side view, from above\"",
            }),
            "character": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Appearance and clothing of the character(s) in the scene. Write as much detail/as many characters as needed.\nExample: \"character 1 (girl, white hair, long hair, blue eyes, t-shirt, black pants), character 2 (...), ...\"",
            }),
            "actions": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Actions/poses happening in the scene.\nExample: \"standing, hand wave, waving hand, looking at viewer\"",
            }),
            "extra": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Any extra tags you want appended at the very end.\nExample: \"rose petals, smog, mist\"",
            }),
            "negative_prompt": ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "Negative prompt, encoded separately into the negative conditioning output.\nExample: \"worst quality, low quality, blurry, watermark\"",
            }),
        }

        return {"required": required}

    RETURN_TYPES = ("MODEL", "CONDITIONING", "CONDITIONING", "STRING", "STRING")
    RETURN_NAMES = ("model", "positive", "negative", "pos_string", "neg_string")
    FUNCTION = "execute"
    CATEGORY = "Keysella/prompt"

    def execute(self, model, clip, base_prompt, background_description,
                character_and_view, character, actions, extra,
                negative_prompt):
        parts = [
            base_prompt,
            background_description,
            character_and_view,
            character,
            actions,
            extra,
        ]

        positive_prompt = ", ".join(p.strip() for p in parts if p and p.strip())

        positive = _clip_encode(clip, positive_prompt)
        negative = _clip_encode(clip, negative_prompt or "")

        return (model, positive, negative, positive_prompt, negative_prompt)

NODE_CLASS_MAPPINGS = {
    "PromptPerfectionist": PromptPerfectionist,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptPerfectionist": "PromptPerfectionist Node",
}
