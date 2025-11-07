type Props = { latency_ms?: number; tokens_prompt?: number; tokens_completion?: number; cost_usd?: number; confidence?: number };

export function MetricsBar({ latency_ms, tokens_prompt, tokens_completion, cost_usd, confidence }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3 glass rounded-xl p-4 shadow-lg animate-fade-in">
      {latency_ms !== undefined && (
        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-blue-400 to-cyan-400 text-white text-xs font-semibold">
          ⚡ {latency_ms}ms
        </span>
      )}
      {tokens_prompt !== undefined && (
        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 text-white text-xs font-semibold">
          📝 {tokens_prompt}
        </span>
      )}
      {tokens_completion !== undefined && (
        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-green-400 to-emerald-400 text-white text-xs font-semibold">
          ✨ {tokens_completion}
        </span>
      )}
      {cost_usd !== undefined && (
        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-yellow-400 to-orange-400 text-white text-xs font-semibold">
          💰 ${cost_usd?.toFixed(4)}
        </span>
      )}
      {confidence !== undefined && (
        <span className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${
          confidence < 0.4 
            ? 'bg-gradient-to-r from-red-400 to-red-600' 
            : confidence < 0.7 
            ? 'bg-gradient-to-r from-yellow-400 to-orange-400' 
            : 'bg-gradient-to-r from-green-400 to-emerald-400'
        }`}>
          🎯 {(confidence * 100).toFixed(0)}%
        </span>
      )}
    </div>
  );
}


