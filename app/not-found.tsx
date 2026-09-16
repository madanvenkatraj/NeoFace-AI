import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
      <h2 className="text-3xl font-bold mb-4">404 - Page Not Found</h2>
      <p className="text-zinc-400 mb-6">Could not find the requested resource.</p>
      <Link 
        href="/"
        className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
      >
        Return Home
      </Link>
    </div>
  );
}
