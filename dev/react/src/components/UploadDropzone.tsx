"use client";

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { motion, useAnimationControls } from "framer-motion";
import { Check, Upload as UpIcon } from "lucide-react";
import "./UploadDropzone.css";

/* ══ Upload dropzone ══════════════════════════════════════
   A drop box that inhales, accepts drag and drop of real
   files or click-to-browse, calculates real progress, rolls
   the percentage, ticks on completion, and handles size
   validation with physics-based spring animations.

   ── THE BOX INHALES, AND SWALLOWS ───────────────────────
   A plain filled box with reactive hover and drop interaction.
   A file carried over it is answered before it is let go:
   the box scales with a small bounce and the arrow lifts.
   When dropped, the file is validated, animated with a rolling
   percentage counter, and confirms with a spring checkmark.

   ── ONE OF THEM IS TOO BIG ──────────────────────────────
   The limit is fixed at 5 MB: dropping a file over 5 MB
   shakes the box with elastic feedback and displays the
   refusal alert in red. */

/* Read once, the way the wheel and the pill nav do. A
   preference, not a live input. */
const stillness = () =>
  typeof window !== "undefined" &&
  !!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

const MAX = 5;

/* what it says the second time, and after */
const SNARK = [
  "Supera el límite de 5 MB.",
  "El archivo no se pudo comprimir.",
  "Prueba optimizando o comprimiendo el archivo.",
  "El archivo excede el tamaño máximo permitido.",
  "Tamaño no válido.",
];

export type F = {
  id: string;
  name: string;
  ext: string;
  size: number;
  tint: string;
  raw?: File;
};

const fmt = (b: number) => (b >= 1e6 ? `${(b / 1e6).toFixed(1)} MB` : `${Math.round(b / 1e3)} KB`);
const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));

function getFileTint(ext: string): string {
  const e = ext.toUpperCase();
  if (["PNG", "JPG", "JPEG", "WEBP", "GIF", "SVG"].includes(e)) return "#079455";
  if (["MP4", "MOV", "WEBM", "AVI"].includes(e)) return "#155EEF";
  if (["MP3", "WAV", "OGG", "M4A"].includes(e)) return "#eab308";
  if (["PDF", "DOC", "DOCX", "TXT"].includes(e)) return "#d92d20";
  return "#64748b";
}

/* ── the file icon ─────────────────────────────────────────
   After Untitled UI's: a rounded page on a 40 grid with a thin
   grey outline and a folded corner, and the extension on a
   coloured label that sticks out past the page's left edge —
   the colour carries the kind before the word is read. */
function Page({ f, size = 40 }: { f: F; size?: number }) {
  return (
    <svg className="upl-page" width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <path
        className="upl-page-line"
        d="M7.75 4A3.25 3.25 0 0 1 11 .75h16c.121 0 .238.048.323.134l10.793 10.793a.46.46 0 0 1 .134.323v24A3.25 3.25 0 0 1 35 39.25H11A3.25 3.25 0 0 1 7.75 36z"
      />
      <path className="upl-page-line" d="M27 .5V8a4 4 0 0 0 4 4h7.5" />
      <rect width="29" height="16" x="1" y="18" rx="8" fill={f.tint} />
      <text x="15.5" y="29.3" textAnchor="middle" className="upl-page-ext">{f.ext}</text>
    </svg>
  );
}

function Roll({ value }: { value: number }) {
  const s = String(Math.round(value));
  return (
    <span className="upl-roll" aria-label={`${s}%`}>
      {s.split("").map((d, i) => (
        <span key={s.length - i} className="upl-roll-col">
          <span className="upl-roll-strip" style={{ transform: `translateY(${-Number(d)}em)` }}>
            {"0123456789".split("").map((n) => <span key={n}>{n}</span>)}
          </span>
        </span>
      ))}
      %
    </span>
  );
}

type Phase = { kind: "idle" } | { kind: "up"; f: F; p: number } | { kind: "done"; f: F };

export interface UploadDropzoneProps {
  /* how fast a file sends, 0..100 */
  speed?: number;
  /* how springy a file flies home, 0..100 */
  bounce?: number;
  corner?: number;
  onUploadComplete?: (file: F, rawFile?: File) => void;
  accept?: string;
}

