import React from 'react';
import { TransistorNode } from '../types/network';
import { LayoutNode } from '../layout/TreeLayout';

interface TransistorProps {
  layout: LayoutNode;
}

export const Transistor: React.FC<TransistorProps> = ({ layout }) => {
  const { node, width, height } = layout;
  const { name, deviceType } = node as TransistorNode;
  
  const cx = width / 2;
  const cy = height / 2;
  
  // Dimensions
  const channelLength = 24;
  const gateOffset = 12;
  const terminalLen = (height - channelLength) / 2;
  const plateWidth = 3;

  return (
    <g className={`transistor ${deviceType}`}>
      {/* Top Terminal (Drain/Source) */}
      <line x1={cx} y1={0} x2={cx} y2={terminalLen} strokeWidth={2} />
      
      {/* Bottom Terminal (Source/Drain) */}
      <line x1={cx} y1={height} x2={cx} y2={height - terminalLen} strokeWidth={2} />
      
      {/* Gate Plate (Vertical) */}
      <line 
        x1={cx - gateOffset} 
        y1={terminalLen} 
        x2={cx - gateOffset} 
        y2={height - terminalLen} 
        strokeWidth={plateWidth} 
      />

      {/* Channel Line (Vertical) */}
      <line 
        x1={cx} 
        y1={terminalLen} 
        x2={cx} 
        y2={height - terminalLen} 
        strokeWidth={2} 
      />

      {/* Gate Connection */}
      <line 
        x1={cx - gateOffset} 
        y1={cy} 
        x2={0} 
        y2={cy} 
        strokeWidth={2} 
      />

      {/* PMOS Bubble */}
      {deviceType === 'pmos' && (
        <circle 
          cx={cx - gateOffset - 5} 
          cy={cy} 
          r={4} 
          fill="white" 
          strokeWidth={2} 
        />
      )}

      {/* Label */}
      <text 
        x={(cx - gateOffset) / 2} 
        y={cy - 10} 
        className="text-xs font-bold" 
        style={{ fontSize: '14px', textAnchor: 'middle' }}
      >
        {name}
      </text>
    </g>
  );
};