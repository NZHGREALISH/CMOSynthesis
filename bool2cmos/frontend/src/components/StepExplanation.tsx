import React from 'react';

export function StepExplanation({
  steps,
}: {
  steps: {
    parse: { expr: string };
    simplify: { expr: string };
    complement: { expr: string };
    nnf: { expr: string };
    factor: { expr: string };
  };
}) {
  const rows: Array<[string, string]> = [
    ['Parse', steps.parse.expr],
    ['Simplify', steps.simplify.expr],
    ['Complement', steps.complement.expr],
    ['NNF', steps.nnf.expr],
    ['Factor', steps.factor.expr],
  ];

  return (
    <div className="card">
      <h2>Pipeline</h2>
      <table className="table">
        <tbody>
          {rows.map(([k, v]) => (
            <tr key={k}>
              <th>{k}</th>
              <td>
                <code>{v}</code>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
