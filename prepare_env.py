import json

with open(r'C:\Users\armoo\.openclaw\openclaw.json', 'r') as f:
    config_content = f.read()

env_vars = [
    {"key": "NODE_OPTIONS", "value": "--max-old-space-size=400"},
    {"key": "PORT", "value": "8080"},
    {"key": "OPENCLAW_JSON", "value": config_content}
]

with open(r'C:\Users\armoo\.openclaw\workspace\render_env_final.json', 'w') as f:
    json.dump(env_vars, f)
