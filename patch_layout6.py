import re

with open('app/layout.tsx', 'r') as f:
    content = f.read()

content = content.replace("<html ", "<html\n      ").replace("</div>", "</html>")
# oh wait, the issue is that it says "Unexpected token `html`. Expected jsx identifier"
# that means the previous replace broke it. Let me just write the file out fully to be safe.

with open('app/layout.tsx', 'w') as f:
    f.write('''import type {Metadata} from 'next';
import { Outfit } from 'next/font/google';
import './globals.css';
import SystemMonitor from '@/components/SystemMonitor';

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'NeoFace AI',
  description: 'High-performance photo and video face swapping without watermarks.',
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en" className={`${outfit.variable} dark`}>
      <body className="bg-zinc-950 text-slate-100 min-h-screen font-sans selection:bg-cyan-500/30 overflow-x-hidden antialiased" suppressHydrationWarning>
        <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
          <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-cyan-600/10 blur-[120px] mix-blend-screen" />
          <div className="absolute bottom-[-10%] right-[-5%] w-[50vw] h-[50vw] rounded-full bg-violet-600/10 blur-[150px] mix-blend-screen" />
          <div className="absolute top-[40%] left-[60%] w-[30vw] h-[30vw] rounded-full bg-indigo-600/10 blur-[100px] mix-blend-screen" />
        </div>
        
        <div className="relative z-10 flex flex-col min-h-screen">
          {children}
        </div>
        
        <SystemMonitor />
      </body>
    </html>
  );
}
''')
