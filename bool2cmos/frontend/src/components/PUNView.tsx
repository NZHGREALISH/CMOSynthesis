import React from 'react';

import { NetworkNode } from '../types/network';
import { NetworkView } from './NetworkView';

export function PUNView({ network }: { network: NetworkNode }) {
  return <NetworkView title="PUN" network={network} />;
}
