import re

with open('backend/main.py', 'r') as f:
    content = f.read()

# Make sure it's imported (though we might just be able to import it directly since db is imported)
if "from db import get_idle_status" not in content:
    content = content.replace("from db import init_db", "from db import init_db, get_idle_status")

new_endpoint = """
@app.get("/api/system/idle")
async def get_system_idle():
    try:
        from db import get_idle_status
        return get_idle_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

if "/api/system/idle" not in content:
    content = content.replace("@app.get(\"/api/system/metrics\")", new_endpoint + "\n@app.get(\"/api/system/metrics\")")

with open('backend/main.py', 'w') as f:
    f.write(content)
