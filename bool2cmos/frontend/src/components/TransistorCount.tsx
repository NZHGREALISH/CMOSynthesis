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
      <h2>Transistor Count</h2>
      <table className="table">
        <tbody>
          <tr>
            <th>PDN</th>
            <td>{count.pdnTransistors}</td>
          </tr>
          <tr>
            <th>PUN</th>
            <td>{count.punTransistors}</td>
          </tr>
          <tr>
            <th>Inverters</th>
            <td>{count.inverterTransistors}</td>
          </tr>
          <tr>
            <th>Total</th>
            <td>{count.totalTransistors}</td>
          </tr>
          <tr>
            <th>Inverted Inputs</th>
            <td>{count.invertedInputs.length ? count.invertedInputs.join(', ') : '—'}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
