import React from 'react';

export function TransistorCount({
  count,
}: {
  count: {
    pdnTransistors: number;
    punTransistors: number;
    inverterTransistors: number;
    totalTransistors: number;
    invertedInputs: string[];
  };
}) {
  return (
    <div className="card">
      <h2>Counts</h2>
      <div className="counts">
        <div>
          <div className="k">PDN</div>
          <div className="v">{count.pdnTransistors}</div>
        </div>
        <div>
          <div className="k">PUN</div>
          <div className="v">{count.punTransistors}</div>
        </div>
        <div>
          <div className="k">Inverters</div>
          <div className="v">{count.inverterTransistors}</div>
        </div>
        <div>
          <div className="k">Total</div>
          <div className="v">{count.totalTransistors}</div>
        </div>
      </div>
      {count.invertedInputs.length > 0 && (
        <p className="subtle">
          Inverted inputs: <code>{count.invertedInputs.join(', ')}</code>
        </p>
      )}
    </div>
  );
}
