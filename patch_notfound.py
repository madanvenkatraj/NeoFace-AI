import re

with open('app/not-found.tsx', 'w') as f:
    f.write('''import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-zinc-950 text-white">
      <h2 className="text-4xl font-bold mb-4">404 - Not Found</h2>
      <p className="text-slate-400 mb-8">The page you are looking for does not exist.</p>
      <Link href="/" className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded transition-colors">
        Return Home
      </Link>
    </div>
  )
}
''')

