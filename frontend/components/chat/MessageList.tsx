import React from 'react';
import ReactMarkdown from 'react-markdown';
import hljs from 'highlight.js';
import { ChatMessage } from '../../lib/store';

type Props = { messages: ChatMessage[] };

export function MessageList({ messages }: Props) {
  React.useEffect(() => {
    document.querySelectorAll('pre code').forEach((el) => hljs.highlightElement(el as HTMLElement));
  }, [messages]);
  return (
    <div className="space-y-4">
      {messages.map((m, i) => (
        <div 
          key={i} 
          className={`${m.role === 'user' ? 'text-right' : 'text-left'} animate-slide-in-up`}
          style={{ animationDelay: `${i * 0.1}s` }}
        >
          <div className={`inline-block max-w-[75%] rounded-xl px-4 py-3 text-sm shadow-lg transition-all duration-300 hover:shadow-xl ${
            m.role === 'user' 
              ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white border-2 border-blue-400' 
              : 'bg-gradient-to-br from-white to-blue-50 text-black border-2 border-purple-200 hover:border-purple-400'
          }`}>
            <ReactMarkdown className={m.role === 'user' ? 'text-white' : 'text-black'}>{m.content}</ReactMarkdown>
          </div>
        </div>
      ))}
    </div>
  );
}


