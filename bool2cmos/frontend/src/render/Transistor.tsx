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
  const channelLength = 20;
  const gateOffset = 8;
  const terminalLen = (height - channelLength) / 2;

  return (
    <g className={`transistor ${deviceType}`}>
      {/* Top Terminal (Drain/Source) */}
      <line x1={cx} y1={0} x2={cx} y2={terminalLen} stroke="black" strokeWidth={2} />
      
      {/* Bottom Terminal (Source/Drain) */}
      <line x1={cx} y1={height} x2={cx} y2={height - terminalLen} stroke="black" strokeWidth={2} />
      
      {/* Channel (simplified) */}
      {/* For simplicity, we draw the channel line and the gate plate */}
      
      {/* Gate Plate (Vertical) */}
      <line 
        x1={cx - gateOffset} 
        y1={terminalLen} 
        x2={cx - gateOffset} 
        y2={height - terminalLen} 
        stroke="black" 
        strokeWidth={2} 
      />

      {/* Channel Line (Vertical) - Dotted or solid based on preference, using solid for now */}
      <line 
        x1={cx} 
        y1={terminalLen} 
        x2={cx} 
        y2={height - terminalLen} 
        stroke="black" 
        strokeWidth={2} 
      />

      {/* Gate Connection */}
      <line 
        x1={cx - gateOffset} 
        y1={cy} 
        x2={0} 
        y2={cy} 
        stroke="black" 
        strokeWidth={2} 
      />

      {/* PMOS Bubble */}
      {deviceType === 'pmos' && (
        <circle 
          cx={cx - gateOffset - 5} 
          cy={cy} 
          r={3} 
          fill="white" 
          stroke="black" 
          strokeWidth={2} 
        />
      )}

      {/* Label */}
      <text 
        x={0} 
        y={cy - 10} 
        className="text-xs font-bold" 
        fill="black"
        style={{ fontSize: '12px' }}
      >
        {name}
      </text>
    </g>
  );
};
