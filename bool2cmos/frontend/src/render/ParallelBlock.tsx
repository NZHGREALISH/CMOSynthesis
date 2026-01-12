import React from 'react';
import { LayoutNode } from '../layout/TreeLayout';
import { Wire } from './Wire';

interface ParallelBlockProps {
  layout: LayoutNode;
  renderNode: (layout: LayoutNode) => React.ReactNode;
}

export const ParallelBlock: React.FC<ParallelBlockProps> = ({ layout, renderNode }) => {
  const { width, height, children } = layout;

  if (children.length === 0) return null;

  // Calculate center x for each child relative to the ParallelBlock
  const childCenters = children.map(c => c.x + c.width / 2);
  const minX = Math.min(...childCenters);
  const maxX = Math.max(...childCenters);

  return (
    <g className="parallel-block">
      {/* Render Children */}
      {children.map((child, index) => (
        <g key={index} transform={`translate(${child.x}, ${child.y})`}>
          {renderNode(child)}
        </g>
      ))}

      {/* Top Rail */}
      <Wire x1={minX} y1={0} x2={maxX} y2={0} />

      {/* Bottom Rail */}
      <Wire x1={minX} y1={height} x2={maxX} y2={height} />

      {/* Vertical Drops to Children */}
      {children.map((child, index) => {
        const cx = childCenters[index];
        return (
          <React.Fragment key={`drop-${index}`}>
            {/* Top Drop */}
            <Wire x1={cx} y1={0} x2={cx} y2={child.y} />
            
            {/* Bottom Drop */}
            <Wire x1={cx} y1={child.y + child.height} x2={cx} y2={height} />
          </React.Fragment>
        );
      })}
    </g>
  );
};
