import json
import os

with open(r'C:\Users\armoo\.openclaw\openclaw.json', 'r') as f:
    config_content = f.read()

payload = {
  "type": "web_service",
  "name": "openclaw-cloud-backup",
  "ownerId": "tea-d6d0uh4tgctc73es86r0",
  "repo": "https://github.com/openclaw/openclaw",
  "autoDeploy": "yes",
  "serviceDetails": {
    "env": "docker",
    "plan": "free",
    "region": "oregon",
    "numInstances": 1
  },
  "envVars": [
    {
      "key": "PORT",
      "value": "8080"
    },
    {
      "key": "OPENCLAW_JSON",
      "value": config_content
    }
  ]
}

with open(r'C:\Users\armoo\.openclaw\workspace\render_payload_final.json', 'w') as f:
    json.dump(payload, f)
