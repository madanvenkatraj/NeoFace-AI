import json

with open("firebase-blueprint.json", "r") as f:
    data = json.load(f)

data["entities"]["SwapResult"] = {
    "title": "SwapResult",
    "description": "Result of a face swap operation",
    "type": "object",
    "properties": {
        "id": { "type": "string", "maxLength": 128, "pattern": "^[a-zA-Z0-9_\\-]+$" },
        "userId": { "type": "string", "maxLength": 128, "pattern": "^[a-zA-Z0-9_\\-]+$" },
        "resultUrl": { "type": "string", "maxLength": 1024 },
        "thumbnailUrl": { "type": "string", "maxLength": 1024 },
        "isVideo": { "type": "boolean" },
        "qualityMode": { "type": "string", "maxLength": 20 },
        "facesSwapped": { "type": "number" },
        "createdAt": { "type": "number" }
    },
    "required": ["id", "userId", "resultUrl", "isVideo", "createdAt"]
}

data["firestore"]["/users/{userId}/swapHistory/{resultId}"] = {
    "schema": { "$ref": "#/entities/SwapResult" },
    "description": "User's face swap history"
}

with open("firebase-blueprint.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated blueprint")
