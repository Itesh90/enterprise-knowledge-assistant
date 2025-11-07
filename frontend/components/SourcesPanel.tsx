import React from 'react';

type Source = { rank: number; title: string; url: string; section?: string; score?: number; text?: string };

type Props = { sources: Source[]; query?: string };

function highlight(text: string, query?: string) {
  if (!query) return text;
  try {
    const q = query.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`(${q})`, 'ig');
    return text.replace(re, '<mark>$1</mark>');
  } catch {
    return text;
  }
}

export function SourcesPanel({ sources, query }: Props) {
  const [open, setOpen] = React.useState<number | null>(null);
  return (
    <div className="space-y-3 animate-fade-in">
      <div className="font-bold text-lg gradient-text">Sources</div>
      <ul className="space-y-3 text-sm">
        {sources.map((s, idx) => (
          <li 
            key={s.rank} 
            className="rounded-xl bg-gradient-to-br from-white to-purple-50 border-2 border-purple-200 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-[1.02] animate-slide-in-up"
            style={{ animationDelay: `${idx * 0.1}s` }}
          >
            <div className="flex items-center justify-between px-4 py-3">
              <button 
                className="text-left text-black font-medium hover:text-purple-600 transition-colors duration-200 flex-1" 
                onClick={() => setOpen(open === s.rank ? null : s.rank)}
              >
                <span className="inline-block w-6 h-6 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-bold flex items-center justify-center mr-2">
                  {s.rank}
                </span>
                {s.title}
              </button>
              {typeof s.score === 'number' && (
                <span className="px-3 py-1 rounded-full bg-gradient-to-r from-green-400 to-blue-400 text-white text-xs font-semibold">
                  {s.score.toFixed(3)}
                </span>
              )}
            </div>
            {open === s.rank && (
              <div className="border-t border-purple-200 px-4 py-3 bg-gradient-to-br from-white to-blue-50 animate-fade-in">
                {s.url && (
                  <a 
                    className="inline-block mb-2 px-3 py-1 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-200 transform hover:scale-105" 
                    href={s.url} 
                    target="_blank" 
                    rel="noreferrer"
                  >
                    🔗 Open source
                  </a>
                )}
                {s.text && (
                  <div className="prose prose-sm mt-2 max-w-none text-black leading-relaxed" dangerouslySetInnerHTML={{ __html: highlight(s.text, query) }} />
                )}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}


