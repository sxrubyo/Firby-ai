'use client';

import React from 'react';
import Iridescence from '@/components/ui/Iridescence';

export default function IridescenceDemo() {
  return (
    <div className="relative w-full h-[400px] overflow-hidden rounded-3xl border border-neutral-200 dark:border-neutral-800">
      <Iridescence
        color={[0.054901960784313725, 0.054901960784313725, 0.054901960784313725]}
        mouseReact={false}
        amplitude={0.1}
        speed={0.5}
      />
      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none text-center px-4">
        <h2 className="text-3xl font-bold tracking-tight text-white mb-2">
          Ponga a trabajar a su operador autónomo hoy mismo
        </h2>
        <p className="text-sm text-neutral-300 max-w-md">
          Pruebe 7 días gratis con todas las funciones. Sin contratos de permanencia.
        </p>
      </div>
    </div>
  );
}
