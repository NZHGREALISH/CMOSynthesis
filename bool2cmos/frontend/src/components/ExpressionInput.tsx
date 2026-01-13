import React, { useCallback, useEffect, useRef } from 'react';

import { BooleanSymbolBar } from './BooleanSymbolBar';

type PendingSelection = { start: number; end: number };

export function ExpressionInput({
  value,
  onChange,
  onSubmit,
  disabled,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const pendingSelectionRef = useRef<PendingSelection | null>(null);

  useEffect(() => {
    const pending = pendingSelectionRef.current;
    if (!pending) return;
    pendingSelectionRef.current = null;
    const el = inputRef.current;
    if (!el) return;
    el.focus();
    el.setSelectionRange(pending.start, pending.end);
  }, [value]);

  const submit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      onSubmit();
    },
    [onSubmit]
  );

  return (
    <form className="card" onSubmit={submit}>
      <label className="label">
        Expression
        <input
          className="input"
          ref={inputRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Example: A(B+!C) or A & (B | !C)"
          disabled={disabled}
        />
        <BooleanSymbolBar
          inputRef={inputRef}
          value={value}
          onChange={onChange}
          onRequestSelection={(sel) => {
            pendingSelectionRef.current = sel;
          }}
          disabled={disabled}
        />
      </label>
      <button className="button" type="submit" disabled={disabled}>
        {disabled ? 'Synthesizing…' : 'Synthesize'}
      </button>
    </form>
  );
}
