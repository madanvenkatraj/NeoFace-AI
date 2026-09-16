import type {Metadata} from 'next';
import { Outfit } from 'next/font/google';
import './globals.css';
import GlobalChat from '@/components/GlobalChat';
import { FirebaseProvider } from '@/components/FirebaseProvider';

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
        <FirebaseProvider>
          <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
            <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-cyan-600/10 blur-[120px] mix-blend-screen" />
            <div className="absolute bottom-[-10%] right-[-5%] w-[50vw] h-[50vw] rounded-full bg-violet-600/10 blur-[150px] mix-blend-screen" />
            <div className="absolute top-[40%] left-[60%] w-[30vw] h-[30vw] rounded-full bg-indigo-600/10 blur-[100px] mix-blend-screen" />
          </div>
          
          <div className="relative z-10 flex flex-col min-h-screen">
            {children}
          </div>
          
          <GlobalChat />
        </FirebaseProvider>
      </body>
    </html>
  );
}
