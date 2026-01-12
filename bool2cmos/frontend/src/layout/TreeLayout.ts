import { NetworkNode } from '../types/network';

export interface LayoutNode {
  node: NetworkNode;
  x: number;
  y: number;
  width: number;
  height: number;
  children: LayoutNode[];
}

export const CONFIG = {
  TRANSISTOR_SIZE: 60,
  H_SPACING: 40,
  V_SPACING: 40,
};

export function calculateLayout(node: NetworkNode): LayoutNode {
  if (node.type === 'transistor') {
    return {
      node,
      x: 0,
      y: 0,
      width: CONFIG.TRANSISTOR_SIZE,
      height: CONFIG.TRANSISTOR_SIZE,
      children: [],
    };
  }

  if (node.type === 'series') {
    const childrenLayouts = node.children.map(calculateLayout);
    
    // Width is the max width of children
    const width = Math.max(...childrenLayouts.map((c) => c.width), 0);
    
    // Height is sum of heights + spacing
    const totalChildHeight = childrenLayouts.reduce((sum, c) => sum + c.height, 0);
    const height = totalChildHeight + (childrenLayouts.length - 1) * CONFIG.V_SPACING;

    // Position children
    let currentY = 0;
    const positionedChildren = childrenLayouts.map((child) => {
      const x = (width - child.width) / 2; // Center horizontally
      const y = currentY;
      currentY += child.height + CONFIG.V_SPACING;
      return { ...child, x, y };
    });

    return {
      node,
      x: 0,
      y: 0,
      width,
      height,
      children: positionedChildren,
    };
  }

  if (node.type === 'parallel') {
    const childrenLayouts = node.children.map(calculateLayout);

    // Width is sum of widths + spacing
    const totalChildWidth = childrenLayouts.reduce((sum, c) => sum + c.width, 0);
    const width = totalChildWidth + (childrenLayouts.length - 1) * CONFIG.H_SPACING;

    // Height is max height of children
    const height = Math.max(...childrenLayouts.map((c) => c.height), 0);

    // Position children
    let currentX = 0;
    const positionedChildren = childrenLayouts.map((child) => {
      const x = currentX;
      const y = (height - child.height) / 2; // Center vertically
      currentX += child.width + CONFIG.H_SPACING;
      return { ...child, x, y };
    });

    return {
      node,
      x: 0,
      y: 0,
      width,
      height,
      children: positionedChildren,
    };
  }

  throw new Error('Unknown node type');
}
