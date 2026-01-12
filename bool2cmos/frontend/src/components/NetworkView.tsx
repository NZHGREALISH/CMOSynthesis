import React, { useMemo } from 'react';

import { calculateLayout } from '../layout/TreeLayout';
import { LayoutNode } from '../layout/TreeLayout';
import { NetworkNode } from '../types/network';
import { ParallelBlock } from '../render/ParallelBlock';
import { SeriesBlock } from '../render/SeriesBlock';
import { Transistor } from '../render/Transistor';

export function NetworkView({ title, network }: { title: string; network: NetworkNode }) {
  const layout = useMemo(() => calculateLayout(network), [network]);

  function renderNode(nodeLayout: LayoutNode): React.ReactNode {
    if (nodeLayout.node.type === 'transistor') return <Transistor layout={nodeLayout} />;
    if (nodeLayout.node.type === 'series') return <SeriesBlock layout={nodeLayout} renderNode={renderNode} />;
    return <ParallelBlock layout={nodeLayout} renderNode={renderNode} />;
  }

  const padding = 16;
  const width = Math.max(1, layout.width + padding * 2);
  const height = Math.max(1, layout.height + padding * 2);

  return (
    <div className="card">
      <h2>{title}</h2>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
        <g transform={`translate(${padding}, ${padding})`}>{renderNode(layout)}</g>
      </svg>
    </div>
  );
}
