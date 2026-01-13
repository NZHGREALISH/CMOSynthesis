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
  const terminalLen = (height - channelLength) / 2;
  const plateWidth = 3;
  
  // Layout offsets
  // "Protruding" style: Trunk -> (stubs) -> Channel -> Gate
  // Moving channel to the Left of trunk to keep gate on the far Left (input side)
  const channelOffset = 16; 
  const gateGap = 8;
  
  const trunkX = cx;
  const channelX = cx - channelOffset;
  const gateX = channelX - gateGap;
  
  // Vertical bounds for the device active area
  const topY = terminalLen;
  const botY = height - terminalLen;

  return (
    <g className={`transistor ${deviceType}`}>
      {/* --- Main Trunk (Source/Drain Terminals) --- */}
      {/* Top Segment */}
      <line x1={trunkX} y1={0} x2={trunkX} y2={topY} strokeWidth={2} />
      {/* Bottom Segment */}
      <line x1={trunkX} y1={height} x2={trunkX} y2={botY} strokeWidth={2} />
      
      {/* --- Stubs (Connecting Trunk to Channel) --- */}
      <line x1={trunkX} y1={topY} x2={channelX} y2={topY} strokeWidth={2} />
      <line x1={trunkX} y1={botY} x2={channelX} y2={botY} strokeWidth={2} />

      {/* --- Channel (Vertical) --- */}
      <line 
        x1={channelX} 
        y1={topY} 
        x2={channelX} 
        y2={botY} 
        strokeWidth={2} 
      />

      {/* --- Gate Plate (Vertical) --- */}
      <line 
        x1={gateX} 
        y1={topY} 
        x2={gateX} 
        y2={botY} 
        strokeWidth={plateWidth} 
      />

      {/* --- Gate Connection --- */}
      <line 
        x1={gateX} 
        y1={cy} 
        x2={0} 
        y2={cy} 
        strokeWidth={2} 
      />

      {/* --- PMOS Bubble --- */}
      {deviceType === 'pmos' && (
        <circle 
          cx={gateX - 5} 
          cy={cy} 
          r={4} 
          fill="white" 
          strokeWidth={2} 
        />
      )}

      {/* Label */}
      <text 
        x={channelX - 2} // Align slightly left of channel? Or centered on channel?
        y={cy - 10} 
        className="text-xs font-bold" 
        style={{ fontSize: '14px', textAnchor: 'middle' }}
      >
        {name}
      </text>
    </g>
  );
};
