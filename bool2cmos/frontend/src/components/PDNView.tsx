import React from 'react';

import { NetworkNode } from '../types/network';
import { NetworkView } from './NetworkView';

export function PDNView({ network }: { network: NetworkNode }) {
  return <NetworkView title="PDN" network={network} />;
}
