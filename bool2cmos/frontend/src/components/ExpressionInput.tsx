import React, { useCallback } from 'react';

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
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Example: A & (B | !C)"
          disabled={disabled}
        />
      </label>
      <button className="button" type="submit" disabled={disabled}>
        {disabled ? 'Synthesizing…' : 'Synthesize'}
      </button>
    </form>
  );
}
