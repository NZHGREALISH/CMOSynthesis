import React, { useMemo, useState } from 'react';

type PendingSelection = { start: number; end: number };

function uniq<T>(items: T[]): T[] {
  return Array.from(new Set(items));
}

function detectVariables(expr: string): string[] {
  const tokens = expr.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? [];
  const vars: string[] = [];
  for (const raw of tokens) {
    const upper = raw.toUpperCase();
    if (upper === 'AND' || upper === 'OR' || upper === 'NOT') continue;
    if (/^[A-Z]$/.test(upper)) {
      vars.push(upper);
      continue;
    }
    if (/^[A-Z]+$/.test(upper)) {
      for (const ch of upper) vars.push(ch);
    }
  }
  return uniq(vars).sort();
}

function readBooleanPref(): boolean {
  try {
    const raw = localStorage.getItem('lectureNotation');
    if (raw === null) return true;
    return raw === 'true';
  } catch {
    return true;
  }
}

function writeBooleanPref(value: boolean) {
  try {
    localStorage.setItem('lectureNotation', String(value));
  } catch {
    // ignore
  }
}

export function BooleanSymbolBar({
  inputRef,
  value,
  onChange,
  onRequestSelection,
  disabled,
}: {
  inputRef: React.RefObject<HTMLInputElement>;
  value: string;
  onChange: (next: string) => void;
  onRequestSelection: (sel: PendingSelection) => void;
  disabled?: boolean;
}) {
  const [lectureNotation, setLectureNotation] = useState<boolean>(() => readBooleanPref());

  const variables = useMemo(() => {
    const base = ['A', 'B', 'C', 'D', 'E', 'F'];
    const detected = detectVariables(value);
    return uniq([...base, ...detected]).filter((v) => /^[A-Z]$/.test(v));
  }, [value]);

  const labels = useMemo(() => {
    if (lectureNotation) {
      return { and: '·', or: '+', not: 'Ā', overbar: '¯' };
    }
    return { and: '&', or: '|', not: '!', overbar: 'Overbar' };
  }, [lectureNotation]);

  function replaceRange(start: number, end: number, replacement: string, nextCaret: number) {
    const next = value.slice(0, start) + replacement + value.slice(end);
    onChange(next);
    onRequestSelection({ start: nextCaret, end: nextCaret });
  }

  function withInputSelection(fn: (start: number, end: number) => void) {
    const el = inputRef.current;
    if (!el) return;
    const start = el.selectionStart ?? value.length;
    const end = el.selectionEnd ?? value.length;
    fn(start, end);
  }

  function insertToken(token: string) {
    withInputSelection((start, end) => {
      replaceRange(start, end, token, start + token.length);
    });
  }

  function insertBinaryOperator(op: '&' | '|') {
    withInputSelection((start, end) => {
      const before = value.slice(0, start);
      const after = value.slice(end);
      const needsLeftSpace = before.length > 0 && !/\s$/.test(before) && !/[([{]$/.test(before);
      const needsRightSpace = after.length > 0 && !/^\s/.test(after) && !/^[)\]}]/.test(after);
      const replacement = `${needsLeftSpace ? ' ' : ''}${op}${needsRightSpace ? ' ' : ''}`;
      replaceRange(start, end, replacement, start + replacement.length);
    });
  }

  function insertNot() {
    insertToken('!');
  }

  function applyOverbar() {
    withInputSelection((start, end) => {
      if (start === end) {
        const replacement = '!()';
        const caret = start + 2;
        replaceRange(start, end, replacement, caret);
        return;
      }
      const selected = value.slice(start, end);
      const replacement = `!(${selected})`;
      replaceRange(start, end, replacement, start + replacement.length);
    });
  }

  function toggleLectureNotation(checked: boolean) {
    setLectureNotation(checked);
    writeBooleanPref(checked);
  }

  const preventFocusSteal = (e: React.MouseEvent) => e.preventDefault();

  return (
    <div className="symbolBar" aria-label="Lecture-style boolean toolbar">
      <div className="symbolBarRow">
        <div className="symbolBarGroup" aria-label="Variable inserts">
          {variables.map((v) => (
            <button
              key={v}
              type="button"
              className="symbolButton"
              onMouseDown={preventFocusSteal}
              onClick={() => insertToken(v)}
              disabled={disabled}
              aria-label={`Insert ${v}`}
              title={`Insert ${v}`}
            >
              {v}
            </button>
          ))}
        </div>

        <div className="symbolBarGroup" aria-label="Operator inserts">
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={() => insertBinaryOperator('&')}
            disabled={disabled}
            aria-label="Insert AND"
            title="Insert AND"
          >
            {labels.and}
          </button>
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={() => insertBinaryOperator('|')}
            disabled={disabled}
            aria-label="Insert OR"
            title="Insert OR"
          >
            {labels.or}
          </button>
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={insertNot}
            disabled={disabled}
            aria-label="Insert NOT"
            title="Insert NOT"
          >
            {labels.not}
          </button>
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={applyOverbar}
            disabled={disabled}
            aria-label="Apply overbar (wrap selection with !())"
            title="Wrap selection: !(...)"
          >
            {labels.overbar}
          </button>
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={() => insertToken('(')}
            disabled={disabled}
            aria-label="Insert ("
            title="Insert ("
          >
            (
          </button>
          <button
            type="button"
            className="symbolButton"
            onMouseDown={preventFocusSteal}
            onClick={() => insertToken(')')}
            disabled={disabled}
            aria-label="Insert )"
            title="Insert )"
          >
            )
          </button>
        </div>

        <label className="symbolToggle" title="Toggle button labels between lecture symbols and ASCII operators">
          <input
            type="checkbox"
            checked={lectureNotation}
            onChange={(e) => toggleLectureNotation(e.target.checked)}
            disabled={disabled}
          />
          <span>Lecture notation</span>
        </label>
      </div>

      <div className="symbolHint">Lecture symbols are mapped to &amp;, |, ! for parsing.</div>
    </div>
  );
}
