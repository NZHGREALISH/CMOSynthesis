import React from 'react';

interface WireProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color?: string;
  width?: number;
}

export const Wire: React.FC<WireProps> = ({ 
  x1, 
  y1, 
  x2, 
  y2, 
  color = 'black', 
  width = 2 
}) => {
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={color}
      strokeWidth={width}
      strokeLinecap="round"
    />
  );
};
