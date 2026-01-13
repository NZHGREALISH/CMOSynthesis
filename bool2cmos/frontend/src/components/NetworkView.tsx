import React, { useMemo } from 'react';

import { calculateLayout } from '../layout/TreeLayout';
import { LayoutNode } from '../layout/TreeLayout';
import { NetworkNode } from '../types/network';
import { ParallelBlock } from '../render/ParallelBlock';
import { SeriesBlock } from '../render/SeriesBlock';
import { Transistor } from '../render/Transistor';

export function NetworkView({
  title,
  network,
  topLabel,
  bottomLabel,
}: {
  title: string;
  network: NetworkNode;
  topLabel?: string;
  bottomLabel?: string;
}) {
  const layout = useMemo(() => calculateLayout(network), [network]);

  function renderNode(nodeLayout: LayoutNode): React.ReactNode {
    if (nodeLayout.node.type === 'transistor') return <Transistor layout={nodeLayout} />;
    if (nodeLayout.node.type === 'series') return <SeriesBlock layout={nodeLayout} renderNode={renderNode} />;
    return <ParallelBlock layout={nodeLayout} renderNode={renderNode} />;
  }

  const padding = 16;
  const labelSpace = 30;

  const topOffset = topLabel ? labelSpace : 0;
  const bottomOffset = bottomLabel ? labelSpace : 0;

  const width = Math.max(1, layout.width + padding * 2);
  const height = Math.max(1, layout.height + padding * 2 + topOffset + bottomOffset);

  const contentX = padding;
  const contentY = padding + topOffset;
  const centerX = width / 2;
  const connectionYTop = contentY;
  const connectionYBottom = contentY + layout.height;

  return (
    <div className="card">
      <h2>{title}</h2>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={title}>
        <g transform={`translate(${contentX}, ${contentY})`}>{renderNode(layout)}</g>

        {topLabel && (
          <g>
            <text
              x={centerX}
              y={padding + 12}
              textAnchor="middle"
              fontSize="12"
              fontWeight="bold"
              fill="#374151"
            >
              {topLabel}
            </text>
            <line
              x1={centerX}
              y1={padding + 16}
              x2={centerX}
              y2={connectionYTop}
              stroke="#374151"
              strokeWidth="2"
            />
          </g>
        )}

        {bottomLabel && (
          <g>
            <line
              x1={centerX}
              y1={connectionYBottom}
              x2={centerX}
              y2={height - padding - 16}
              stroke="#374151"
              strokeWidth="2"
            />
            <text
              x={centerX}
              y={height - padding - 4}
              textAnchor="middle"
              fontSize="12"
              fontWeight="bold"
              fill="#374151"
            >
              {bottomLabel}
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}
