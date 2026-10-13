'use client';

import React from 'react';
import ShapeBlur from '@/components/ui/ShapeBlur';

export default function ShapeBlurDemo() {
  return (
    <div style={{ position: 'relative', height: '500px', overflow: 'hidden' }}>
      <ShapeBlur
        variation={0}
        pixelRatioProp={typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1}
        shapeSize={0.5}
        roundness={0.5}
        borderSize={0.05}
        circleSize={0.5}
        circleEdge={1}
      />
    </div>
  );
}
