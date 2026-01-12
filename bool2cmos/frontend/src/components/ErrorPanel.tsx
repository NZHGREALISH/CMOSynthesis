import React from 'react';

export function ErrorPanel({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="card error">
      <strong>Error:</strong> {message}
    </div>
  );
}
