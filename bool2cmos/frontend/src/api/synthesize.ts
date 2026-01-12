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
  input: {
    expression: string;
    style?: { not: string; and: string; or: string };
  };
  steps: {
    parse: { expr: string };
    simplify: { expr: string };
    complement: { expr: string };
    nnf: { expr: string };
    nnfComplement?: { expr: string };
    factor: { expr: string };
    factorComplement?: { expr: string };
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

function mapApiNetwork(node: ApiNetwork, notOp: string): NetworkNode {
  if (node.type === 'transistor') {
    const name = node.gateInverted ? `${notOp}${node.gate}` : node.gate;
    return { type: 'transistor', name, deviceType: node.kind };
  }
  return { type: node.kind, children: node.children.map((c) => mapApiNetwork(c, notOp)) };
}

export function toCMOSNetwork(resp: SynthesisResponse): CMOSNetwork {
  const notOp = resp.input.style?.not ?? '~';
  return {
    pun: mapApiNetwork(resp.steps.pun.network, notOp),
    pdn: mapApiNetwork(resp.steps.pdn.network, notOp),
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
