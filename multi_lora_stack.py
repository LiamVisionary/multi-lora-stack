import json

from nodes import LoraLoader, LoraLoaderModelOnly

FALSE_LIKE_VALUES = {"false", "0", "off", "none", "no", "disabled"}
TRUE_LIKE_VALUES = {"true", "1", "on", "yes", "enabled"}


def parse_lora_stack(lora_stack):
    if isinstance(lora_stack, str):
        try:
            parsed = json.loads(lora_stack)
            return parsed if isinstance(parsed, list) else []
        except Exception as e:
            print(f"Failed to parse lora_stack JSON: {e}")
            return []
    return lora_stack if isinstance(lora_stack, list) else []


def _is_lora_enabled(config):
    value = config.get("on", False)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in FALSE_LIKE_VALUES:
            return False
        if normalized in TRUE_LIKE_VALUES:
            return True
        return bool(normalized)
    return bool(value)


def _lora_stack_summary(lora_configs):
    total = len(lora_configs)
    active = 0
    zero_strength = 0
    strengths = []
    for config in lora_configs:
        if not isinstance(config, dict) or not _is_lora_enabled(config):
            continue
        strength = float(config.get("strength", 1.0))
        clip_strength = float(config.get("strengthTwo", strength))
        if strength == 0 and clip_strength == 0:
            zero_strength += 1
            continue
        active += 1
        strengths.append(round(strength, 4))
    return total, active, zero_strength, strengths


def enabled_model_loras(lora_stack):
    loras = []
    for i, config in enumerate(parse_lora_stack(lora_stack)):
        if not isinstance(config, dict):
            print(f"Skipping invalid LoRA config at index {i}: {config}")
            continue
        if not _is_lora_enabled(config):
            continue
        lora_name = config.get("lora")
        if not lora_name or lora_name == "None":
            continue
        strength_model = float(config.get("strength", 1.0))
        if strength_model == 0:
            continue
        loras.append((lora_name, strength_model))
    return loras

