import React, { useMemo, useState } from 'react';
import { calculateLayout } from './layout/TreeLayout';
import { NetworkNode } from './types/network';
import { ParallelBlock } from './render/ParallelBlock';
import { SeriesBlock } from './render/SeriesBlock';
import { Transistor } from './render/Transistor';
import { synthesize } from './api/synthesize';
import './styles/cmos.css';

function NetworkSvg({ title, node }: { title: string; node: NetworkNode }) {
  const layout = useMemo(() => calculateLayout(node), [node]);

  const renderNode = (l: any): React.ReactNode => {
    if (l.node.type === 'transistor') return <Transistor layout={l} />;
    if (l.node.type === 'series') return <SeriesBlock layout={l} renderNode={renderNode} />;
    if (l.node.type === 'parallel') return <ParallelBlock layout={l} renderNode={renderNode} />;
    return null;
  };

  return (
    <div className="panel">
      <div className="panel-title">{title}</div>
      <svg width={layout.width} height={layout.height} viewBox={`0 0 ${layout.width} ${layout.height}`}>
        {renderNode(layout as any)}
      </svg>
    </div>
  );
}

export default function App() {
  const [expr, setExpr] = useState('A & (B | C)');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    steps: {
      simplify: string;
      factor: string;
      count: { totalTransistors: number; invertedInputs: string[] };
    };
    network: { pdn: NetworkNode; pun: NetworkNode };
  } | null>(null);

  async function onRun() {
    setLoading(true);
    setError(null);
    try {
      const out = await synthesize(expr);
      setResult({
        steps: {
          simplify: out.raw.steps.simplify.expr,
          factor: out.raw.steps.factor.expr,
          count: {
            totalTransistors: out.raw.steps.count.totalTransistors,
            invertedInputs: out.raw.steps.count.invertedInputs,
          },
        },
        network: out.network,
      });
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>CMOSynthesis</h1>

      <div className="row">
        <input
          className="input"
          value={expr}
          onChange={(e) => setExpr(e.target.value)}
          placeholder="Enter boolean expression, e.g. A & (B | C)"
        />
        <button className="button" onClick={onRun} disabled={loading}>
          {loading ? 'Running…' : 'Synthesize'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <>
          <div className="panel">
            <div className="panel-title">Summary</div>
            <div className="summary">
              <div>
                <span className="label">Simplified:</span> {result.steps.simplify}
              </div>
              <div>
                <span className="label">Factored:</span> {result.steps.factor}
              </div>
              <div>
                <span className="label">Total transistors:</span> {result.steps.count.totalTransistors}
              </div>
              <div>
                <span className="label">Inverted inputs:</span>{' '}
                {result.steps.count.invertedInputs.length ? result.steps.count.invertedInputs.join(', ') : '(none)'}
              </div>
            </div>
          </div>

          <div className="grid">
            <NetworkSvg title="PUN (PMOS)" node={result.network.pun} />
            <NetworkSvg title="PDN (NMOS)" node={result.network.pdn} />
          </div>
        </>
      )}
    </div>
  );
}
