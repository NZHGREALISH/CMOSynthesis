import React from 'react';

export function StepExplanation({
  steps,
}: {
  steps: {
    parse: { expr: string };
    simplify: { expr: string };
    complement: { expr: string };
    nnf: { expr: string };
    nnfComplement?: { expr: string };
    factor: { expr: string };
    factorComplement?: { expr: string };
  };
}) {
  const rows: Array<[string, string]> = [
    ['Parse', steps.parse.expr],
    ['Simplify', steps.simplify.expr],
    ['Complement', steps.complement.expr],
    ['NNF', steps.nnf.expr],
    ...(steps.nnfComplement ? ([['NNF (Complement)', steps.nnfComplement.expr]] as Array<[string, string]>) : []),
    ['Factor', steps.factor.expr],
    ...(steps.factorComplement ? ([['Factor (Complement)', steps.factorComplement.expr]] as Array<[string, string]>) : []),
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
