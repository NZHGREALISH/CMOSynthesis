export type NodeType = 'transistor' | 'series' | 'parallel';

export interface TransistorNode {
  type: 'transistor';
  name: string; // Input signal name, e.g., "A", "B"
  deviceType: 'nmos' | 'pmos';
}

export interface SeriesNode {
  type: 'series';
  children: NetworkNode[];
}

export interface ParallelNode {
  type: 'parallel';
  children: NetworkNode[];
}

export type NetworkNode = TransistorNode | SeriesNode | ParallelNode;

export interface CMOSNetwork {
  pun: NetworkNode;
  pdn: NetworkNode;
}
