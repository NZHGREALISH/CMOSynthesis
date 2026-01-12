import { CMOSNetwork, NetworkNode } from '../types/network';

export type ApiNetwork =
  | {
      type: 'transistor';
      kind: 'nmos' | 'pmos';
      gate: string;
      gateInverted?: boolean;
      onWhen?: number;
    }
  | {
      type: 'node';
      kind: 'series' | 'parallel';
      children: ApiNetwork[];
    };

export interface SynthesisResponse {
  input: { expression: string };
  steps: {
    parse: { expr: string };
    simplify: { expr: string };
    complement: { expr: string };
    nnf: { expr: string };
    factor: { expr: string };
    pdn: { network: ApiNetwork };
    pun: { network: ApiNetwork };
    count: {
      pdnTransistors: number;
      punTransistors: number;
      inverterTransistors: number;
      totalTransistors: number;
      invertedInputs: string[];
    };
  };
}

function mapApiNetwork(node: ApiNetwork): NetworkNode {
  if (node.type === 'transistor') {
    const name = node.gateInverted ? `~${node.gate}` : node.gate;
    return { type: 'transistor', name, deviceType: node.kind };
  }
  return { type: node.kind, children: node.children.map(mapApiNetwork) };
}

export function toCMOSNetwork(resp: SynthesisResponse): CMOSNetwork {
  return {
    pun: mapApiNetwork(resp.steps.pun.network),
    pdn: mapApiNetwork(resp.steps.pdn.network),
  };
}

export async function synthesize(expr: string): Promise<SynthesisResponse> {
  const res = await fetch('/synthesize', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ expr }),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data?.detail) detail = data.detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  return (await res.json()) as SynthesisResponse;
}
