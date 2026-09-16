'use client';

import { useState } from 'react';
import { Save, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from './FirebaseProvider';
import { saveProjectHistory } from '../lib/firebase';
import { useWorkspaceStore } from '../lib/store';

export default function CloudSyncButton() {
  const { user } = useAuth();
  const { present } = useWorkspaceStore();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!user) return null;

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    
    // Create a unique project ID or just use timestamp
    const projectId = `proj_${Date.now()}`;
    
    await saveProjectHistory(user.uid, projectId, {
      name: `Project ${new Date().toLocaleDateString()}`,
      resolution: present.resolution,
      frameRate: present.frameRate,
      compression: present.compression,
    });
    
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <button 
      onClick={handleSave} 
      disabled={saving}
      className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2 rounded-full transition-colors border border-white/10"
      title="Save Project History to Cloud"
    >
      {saving ? (
        <Loader2 size={16} className="animate-spin text-cyan-400" />
      ) : saved ? (
        <CheckCircle2 size={16} className="text-emerald-400" />
      ) : (
        <Save size={16} className="text-slate-300" />
      )}
      {saving ? 'Saving...' : saved ? 'Saved' : 'Save Project'}
    </button>
  );
}
