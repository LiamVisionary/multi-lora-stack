import json

from multi_lora_stack import _lora_stack_summary, enabled_model_loras


def test_string_false_like_flags_do_not_enable_loras():
    stack = json.dumps([
        {"on": "false", "lora": "disabled-string.safetensors", "strength": 1.0},
        {"on": "0", "lora": "disabled-zero.safetensors", "strength": 1.0},
        {"on": "off", "lora": "disabled-off.safetensors", "strength": 1.0},
        {"on": "true", "lora": "enabled-string.safetensors", "strength": 0.5},
    ])

    assert enabled_model_loras(stack) == [("enabled-string.safetensors", 0.5)]
    assert _lora_stack_summary(json.loads(stack)) == (4, 1, 0, [0.5])