export function Upload({
  speed = 65,
  bounce = 45,
  corner = 16,
  onUploadComplete,
  accept,
}: UploadDropzoneProps = {}) {
  const still = stillness();
  const [phase, setPhase] = useState<Phase>({ kind: "idle" });
  const [over, setOver] = useState(false);
  const [refuse, setRefuse] = useState<string | null>(null);
  const tries = useRef(0);
  const cool = useRef(0);
  const [gulp, setGulp] = useState(false);
  const zone = useRef<HTMLDivElement>(null);
  const now = useRef<HTMLSpanElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const shake = useAnimationControls();
  const raf = useRef(0);
  const timers = useRef<number[]>([]);
  const knobs = useRef({ speed });
  knobs.current = { speed };

  useEffect(() => () => {
    cancelAnimationFrame(raf.current);
    raf.current = 0;
    timers.current.forEach(clearTimeout);
    clearTimeout(cool.current);
  }, []);

  const later = (fn: () => void, ms: number) => {
    timers.current.push(window.setTimeout(fn, ms));
  };

  /* ── the upload simulation wire ────────────────────────── */
  const send = (f: F) => {
    if (still) { finish(f); return; }
    setPhase({ kind: "up", f, p: 0 });
    let p = 0;
    let prev = 0;
    const secs = (3.2 - (clamp(knobs.current.speed, 0, 100) / 100) * 2.4) * (0.6 + Math.min(1, f.size / 5e6) * 0.4);
    const tick = (t: number) => {
      const dt = prev ? Math.min(0.05, (t - prev) / 1000) : 0;
      prev = t;
      p = Math.min(1, p + (dt / secs) * (0.6 + Math.random() * 0.9));
      if (p >= 1) { raf.current = 0; finish(f); return; }
      setPhase({ kind: "up", f, p });
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
  };

  const finish = (f: F) => {
    tries.current = 0;
    setPhase({ kind: "done", f });
    if (onUploadComplete) onUploadComplete(f, f.raw);
    /* keep the completed status in the box */
  };

  const refuseIt = () => {
    const n = tries.current++;
    setRefuse(n === 0 ? `Muy grande — máximo ${MAX} MB` : SNARK[Math.min(n - 1, SNARK.length - 1)]);
    shake.start({ x: [0, -7, 6, -4, 2, 0], transition: { duration: 0.38 } });
    later(() => setRefuse(null), 2200);
    clearTimeout(cool.current);
    cool.current = window.setTimeout(() => { tries.current = 0; }, 8000);
  };

  const processRealFile = (file?: File) => {
    if (!file) return;
    const parts = file.name.split(".");
    const ext = parts.length > 1 ? parts.pop()!.toUpperCase() : "FILE";
    const tint = getFileTint(ext);

    const f: F = {
      id: `file_${Date.now()}`,
      name: file.name,
      ext,
      size: file.size,
      tint,
      raw: file,
    };

    if (file.size > MAX * 1024 * 1024) {
      refuseIt();
      return;
    }

    setGulp(true);
    later(() => setGulp(false), 460);
    send(f);
  };

  /* ── the box hugs the upload ─────────────────────────────
     While a file is in it the box closes in round the upload row
     and grows a little when the tick arrives; back to idle it opens
     out to the full drop box again. */
  useLayoutEffect(() => {
    const z = zone.current;
    const n = now.current;
    if (!z) return;
    if (phase.kind === "idle" || !n) {
      z.style.width = "";
      z.style.height = "";
      return;
    }
    z.style.width = `${n.offsetWidth + 32}px`;
    z.style.height = `${n.offsetHeight + 28}px`;
  }, [phase.kind]);

  const r = Math.max(0, corner);
  const up = phase.kind !== "idle";
  const f = phase.kind !== "idle" ? phase.f : null;

  return (
    <div
      className="upl"
      style={{
        "--upl-r": `${r}px`,
        "--upl-spring": `cubic-bezier(0.3, ${1 + (bounce / 100) * 0.9}, 0.4, 1)`,
      } as React.CSSProperties}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        tabIndex={-1}
        className="hidden"
        style={{ display: "none" }}
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            processRealFile(e.target.files[0]);
          }
        }}
      />

      <motion.div animate={shake} className="upl-zone-wrap">
        <div
          ref={zone}
          className="upl-zone"
          data-over={over || undefined}
          data-refuse={refuse ? true : undefined}
          data-busy={up || undefined}
          data-gulp={gulp || undefined}
          role="button"
          tabIndex={0}
          aria-live="polite"
          title="Arrastra un archivo o haz clic para seleccionar"
          onClick={() => {
            if (phase.kind === "idle" || phase.kind === "done") {
              inputRef.current?.click();
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              inputRef.current?.click();
            }
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!over) setOver(true);
          }}
          onDragEnter={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setOver(true);
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setOver(false);
          }}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setOver(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              processRealFile(e.dataTransfer.files[0]);
            }
          }}
        >
          {!f ? (
            <>
              <span className="upl-icon"><UpIcon size={20} strokeWidth={2} /></span>
              <span className="upl-say">
                <b>{refuse ?? (over ? "Suelta tu archivo aquí" : "Arrastra un archivo aquí o haz clic")}</b>
                <span>Hasta {MAX} MB (Fotos, Audios o PDF)</span>
              </span>
            </>
          ) : (
            <span className="upl-now" key={f.id} ref={now}>
              <Page f={f} size={36} />
              <span className="upl-text">
                <span className="upl-name">{f.name}</span>
                <span className="upl-meta">
                  {fmt(f.size)} · {phase.kind === "done" ? "Completado" : <Roll value={phase.kind === "up" ? phase.p * 100 : 0} />}
                </span>
                <span className="upl-track">
                  <span className="upl-bar" style={{ transform: `scaleX(${phase.kind === "up" ? phase.p : 1})` }} />
                </span>
              </span>
              <span className="upl-end">
                {phase.kind === "done" && <span className="upl-tick"><Check size={12} strokeWidth={3} /></span>}
              </span>
            </span>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export const UploadDropzone = Upload;
export default UploadDropzone;
