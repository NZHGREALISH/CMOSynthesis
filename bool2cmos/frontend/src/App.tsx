import React, { useMemo, useState } from 'react';

import { synthesize, toCMOSNetwork, SynthesisResponse } from './api/synthesize';
import { CMOSNetwork } from './types/network';
import { ExpressionInput } from './components/ExpressionInput';
import { ErrorPanel } from './components/ErrorPanel';
import { StepExplanation } from './components/StepExplanation';
import { TransistorCount } from './components/TransistorCount';
import { PDNView } from './components/PDNView';
import { PUNView } from './components/PUNView';

export default function App() {
  const [expr, setExpr] = useState<string>('A & (B | !C)');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SynthesisResponse | null>(null);

  const cmos: CMOSNetwork | null = useMemo(() => {
    if (!result) return null;
    return toCMOSNetwork(result);
  }, [result]);

  async function onSynthesize() {
    setError(null);
    setLoading(true);
    try {
      const resp = await synthesize(expr);
      setResult(resp);
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Bool → CMOS</h1>
        <p className="subtle">
          Enter a boolean expression using <code>!</code>, <code>&</code>, <code>|</code> (or <code>+</code>), and parentheses. Shorthand is supported: <code>AB</code> = <code>A&amp;B</code>.
        </p>
      </header>

      <ExpressionInput value={expr} onChange={setExpr} onSubmit={onSynthesize} disabled={loading} />
      <ErrorPanel message={error} />

      {result && (
        <>
          <TransistorCount count={result.steps.count} />
          <StepExplanation steps={result.steps} />
        </>
      )}

      {cmos && (
        <div className="grid">
          <PUNView network={cmos.pun} />
          <PDNView network={cmos.pdn} />
        </div>
      )}
    </div>
  );
}
