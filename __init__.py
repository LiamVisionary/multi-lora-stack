"""
Multi LoRA Stack - A standalone ComfyUI custom node for managing multiple LoRAs
"""

# Import from the single combined file. The fallback keeps direct pytest
# collection working when this hyphenated folder is imported without a package.
try:
    from .multi_lora_stack import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError:
    from multi_lora_stack import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Web directory for JavaScript files
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
