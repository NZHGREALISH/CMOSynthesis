import React from 'react';

import { NetworkNode } from '../types/network';
import { calculateLayout } from '../layout/TreeLayout';
import { LayoutNode } from '../layout/TreeLayout';
import { Transistor } from '../render/Transistor';
import { SeriesBlock } from '../render/SeriesBlock';
import { ParallelBlock } from '../render/ParallelBlock';

function renderNode(layout: LayoutNode): React.ReactNode {
  if (layout.node.type === 'transistor') return <Transistor layout={layout} />;
  if (layout.node.type === 'series') return <SeriesBlock layout={layout} renderNode={renderNode} />;
  if (layout.node.type === 'parallel') return <ParallelBlock layout={layout} renderNode={renderNode} />;
  return null;
}

export function PDNView({ network }: { network: NetworkNode }) {
  const layout = calculateLayout(network);
  const padding = 24;
  return (
    <div className="card">
      <h2>PDN (Pull-Down)</h2>
      <svg
        className="network"
        width={layout.width + padding * 2}
        height={layout.height + padding * 2}
        viewBox={`0 0 ${layout.width + padding * 2} ${layout.height + padding * 2}`}
      >
        <g transform={`translate(${padding}, ${padding})`}>{renderNode(layout)}</g>
      </svg>
    </div>
  );
}
