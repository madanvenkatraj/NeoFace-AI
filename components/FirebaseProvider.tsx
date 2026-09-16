'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth, getUserPreferences, saveUserPreferences } from '../lib/firebase';
import { useWorkspaceStore } from '../lib/store';

interface AuthContextType {
  user: User | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true });

export function FirebaseProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { present, loadState } = useWorkspaceStore();

  // Load user data on login
  useEffect(() => { // eslint-disable-next-line react-hooks/exhaustive-deps
    const unsubscribe = onAuthStateChanged(auth, async (u) => {
      if (u) {
        setUser(u);
        const prefs = await getUserPreferences(u.uid);
        if (prefs) {
          loadState({
            ...present,
            resolution: prefs.resolution || present.resolution,
            frameRate: prefs.frameRate || present.frameRate,
            compression: prefs.compression || present.compression,
          });
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    });
    return () => unsubscribe();
  }, []); // Only run once on mount

  // Sync preferences to Firestore when they change
  useEffect(() => { // eslint-disable-next-line react-hooks/exhaustive-deps
    if (user && !loading) {
      const prefsToSave = {
        resolution: present.resolution,
        frameRate: present.frameRate,
        compression: present.compression,
      };
      // Debounce saving slightly if needed, but for now just save
      saveUserPreferences(user.uid, prefsToSave).catch(console.error);
    }
  }, [user, loading, present.resolution, present.frameRate, present.compression]);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
