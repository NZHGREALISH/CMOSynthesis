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
    
    // PUN Path (from Simplify)
    ['NNF (PUN)', steps.nnf.expr],
    ['Factor (PUN)', steps.factor.expr],

    // PDN Path (from Complement)
    ['Complement', steps.complement.expr],
    ...(steps.nnfComplement ? ([['NNF (PDN)', steps.nnfComplement.expr]] as Array<[string, string]>) : []),
    ...(steps.factorComplement ? ([['Factor (PDN)', steps.factorComplement.expr]] as Array<[string, string]>) : []),
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
