'use client';

import { useState, useEffect } from 'react';
import { auth, signIn, logOut } from '../lib/firebase';
import { onAuthStateChanged, User } from 'firebase/auth';
import Image from 'next/image';
import { LogOut, UserCircle } from 'lucide-react';

export default function AuthButton() {
  const [user, setUser] = useState<User | null>(null);
  
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
    });
    return () => unsubscribe();
  }, []);

  if (user) {
    return (
      <div className="flex items-center gap-3 bg-white/5 rounded-full pl-2 pr-4 py-1.5 border border-white/10">
        <Image src={user.photoURL || '/placeholder-avatar.png'} alt="avatar" width={24} height={24} className="rounded-full" referrerPolicy="no-referrer" />
        <span className="text-xs font-semibold text-slate-200">{user.displayName?.split(' ')[0]}</span>
        <button onClick={logOut} className="ml-2 text-slate-400 hover:text-white" title="Sign out">
          <LogOut size={14} />
        </button>
      </div>
    );
  }

  return (
    <button onClick={signIn} className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold px-4 py-2 rounded-full transition-colors">
      <UserCircle size={16} /> Sign In
    </button>
  );
}
