import React from 'react';
import { LayoutNode } from '../layout/TreeLayout';
import { Wire } from './Wire';

interface SeriesBlockProps {
  layout: LayoutNode;
  renderNode: (layout: LayoutNode) => React.ReactNode;
}

export const SeriesBlock: React.FC<SeriesBlockProps> = ({ layout, renderNode }) => {
  const { width, children } = layout;
  const cx = width / 2;

  return (
    <g className="series-block">
      {/* Render Children */}
      {children.map((child, index) => (
        <g key={index} transform={`translate(${child.x}, ${child.y})`}>
          {renderNode(child)}
        </g>
      ))}

      {/* Render Inter-child Wires */}
      {children.map((child, index) => {
        if (index === children.length - 1) return null; // Last child has no wire below it
        const nextChild = children[index + 1];
        
        // Wire from bottom of current child to top of next child
        return (
          <Wire
            key={`wire-${index}`}
            x1={cx}
            y1={child.y + child.height}
            x2={cx}
            y2={nextChild.y}
          />
        );
      })}
    </g>
  );
};
