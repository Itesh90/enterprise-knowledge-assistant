import React from 'react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

type Props = { onSend: (text: string) => void; disabled?: boolean };

export function Composer({ onSend, disabled }: Props) {
  const [text, setText] = React.useState('');
  return (
    <form
      className="flex items-center gap-3 glass rounded-xl p-4 shadow-lg animate-fade-in"
      onSubmit={(e) => {
        e.preventDefault();
        const t = text.trim();
        if (t) onSend(t);
        setText('');
      }}
    >
      <Input value={text} onChange={(e) => setText(e.target.value)} placeholder="💬 Ask a question..." className="flex-1" />
      <Button type="submit" disabled={disabled || text.trim().length === 0}>
        {disabled ? '⏳' : '🚀 Send'}
      </Button>
    </form>
  );
}


