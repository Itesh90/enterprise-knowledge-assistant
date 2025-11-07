"use client";
import React from 'react';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import { useQueryApi } from '../../../lib/client';

export default function SearchPage() {
  const [q, setQ] = React.useState('');
  const { mutateAsync, data, isPending } = useQueryApi();
  return (
    <main className="space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold gradient-text">🔍 Semantic Search</h1>
      <form
        className="flex gap-3 glass rounded-xl p-4 shadow-lg"
        onSubmit={async (e) => {
          e.preventDefault();
          if (!q.trim()) return;
          await mutateAsync({ query: q, top_k: 20, k_final: 10 });
        }}
      >
        <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search..." className="flex-1" />
        <Button type="submit" disabled={isPending || q.trim().length === 0}>
          {isPending ? 'Searching...' : '🔎 Search'}
        </Button>
      </form>
      <ul className="space-y-3">
        {(data?.snippets || []).map((s: any, idx: number) => (
          <li 
            key={s.rank} 
            className="rounded-xl bg-gradient-to-br from-white via-purple-50 to-pink-50 border-2 border-purple-200 p-4 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] animate-slide-in-up"
            style={{ animationDelay: `${idx * 0.05}s` }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <span className="inline-block w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm font-bold flex items-center justify-center">
                  {s.rank}
                </span>
                <div className="font-semibold text-black text-base">{s.title}</div>
              </div>
              {typeof s.score === 'number' && (
                <span className="px-3 py-1 rounded-full bg-gradient-to-r from-green-400 to-blue-400 text-white text-xs font-semibold">
                  {s.score.toFixed(3)}
                </span>
              )}
            </div>
            <a 
              className="inline-block mt-2 px-3 py-1 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105" 
              href={s.url || '#'} 
              target="_blank" 
              rel="noreferrer"
            >
              🔗 {s.url || 'Open Source'}
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}


