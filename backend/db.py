import sqlite3
import os
import json
import time

OUTPUT_DIR = "/app/data/outputs"
DB_PATH = os.path.join(OUTPUT_DIR, "jobs.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (task_id TEXT PRIMARY KEY,
                  filename TEXT,
                  params TEXT,
                  state TEXT,
                  progress INTEGER,
                  frames_processed INTEGER,
                  created_at REAL,
                  updated_at REAL)''')
    conn.commit()
    conn.close()

def create_job(task_id, filename, params):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (task_id, filename, json.dumps(params), 'QUEUED', 0, 0, time.time(), time.time()))
    conn.commit()
    conn.close()

def update_job_state(task_id, state, progress=None, frames_processed=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updates = ["state = ?", "updated_at = ?"]
    params = [state, time.time()]
    
    if progress is not None:
        updates.append("progress = ?")
        params.append(progress)
        
    if frames_processed is not None:
        updates.append("frames_processed = ?")
        params.append(frames_processed)
        
    params.append(task_id)
    
    c.execute(f"UPDATE jobs SET {', '.join(updates)} WHERE task_id = ?", params)
    conn.commit()
    conn.close()

def get_job(task_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE task_id = ?", (task_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_idle_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs WHERE state IN ('QUEUED', 'PROGRESS')")
    active_count = c.fetchone()[0]
    
    if active_count > 0:
        conn.close()
        return {"is_idle": False, "idle_minutes": 0, "active_jobs": active_count}
        
    c.execute("SELECT MAX(updated_at) FROM jobs")
    row = c.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return {"is_idle": True, "idle_minutes": 999, "active_jobs": 0} # No jobs ever
        
    last_activity = row[0]
    idle_minutes = (time.time() - last_activity) / 60.0
    return {"is_idle": True, "idle_minutes": idle_minutes, "active_jobs": 0}
