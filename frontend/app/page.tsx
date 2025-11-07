"use client";
import Link from 'next/link';
import { MessageList } from '../components/chat/MessageList';
import { Composer } from '../components/chat/Composer';
import { useQueryApi } from '../lib/client';
import { useChatStore } from '../lib/store';
import { MetricsBar } from '../components/MetricsBar';
import { SourcesPanel } from '../components/SourcesPanel';

export default function Page() {
  const { mutateAsync, isPending, data } = useQueryApi();
  const messages = useChatStore((s) => s.messages);
  const append = useChatStore((s) => s.append);
  return (
    <main className="grid grid-cols-1 gap-6 md:grid-cols-[1fr_320px] animate-fade-in">
      <section className="space-y-6">
        <div className="flex items-center justify-between glass rounded-xl p-4 shadow-lg">
          <h1 className="text-3xl font-bold gradient-text">✨ Enterprise Knowledge Assistant</h1>
          <nav className="space-x-4 text-sm flex items-center">
            <Link href="/ingest" className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium hover:from-purple-600 hover:to-pink-600 transition-all duration-300 transform hover:scale-105">
              📥 Ingest
            </Link>
            <Link href="/search" className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105">
              🔍 Search
            </Link>
          </nav>
        </div>
        <MessageList messages={messages} />
        <Composer
          disabled={isPending}
          onSend={async (text) => {
            append({ role: 'user', content: text, ts: Date.now() });
            try {
              const res = await mutateAsync({ query: text, top_k: 20, k_final: 5 });
              append({ role: 'assistant', content: res.answer, ts: Date.now() });
            } catch (error) {
              const errorMsg = error instanceof Error ? error.message : 'Failed to get response';
              append({ role: 'assistant', content: `Error: ${errorMsg}`, ts: Date.now() });
            }
          }}
        />
        <MetricsBar
          latency_ms={data?.telemetry?.latency_ms}
          tokens_prompt={data?.telemetry?.tokens_prompt}
          tokens_completion={data?.telemetry?.tokens_completion}
          cost_usd={data?.telemetry?.cost_usd}
          confidence={data?.confidence}
        />
      </section>
      <aside className="space-y-4">
        <SourcesPanel
          query={messages.filter((m) => m.role === 'user').slice(-1)[0]?.content}
          sources={(data?.snippets || []).map((s: any) => ({ rank: s.rank, title: s.title, url: s.url, score: s.score, text: s.text }))}
        />
      </aside>
    </main>
  );
}