class MultiLoRAStack:
    """A powerful node to load multiple LoRAs with individual controls."""
    
    def __init__(self):
        # Use a single instance for caching benefits
        self.lora_loader = LoraLoader()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_stack": ("STRING", {
                    "multiline": True, 
                    "default": "[]",
                    "forceInput": False
                }),
            },
            "optional": {},
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("MODEL", "CLIP") 
    FUNCTION = "load_loras"
    CATEGORY = "loaders"

    def load_loras(self, model, clip, lora_stack="[]", **kwargs):
        """Loads multiple LoRAs based on the configuration."""
        # Parse lora_stack if it's a string
        lora_configs = parse_lora_stack(lora_stack)
        total, active, zero_strength, strengths = _lora_stack_summary(lora_configs)
        print(
            "\n=== MultiLoRAStack Debug ===\n"
            f"Parsed {total} LoRA config(s); active={active}; zero_strength={zero_strength}; "
            f"active_model_strengths={strengths}"
        )
        
        applied_count = 0
        current_model = model
        current_clip = clip
        
        # Process each LoRA configuration
        for i, config in enumerate(lora_configs):
            print(f"\n--- Processing LoRA slot {i+1} ---")
            
            if not isinstance(config, dict):
                print(f"Skipping invalid LoRA config at index {i}")
                continue
                
            # Check if this LoRA should be applied
            if not _is_lora_enabled(config):
                print("Skipping disabled LoRA")
                continue
                
            lora_name = config.get('lora')
            if not lora_name or lora_name == "None":
                print("Skipping empty/None LoRA")
                continue
                
            strength_model = float(config.get('strength', 1.0))
            strength_clip = float(config.get('strengthTwo', strength_model))
            
            # Skip if both strengths are 0
            if strength_model == 0 and strength_clip == 0:
                print("Skipping zero-strength LoRA")
                continue
            
            print(
                "Attempting to load LoRA "
                f"slot={i+1}, model_strength={strength_model}, clip_strength={strength_clip}"
            )
            
            # Apply the LoRA using ComfyUI's standard loader
            try:
                # Apply the LoRA to current model and clip
                current_model, current_clip = self.lora_loader.load_lora(
                    current_model, current_clip, lora_name, strength_model, strength_clip
                )
                applied_count += 1
                print(f"Successfully applied LoRA slot={i+1}")
                
            except Exception as e:
                print(f"Failed to load LoRA slot={i+1}: {type(e).__name__}: {str(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
        
        print(f"\n=== Summary ===")
        print(f"Applied {applied_count} out of {len(lora_configs)} LoRAs")
        print(f"===================\n")
        
        return (current_model, current_clip)


class MultiLoRAStackModelOnly:
    """A powerful node to load multiple LoRAs with individual controls (Model Only)."""
    
    def __init__(self):
        # Use a single instance for caching benefits
        self.lora_loader = LoraLoaderModelOnly()
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "lora_stack": ("STRING", {
                    "multiline": True, 
                    "default": "[]",
                    "forceInput": False
                }),
            },
            "optional": {},
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("MODEL",) 
    FUNCTION = "load_loras"
    CATEGORY = "loaders"

    def load_loras(self, model, lora_stack="[]", **kwargs):
        """Loads multiple LoRAs based on the configuration (Model Only)."""
        # Parse lora_stack if it's a string
        lora_configs = parse_lora_stack(lora_stack)
        total, active, zero_strength, strengths = _lora_stack_summary(lora_configs)
        print(
            "\n=== MultiLoRAStackModelOnly Debug ===\n"
            f"Parsed {total} LoRA config(s); active={active}; zero_strength={zero_strength}; "
            f"active_model_strengths={strengths}"
        )
        
        applied_count = 0
        current_model = model
        
        # Process each LoRA configuration
        for i, config in enumerate(lora_configs):
            print(f"\n--- Processing LoRA slot {i+1} ---")
            
            if not isinstance(config, dict):
                print(f"Skipping invalid LoRA config at index {i}")
                continue
                
            # Check if this LoRA should be applied
            if not _is_lora_enabled(config):
                print("Skipping disabled LoRA")
                continue
                
            lora_name = config.get('lora')
            if not lora_name or lora_name == "None":
                print("Skipping empty/None LoRA")
                continue
                
            strength_model = float(config.get('strength', 1.0))
            
            # Skip if strength is 0
            if strength_model == 0:
                print("Skipping zero-strength LoRA")
                continue
            
            print(f"Attempting to load LoRA slot={i+1}, model_strength={strength_model}")
            
            # Apply the LoRA using ComfyUI's model-only loader
            try:
                # FIXED: Use the correct method name
                current_model, = self.lora_loader.load_lora_model_only(
                    current_model, lora_name, strength_model
                )
                applied_count += 1
                print(f"Successfully applied LoRA slot={i+1} (Model Only)")
                
            except Exception as e:
                print(f"Failed to load LoRA slot={i+1}: {type(e).__name__}: {str(e)}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
        
        print(f"\n=== Summary ===")
        print(f"Applied {applied_count} out of {len(lora_configs)} LoRAs (Model Only)")
        print(f"===================\n")
        
        return (current_model,)


class MultiLoRAStackToPreLora:
    """Converts the Multi LoRA Stack JSON into INT8-Fast PRE_LORA data."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_stack": ("STRING", {
                    "multiline": True,
                    "default": "[]",
                    "forceInput": False
                }),
            },
            "optional": {},
        }

    RETURN_TYPES = ("PRE_LORA",)
    RETURN_NAMES = ("PRE_LORA",)
    FUNCTION = "build_pre_lora"
    CATEGORY = "loaders"

    def build_pre_lora(self, lora_stack="[]", **kwargs):
        pre_loras = [
            {"lora_name": lora_name, "lora_strength": round(strength_model, 2)}
            for lora_name, strength_model in enabled_model_loras(lora_stack)
        ]
        print(f"MultiLoRAStackToPreLora: prepared {len(pre_loras)} enabled LoRA(s)")
        return (pre_loras,)


# Register the nodes
NODE_CLASS_MAPPINGS = {
    "MultiLoRAStack": MultiLoRAStack,
    "MultiLoRAStackModelOnly": MultiLoRAStackModelOnly,
    "MultiLoRAStackToPreLora": MultiLoRAStackToPreLora
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiLoRAStack": "Multi LoRA Stack",
    "MultiLoRAStackModelOnly": "Multi LoRA Stack (Model Only)",
    "MultiLoRAStackToPreLora": "Multi LoRA Stack to INT8 Pre-Lora"
}
