import React, { useState } from 'react';
import { Search, Loader2, Image as ImageIcon } from 'lucide-react';

interface SearchCelebrityProps {
  onSelect: (url: string) => void;
}

export default function SearchCelebrity({ onSelect }: SearchCelebrityProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<{url: string, title: string}[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setResults([]);

    try {
      const res = await fetch('/api/search-celebrity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      if (!res.ok) {
        throw new Error('Search failed');
      }

      const data = await res.json();
      if (data.results && data.results.length > 0) {
        setResults(data.results);
      } else {
        setError('No images found.');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during search.');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 mt-4">
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a celebrity face..."
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={isSearching || !query.trim()}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl text-sm font-semibold shadow-sm flex items-center gap-2 transition-colors"
        >
          {isSearching ? <Loader2 className="animate-spin" size={16} /> : 'Search'}
        </button>
      </form>

      {error && <p className="text-red-500 text-xs mb-4">{error}</p>}

      {results.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 overflow-y-auto max-h-48 custom-scrollbar">
          {results.map((res, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onSelect(res.url)}
              className="relative aspect-square bg-slate-200 rounded-lg overflow-hidden border border-slate-300 hover:border-indigo-500 hover:ring-2 hover:ring-indigo-500/50 transition-all group"
              title={res.title}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={res.url} alt={res.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                <span className="text-white text-xs font-bold px-2 py-1 bg-black/60 rounded">Select</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
