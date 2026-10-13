"use client";

/**
 * Firby Sound Engine (Bencho Audio Tokens)
 * - bencho-pop.wav: Sonido al llegar una notificación en workspace.
 * - bencho-perk.wav: Sonido al tocar/interactuar con la campana de notificaciones.
 */

export function playSound(type: "pop" | "perk") {
  if (typeof window === "undefined") return;
  try {
    const filename = type === "pop" ? "bencho-pop.wav" : "bencho-perk.wav";
    const audio = new Audio(`/sounds/${filename}`);
    audio.volume = 0.75;
    const playPromise = audio.play();
    if (playPromise !== undefined) {
      playPromise.catch(() => {
        // Fallback or autoplay policy block
      });
    }
  } catch (_) {}
}

export function playNotificationPop() {
  playSound("pop");
}

export function playNotificationPerk() {
  playSound("perk");
}

if (typeof window !== "undefined") {
  (window as any).playNotificationPop = playNotificationPop;
  (window as any).playNotificationPerk = playNotificationPerk;
}
