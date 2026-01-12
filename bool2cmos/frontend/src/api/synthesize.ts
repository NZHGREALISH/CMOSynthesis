import { CMOSNetwork, NetworkNode } from '../types/network';

type BackendNetwork =
  | {
      type: 'transistor';
      kind: 'nmos' | 'pmos';
      gate: string;
      gateInverted: boolean;
      onWhen: 0 | 1;
    }
  | {
      type: 'node';
      kind: 'series' | 'parallel';
      children: BackendNetwork[];
    };

export interface SynthesisResult {
  input: { expression: string };
  steps: {
    parse: { expr: string };
    simplify: { expr: string };
    complement: { expr: string };
    nnf: { expr: string };
    factor: { expr: string };
    pdn: { network: BackendNetwork };
    pun: { network: BackendNetwork };
    count: {
      pdnTransistors: number;
      punTransistors: number;
      inverterTransistors: number;
      totalTransistors: number;
      invertedInputs: string[];
    };
    export: { format: 'json' };
  };
}

function mapNetwork(node: BackendNetwork): NetworkNode {
  if (node.type === 'transistor') {
    return {
      type: 'transistor',
      name: node.gateInverted ? `!${node.gate}` : node.gate,
      deviceType: node.kind,
    };
  }

  return {
    type: node.kind,
    children: node.children.map(mapNetwork),
  };
}

export async function synthesize(expr: string): Promise<{ raw: SynthesisResult; network: CMOSNetwork }> {
  const resp = await fetch('/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expr }),
  });

  const payload = (await resp.json()) as unknown;

  if (!resp.ok) {
    const message =
      typeof payload === 'object' && payload !== null && 'detail' in payload
        ? String((payload as { detail?: unknown }).detail)
        : `Request failed (${resp.status})`;
    throw new Error(message);
  }

  const raw = payload as SynthesisResult;
  return {
    raw,
    network: {
      pdn: mapNetwork(raw.steps.pdn.network),
      pun: mapNetwork(raw.steps.pun.network),
    },
  };
}
