import { create } from 'zustand';

export type ChatMessage = { role: 'user' | 'assistant'; content: string; ts: number };

type ChatState = {
  messages: ChatMessage[];
  append: (m: ChatMessage) => void;
  clear: () => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  append: (m) => set((s) => ({ messages: [...s.messages, m] })),
  clear: () => set({ messages: [] }),
}));


