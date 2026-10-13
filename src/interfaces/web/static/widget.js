/**
 * Firby AI — Enterprise Conversational Concierge
 * High-Craft Minimalist Interface (Linear / Vercel style)
 * Native WebGL 3D Liquid Orb Thinking Engine (100% Transparent, Zero-Latency)
 * Multi-Model Rotation: Gemini 3.1, 3.5, 3.8 & 2.5
 * https://firbyai.com
 */
(function () {
  if (window.__FIRBY_WIDGET_LOADED__) return;
  window.__FIRBY_WIDGET_LOADED__ = true;

  // Auto-bootstrapper del motor de movimiento inercial Lenis y Firby Agent Surface
  (function ensureMotionAndSurface() {
    function loadScript(src, cb) {
      const s = document.createElement('script');
      s.src = src;
      s.async = true;
      if (cb) s.onload = cb;
      document.head.appendChild(s);
    }

    const isAppWorkspace = typeof window !== 'undefined' && (
      window.location.pathname.startsWith('/workspace') ||
      window.location.pathname.startsWith('/panel') ||
      window.location.pathname.startsWith('/settings') ||
      window.location.pathname.startsWith('/chats') ||
      window.location.pathname.startsWith('/dev-portal')
    );

    if (typeof window.FirbyAgentSurface === 'undefined') {
      loadScript('/firby-agent-surface.js');
    }

    if (!isAppWorkspace && typeof window.FirbyMotionEngine === 'undefined') {
      if (typeof window.Lenis === 'undefined') {
        loadScript('/lenis.min.js', function () {
          loadScript('/firby-motion-engine.js');
        });
      } else {
        loadScript('/firby-motion-engine.js');
      }
    }
  })();

  const currentScript = document.currentScript || (function () {
    const scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  const API_HOST = currentScript.getAttribute('data-host') || '';
  const ORG_ID = currentScript.getAttribute('data-firby-id') || 'firby_landing';
  const ACCENT_COLOR = currentScript.getAttribute('data-accent-color') || '#b9fa01';
  const BORDER_COLOR = currentScript.getAttribute('data-border-color') || '#00825a';
  const POSITION = currentScript.getAttribute('data-position') || 'right';
  const LAUNCHER_ATTR = currentScript.getAttribute('data-launcher') || currentScript.getAttribute('data-mode') || '';
  const isChatOnlyLauncher = LAUNCHER_ATTR === 'chat' || (typeof window !== 'undefined' && window.location.pathname.startsWith('/workspace'));
  
  // Universal 2D Question Icon & Vector Support Engine
  const DEFAULT_AVATAR = '/brand-assets/firby-isotype.png?v=20261004_chat_negro';
  const customAvatarAttr = currentScript.getAttribute('data-avatar');
  const AVATAR_URL = customAvatarAttr || DEFAULT_AVATAR;
  const isCustomAvatar = Boolean(customAvatarAttr && customAvatarAttr !== DEFAULT_AVATAR);

  const FIRBY_ANIMATED_AVATAR_HTML = `
    <picture class="firby-avatar-animated-picture firby-header-avatar-picture">
      <source srcset="/assets/eyes.webp?v=20261009_eyes_v2" type="image/webp">
      <source srcset="/assets/eyes.png?v=20261009_eyes_v2" type="image/png">
      <img src="/assets/eyes.webp?v=20261009_eyes_v2" alt="Firby" class="firby-avatar-fallback-img firby-header-avatar-img" onerror="this.src='${DEFAULT_AVATAR}'" />
    </picture>
  `.trim();

  const getFirbyAvatarHtml = (isHeader = false) => {
    if (isCustomAvatar) {
      const cls = isHeader ? 'firby-header-avatar-img' : 'firby-msg-avatar-img';
      return `<img src="${AVATAR_URL}" alt="Firby" class="${cls}" onerror="this.src='${DEFAULT_AVATAR}'" />`;
    }
    if (isHeader) {
      return FIRBY_ANIMATED_AVATAR_HTML;
    }
    return `
      <picture class="firby-msg-avatar-picture">
        <source srcset="/assets/isotipo_firby4.webp" type="image/webp">
        <img src="/assets/isotipo_firby4.png" alt="Firby" class="firby-msg-avatar-img" onerror="this.src='${DEFAULT_AVATAR}'" />
      </picture>
    `.trim();
  };
  const BUTTON_ICON_URL = currentScript.getAttribute('data-button-icon') || '';

  const isLanding = ORG_ID === 'firby_landing' || ORG_ID === 'firby_default' || ORG_ID === 'firby' || !ORG_ID;
  const rawTitle = currentScript.getAttribute('data-title');
  const OPERATOR_TITLE = isLanding ? 'Firby' : (rawTitle && rawTitle !== 'Asistente virtual' ? rawTitle : 'Firby');

  const SESSION_KEY = 'firby_widget_session_id';
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = 'web_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
    localStorage.setItem(SESSION_KEY, sessionId);
  }

  // Inject Design System & Typography Styles
  const styleEl = document.createElement('style');
  styleEl.innerHTML = `
    .firby-widget-container {
      position: fixed;
      bottom: 92px;
      ${POSITION === 'left' ? 'left: 24px;' : 'right: 24px;'}
      z-index: 9999999;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }

    /* Teaser Pill — Micro-interacción limpia y sobria */
    .firby-teaser-pill {
      position: absolute;
      bottom: 74px;
      ${POSITION === 'left' ? 'left: 0;' : 'right: 0;'}
      background: #09090b;
      color: #f4f4f5;
      padding: 8px 16px;
      border-radius: 20px;
      box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16), 0 2px 6px rgba(0, 0, 0, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 12.5px;
      font-weight: 500;
      letter-spacing: -0.01em;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      animation: firbyFloat 4s ease-in-out infinite;
      transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1), transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      user-select: none;
    }
    .firby-teaser-pill:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 32px rgba(0, 0, 0, 0.22);
      color: #ffffff;
    }
    .firby-teaser-pill.hide {
      opacity: 0;
      pointer-events: none;
      transform: translateY(8px);
    }
    @keyframes firbyFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-3px); }
    }

    /* Copilot Vision & UI Spotlight Engine */
    @keyframes firbyCopilotGlow {
      0% {
        box-shadow: 0 0 0 0 rgba(185, 250, 1, 0.65), 0 8px 24px rgba(185, 250, 1, 0.2);
      }
      50% {
        box-shadow: 0 0 0 20px rgba(185, 250, 1, 0), 0 16px 40px rgba(185, 250, 1, 0.35);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(185, 250, 1, 0), 0 0 0 rgba(185, 250, 1, 0);
      }
    }
    .firby-copilot-highlight {
      animation: firbyCopilotGlow 2.8s cubic-bezier(0.25, 1, 0.5, 1) 1 !important;
      outline: 2px solid rgba(185, 250, 1, 0.95) !important;
      outline-offset: 8px !important;
      border-radius: 18px !important;
      transition: outline 0.4s ease, box-shadow 0.4s ease !important;
    }
    .firby-copilot-nav-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      margin: 8px auto;
      font-size: 12px;
      font-weight: 600;
      color: #2c2a29;
      background: rgba(185, 250, 1, 0.22);
      border: 1px solid rgba(185, 250, 1, 0.5);
      border-radius: 9999px;
      animation: firbyFadeIn 0.3s ease;
    }
    .firby-copilot-spinner {
      width: 10px;
      height: 10px;
      border: 2px solid #2c2a29;
      border-top-color: transparent;
      border-radius: 50%;
      animation: firbySpin 0.7s linear infinite;
    }
    @keyframes firbySpin {
      to { transform: rotate(360deg); }
    }
    @keyframes firbyFadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Sierra AI Typography & Structured List Items */
    .firby-msg-agent strong {
      color: #111827;
      font-weight: 700;
    }
    html.dark .firby-msg-agent strong,
    html[data-theme="dark"] .firby-msg-agent strong {
      color: #f3f4f6;
    }
    .firby-bullet-item {
      display: flex;
      align-items: baseline;
      gap: 8px;
      margin: 5px 0;
      line-height: 1.5;
    }
    .firby-bullet-dot {
      display: inline-block;
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background-color: #b0f550;
      flex-shrink: 0;
      transform: translateY(-2px);
    }

    @font-face {
      font-family: 'Satoshi';
      src: url('/assets/fonts/Satoshi-Light.woff2') format('woff2'),
           url('/assets/fonts/Satoshi-Light.woff') format('woff'),
           url('/assets/fonts/Satoshi-Light.ttf') format('truetype');
      font-weight: 300;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'Satoshi';
      src: url('/assets/fonts/Satoshi-Regular.woff2') format('woff2'),
           url('/assets/fonts/Satoshi-Regular.woff') format('woff'),
           url('/assets/fonts/Satoshi-Regular.ttf') format('truetype');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'Satoshi';
      src: url('/assets/fonts/Satoshi-Medium.woff2') format('woff2'),
           url('/assets/fonts/Satoshi-Medium.woff') format('woff'),
           url('/assets/fonts/Satoshi-Medium.ttf') format('truetype');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'Satoshi';
      src: url('/assets/fonts/Satoshi-Bold.woff2') format('woff2'),
           url('/assets/fonts/Satoshi-Bold.woff') format('woff'),
           url('/assets/fonts/Satoshi-Bold.ttf') format('truetype');
      font-weight: 600 700;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'General Sans';
      src: url('/assets/fonts/GeneralSans-Light.woff2') format('woff2'),
           url('/assets/fonts/GeneralSans-Light.woff') format('woff'),
           url('/assets/fonts/GeneralSans-Light.ttf') format('truetype');
      font-weight: 300;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'General Sans';
      src: url('/assets/fonts/GeneralSans-Regular.woff2') format('woff2'),
           url('/assets/fonts/GeneralSans-Regular.woff') format('woff'),
           url('/assets/fonts/GeneralSans-Regular.ttf') format('truetype');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'General Sans';
      src: url('/assets/fonts/GeneralSans-Medium.woff2') format('woff2'),
           url('/assets/fonts/GeneralSans-Medium.woff') format('woff'),
           url('/assets/fonts/GeneralSans-Medium.ttf') format('truetype');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }
    @font-face {
      font-family: 'Averta';
      src: url('/assets/fonts/AvertaDemoPE-Regular.woff2') format('woff2'),
           url('/assets/fonts/AvertaDemoPE-Regular.woff') format('woff'),
           url('/assets/fonts/Averta-Regular.ttf') format('truetype');
      font-weight: 400 800;
      font-style: normal;
      font-display: swap;
    }

    /* Help Widget Menu — Idéntico a Wompi (bws-help-widget) */
    .bws-hw {
      position: fixed;
      bottom: 24px;
      ${POSITION === 'left' ? 'left: 24px;' : 'right: 24px;'}
      z-index: 9999999;
      font-family: 'Satoshi', 'General Sans', 'Averta', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Open Sans", Helvetica, Arial, sans-serif;
      pointer-events: none;
    }
    .bws-hw.chat-open {
      bottom: 20px !important;
    }

    .bws-hw-floating-btn {
      display: flex !important;
      pointer-events: auto !important;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.8), 0 12px 32px -4px rgba(0, 0, 0, 0.12), 0 4px 12px -2px rgba(0, 0, 0, 0.04);
      cursor: pointer;
      align-items: center;
      justify-content: center;
      transition: transform 0.24s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.24s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.2s ease, border-color 0.2s ease;
      outline: none;
      user-select: none;
      position: relative;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
      text-decoration: none;
    }

    .bws-hw-floating-btn:hover {
      transform: translateY(-2px) scale(1.02);
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.9), 0 16px 36px -4px rgba(0, 0, 0, 0.16), 0 6px 14px -2px rgba(0, 0, 0, 0.06);
    }

    .bws-hw-floating-btn:active {
      transform: scale(0.96);
    }

    .firby-btn-icon {
      position: absolute;
      inset: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      color: inherit;
      transition: opacity 0.25s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .firby-btn-question-icon {
      opacity: 1;
      transform: rotate(0deg) scale(1);
    }

    .firby-question-img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 50%;
      display: block;
      pointer-events: none;
      user-select: none;
    }

    .firby-btn-close-icon {
      opacity: 0;
      transform: rotate(-90deg) scale(0.8);
      pointer-events: none;
    }

    .bws-hw.bws-hw-active .bws-hw-floating-btn,
    .bws-hw-floating-btn.is-open {
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(0, 0, 0, 0.12);
      box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.16);
    }

    .bws-hw.bws-hw-active .bws-hw-floating-btn .firby-btn-question-icon,
    .bws-hw-floating-btn.is-open .firby-btn-question-icon {
      opacity: 0;
      transform: rotate(180deg) scale(0.8);
      pointer-events: none;
    }

    .bws-hw.bws-hw-active .bws-hw-floating-btn .firby-btn-close-icon,
    .bws-hw-floating-btn.is-open .firby-btn-close-icon {
      opacity: 1;
      transform: rotate(0deg) scale(1);
      animation: 0.26s firbyWompiClose cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes firbyWompiClose {
      0% { transform: rotate(-90deg) scale(0.7); }
      100% { transform: rotate(0deg) scale(1); }
    }

    .bws-hw.bws-hw-active .bws-hw-floating-btn .firby-btn-chat-icon,
    .bws-hw-floating-btn.is-open .firby-btn-chat-icon {
      opacity: 0;
      transform: rotate(180deg) scale(0.8);
      pointer-events: none;
    }

    /* Mode: Chat-Only Compact Launcher (Sin '?', Solo Chat Firby, Más Grande y a la Izquierda) */
    .bws-hw-chat-only {
      bottom: 28px !important;
      right: 40px !important;
      z-index: 9999999 !important;
    }
    .bws-hw-chat-only .bws-hw-menu {
      display: none !important;
    }
    .bws-hw-chat-only .firby-teaser-pill {
      display: none !important;
    }
    .bws-hw-chat-only .bws-hw-floating-btn {
      width: 60px !important;
      height: 60px !important;
      color: #2C2A29;
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.9), 0 10px 24px -4px rgba(0, 0, 0, 0.12), 0 4px 10px -2px rgba(0, 0, 0, 0.04) !important;
    }
    .bws-hw-chat-only .bws-hw-floating-btn:hover {
      transform: translateY(-2px) scale(1.04) !important;
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.9), 0 14px 28px -4px rgba(0, 0, 0, 0.16) !important;
    }
    .bws-hw-chat-only .firby-btn-chat-icon svg {
      width: 29px !important;
      height: 24px !important;
    }
    .bws-hw-chat-only .firby-btn-close-icon svg {
      width: 22px !important;
      height: 22px !important;
    }
    .bws-hw-chat-only .firby-chat-window {
      bottom: 76px !important;
    }
    .firby-dark-mode.bws-hw-chat-only .bws-hw-floating-btn,
    html.dark .bws-hw-chat-only .bws-hw-floating-btn,
    html[data-theme="dark"] .bws-hw-chat-only .bws-hw-floating-btn {
      background: #141416 !important;
      border: 1px solid rgba(185, 250, 1, 0.28) !important;
      box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.7), 0 0 16px -2px rgba(185, 250, 1, 0.15) !important;
      color: #b9fa01 !important;
    }
    .firby-dark-mode.bws-hw-chat-only .firby-btn-chat-icon,
    html.dark .bws-hw-chat-only .firby-btn-chat-icon,
    html[data-theme="dark"] .bws-hw-chat-only .firby-btn-chat-icon {
      color: #b9fa01 !important;
    }
    .firby-dark-mode.bws-hw-chat-only .firby-btn-chat-icon svg,
    html.dark .bws-hw-chat-only .firby-btn-chat-icon svg,
    html[data-theme="dark"] .bws-hw-chat-only .firby-btn-chat-icon svg {
      color: #b9fa01 !important;
    }
    .firby-dark-mode.bws-hw-chat-only .firby-btn-chat-icon svg path,
    html.dark .bws-hw-chat-only .firby-btn-chat-icon svg path,
    html[data-theme="dark"] .bws-hw-chat-only .firby-btn-chat-icon svg path {
      fill: #b9fa01 !important;
    }
    .firby-dark-mode.bws-hw-chat-only .firby-btn-close-icon,
    html.dark .bws-hw-chat-only .firby-btn-close-icon,
    html[data-theme="dark"] .bws-hw-chat-only .firby-btn-close-icon {
      color: #ffffff !important;
    }
    .firby-dark-mode.bws-hw-chat-only .firby-btn-close-icon svg path,
    html.dark .bws-hw-chat-only .firby-btn-close-icon svg path,
    html[data-theme="dark"] .bws-hw-chat-only .firby-btn-close-icon svg path {
      fill: #ffffff !important;
    }
    @media (prefers-color-scheme: dark) {
      .bws-hw-chat-only .bws-hw-floating-btn {
        background: #141416 !important;
        border: 1px solid rgba(185, 250, 1, 0.28) !important;
        color: #b9fa01 !important;
      }
      .bws-hw-chat-only .firby-btn-chat-icon svg path {
        fill: #b9fa01 !important;
      }
      .bws-hw-chat-only .firby-btn-close-icon svg path {
        fill: #ffffff !important;
      }
    }
    @media (max-width: 768px) {
      .bws-hw-chat-only {
        bottom: max(22px, env(safe-area-inset-bottom, 22px)) !important;
        right: 28px !important;
      }
      .bws-hw-chat-only .bws-hw-floating-btn {
        width: 54px !important;
        height: 54px !important;
      }
      .bws-hw-chat-only .firby-btn-chat-icon svg {
        width: 26px !important;
        height: 21px !important;
      }
      .bws-hw-chat-only .firby-btn-close-icon svg {
        width: 20px !important;
        height: 20px !important;
      }
      .bws-hw-chat-only .firby-chat-window {
        bottom: 0 !important;
      }
    }

    /* Ambient Depth Glow - Degradado Verde Wompi / Firby */
    .bws-hw::after {
      content: '';
      position: absolute;
      bottom: -6em;
      ${POSITION === 'left' ? 'left: -6em;' : 'right: -6em;'}
      width: 20em;
      height: 20em;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(223,255,97,0.92) 11%, rgba(176,242,174,0.75) 28%, rgba(176,242,174,0.45) 43%, rgba(176,242,174,0.18) 55%, rgba(255,255,255,0) 65%);
      z-index: -2;
      transform: scale3d(0, 0, 1);
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
      opacity: 0;
      pointer-events: none;
    }

    .bws-hw.bws-hw-active::after,
    .bws-hw.chat-open::after,
    .bws-hw.is-active::after {
      opacity: 1;
      width: 20em;
      height: 20em;
      bottom: -6em;
      ${POSITION === 'left' ? 'left: -6em;' : 'right: -6em;'}
      background: radial-gradient(circle, rgba(223,255,97,0.92) 11%, rgba(176,242,174,0.75) 28%, rgba(176,242,174,0.45) 43%, rgba(176,242,174,0.18) 55%, rgba(255,255,255,0) 65%);
      transform: scale3d(4, 4, 1);
    }

    /* Menu & Floating Options */
    .bws-hw-menu {
      padding: 0;
      margin: 0;
      list-style: none;
    }

    .bws-hw-item {
      position: absolute;
      bottom: 0;
      ${POSITION === 'left' ? 'left: 0;' : 'right: 0;'}
      z-index: -1;
      display: flex;
      justify-content: center;
      align-items: center;
      text-decoration: none;
      color: #0f172a;
      font-size: 16px;
      width: 56px;
      height: 56px;
      background: rgba(255, 255, 255, 0.90);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.8), 0 10px 24px -4px rgba(0, 0, 0, 0.10);
      border-radius: 50%;
      text-align: center;
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.2s ease, opacity 0.22s ease, box-shadow 0.2s ease;
      opacity: 0;
      pointer-events: none;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
    }

    .bws-hw-item > img {
      width: 28px;
      height: auto;
      max-width: 30px;
      max-height: 30px;
      transition: filter 0.2s ease;
      display: block;
    }

    .bws-hw-item > svg {
      width: 24px;
      height: 24px;
      color: #2c2a29;
      transition: color 0.2s ease;
      display: block;
    }

    .bws-hw-item:hover {
      background-color: #ffffff;
      transform: scale(1.05);
      box-shadow: 0 14px 30px -4px rgba(0, 0, 0, 0.14);
    }

    .bws-hw-item:active {
      transform: scale(0.95);
    }

    .bws-hw-item .bws-hw-text {
      color: #0f172a;
      font-size: 13.5px;
      font-weight: 600;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      ${POSITION === 'left' ? 'left: 70px; text-align: left;' : 'right: 70px; text-align: right;'}
      z-index: -1;
      display: inline-flex;
      align-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      letter-spacing: -0.015em;
      white-space: nowrap;
      pointer-events: none;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      padding: 7px 15px;
      border-radius: 9999px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.85), 0 6px 18px rgba(0, 0, 0, 0.07);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .bws-hw-item:hover .bws-hw-text {
      background: #ffffff;
      color: #0f172a;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.10);
    }

    /* Active State for Menu Items */
    .bws-hw.bws-hw-active .bws-hw-item {
      opacity: 1;
      pointer-events: auto;
      z-index: 100 !important;
    }

    .bws-hw.bws-hw-active .bws-hw-item .bws-hw-text {
      pointer-events: auto;
      z-index: 101 !important;
    }

    /* 1: Chatea con Firby */
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(1) {
      transform: translate3d(0, -350px, 0);
    }
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(1):hover {
      transform: translate3d(0, -350px, 0) scale(1.06);
    }
    /* 2: Sobre nosotros */
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(2) {
      transform: translate3d(0, -280px, 0);
    }
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(2):hover {
      transform: translate3d(0, -280px, 0) scale(1.06);
    }
    /* 3: Preguntas frecuentes */
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(3) {
      transform: translate3d(0, -210px, 0);
    }
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(3):hover {
      transform: translate3d(0, -210px, 0) scale(1.06);
    }
    /* 4: Escríbenos */
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(4) {
      transform: translate3d(0, -140px, 0);
    }
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(4):hover {
      transform: translate3d(0, -140px, 0) scale(1.06);
    }
    /* 5: WhatsApp */
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(5) {
      transform: translate3d(0, -70px, 0);
    }
    .bws-hw.bws-hw-active .bws-hw-item:nth-child(5):hover {
      transform: translate3d(0, -70px, 0) scale(1.08);
    }

    /* Header Actions: More Options (3 Dots) + Close */
    .firby-header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .firby-more-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: rgba(0, 0, 0, 0.04);
      border: 1px solid rgba(0, 0, 0, 0.06);
      color: #71717a;
      transition: all 0.18s ease;
      cursor: pointer;
      padding: 0;
      flex-shrink: 0;
    }
    .firby-more-btn:hover {
      background: rgba(0, 0, 0, 0.08);
      color: #09090b;
      transform: scale(1.05);
    }
    .firby-more-dropdown {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      background: #ffffff;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 10px;
      padding: 4px;
      min-width: 170px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
      display: none;
      z-index: 1000;
    }
    .firby-more-dropdown.show {
      display: block;
      animation: firbyFadeIn 0.15s ease-out;
    }
    .firby-dropdown-item {
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
      padding: 8px 12px;
      font-size: 13px;
      color: #374151;
      background: transparent;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.12s, color 0.12s;
      text-align: left;
      font-family: inherit;
    }
    .firby-dropdown-item:hover {
      background: rgba(0, 0, 0, 0.05);
      color: #111827;
    }

    /* Chat Window — Liquid Glass SaaS Premium */
    .firby-chat-window {
      position: absolute;
      bottom: 70px;
      ${POSITION === 'left' ? 'left: 0;' : 'right: 0;'}
      width: 400px;
      max-width: calc(100vw - 32px);
      height: 475px;
      max-height: calc(100vh - 105px);
      font-family: 'Satoshi', 'General Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
      background: rgba(255, 255, 255, 0.84);
      backdrop-filter: blur(24px) saturate(140%) brightness(103%);
      -webkit-backdrop-filter: blur(24px) saturate(140%) brightness(103%);
      border-radius: 26px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: inset 0 1px 0.5px rgba(255, 255, 255, 0.75), 0 24px 64px -12px rgba(0, 0, 0, 0.16), 0 8px 20px -4px rgba(0, 0, 0, 0.06);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      pointer-events: none;
      transform: translateY(20px) scale(0.96);
      transform-origin: bottom right;
      transition: opacity 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.32s cubic-bezier(0.16, 1, 0.3, 1),
                  filter 0.28s cubic-bezier(0.16, 1, 0.3, 1);
      filter: blur(6px);
      contain: layout style;
    }
    .firby-chat-window.open {
      opacity: 1;
      pointer-events: auto;
      transform: translateY(0) scale(1);
      filter: blur(0px);
    }

    /* Mobile Drag Handle */
    .firby-mobile-drag-handle {
      display: none;
      align-items: center;
      justify-content: center;
      padding: 8px 0 2px 0;
      width: 100%;
      cursor: grab;
      touch-action: none;
      background: transparent;
      user-select: none;
    }
    .firby-drag-pill {
      width: 36px;
      height: 4.5px;
      border-radius: 9999px;
      background: rgba(0, 0, 0, 0.16);
    }

    /* Header — Interfaz Ejecutiva y Limpia */
    .firby-chat-header {
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      color: #09090b;
      padding: 13px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(0, 0, 0, 0.06);
      position: relative;
      z-index: 10;
      flex-shrink: 0;
    }

    /* Integrated Agent Surface Activity Bar (Dentro del Chat) */
    .firby-chat-activity-bar {
      max-height: 0;
      opacity: 0;
      overflow: hidden;
      background: rgba(0, 130, 90, 0.05);
      border-bottom: 1px solid transparent;
      transition: max-height 0.28s cubic-bezier(0.16, 1, 0.3, 1),
                  opacity 0.24s cubic-bezier(0.16, 1, 0.3, 1),
                  border-color 0.24s ease,
                  background-color 0.24s ease;
      z-index: 9;
      flex-shrink: 0;
    }
    .firby-chat-activity-bar.active {
      max-height: 38px;
      opacity: 1;
      border-bottom-color: rgba(0, 130, 90, 0.12);
    }
    .firby-activity-inner {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 16px;
      height: 38px;
      box-sizing: border-box;
    }
    .firby-activity-presence {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .firby-activity-dot {
      width: 6.5px;
      height: 6.5px;
      border-radius: 50%;
      background: #00825a;
      animation: firbyActivityPulse 2.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
      flex-shrink: 0;
    }
    @keyframes firbyActivityPulse {
      0%, 100% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 0 3.5px rgba(0, 130, 90, 0.2); }
    }
    .firby-activity-brand {
      font-size: 11.5px;
      font-weight: 600;
      letter-spacing: -0.01em;
      color: #09090b;
    }
    .firby-activity-divider {
      width: 1px;
      height: 12px;
      background: rgba(0, 0, 0, 0.1);
    }
    .firby-activity-text {
      font-size: 12px;
      font-weight: 350;
      letter-spacing: -0.01em;
      color: #475569;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .firby-activity-cancel {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: none;
      background: transparent;
      color: #64748b;
      cursor: pointer;
      padding: 0;
      transition: all 0.15s ease;
    }
    .firby-activity-cancel:hover {
      background: rgba(0, 0, 0, 0.08);
      color: #0f172a;
    }

    /* Floating Scroll-to-Bottom Pill for New Messages */
    .firby-scroll-bottom-pill {
      position: absolute;
      bottom: 64px;
      left: 50%;
      transform: translateX(-50%) translateY(10px) scale(0.95);
      opacity: 0;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.88);
      color: #ffffff;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 9999px;
      padding: 6px 14px;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: -0.01em;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
      z-index: 20;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
                  opacity 0.18s ease;
    }
    .firby-scroll-bottom-pill.visible {
      transform: translateX(-50%) translateY(0) scale(1);
      opacity: 1;
      pointer-events: auto;
    }
    .firby-scroll-bottom-pill:hover {
      background: rgba(15, 23, 42, 0.96);
      transform: translateX(-50%) translateY(-2px) scale(1.02);
    }
    .firby-header-profile {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .firby-header-avatar-wrap {
      width: 28px;
      height: 28px;
      background: transparent !important;
      background-color: transparent !important;
      border: none !important;
      box-shadow: none !important;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden !important;
      border-radius: 50% !important;
      -webkit-border-radius: 50% !important;
      -webkit-mask-image: -webkit-radial-gradient(white, black);
      mask-image: radial-gradient(white, black);
      flex-shrink: 0;
    }
    .firby-header-avatar-img,
    .firby-avatar-fallback-img,
    .firby-avatar-animated-picture,
    .firby-header-avatar-picture,
    .firby-header-avatar-wrap picture,
    .firby-header-avatar-wrap img,
    .firby-header-avatar-wrap video {
      width: 26px;
      height: 26px;
      border-radius: 50% !important;
      -webkit-border-radius: 50% !important;
      object-fit: contain;
      background: transparent !important;
      background-color: transparent !important;
      border: none !important;
      box-shadow: none !important;
      display: block;
      pointer-events: none;
    }
    .firby-header-title {
      font-family: inherit;
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.015em;
      margin: 0;
      color: #09090b;
      line-height: 1.2;
    }
    .firby-header-status {
      display: flex;
      align-items: center;
      margin-top: 2px;
    }
    .firby-status-dot {
      display: none !important;
    }
    .firby-status-text {
      font-family: inherit;
      font-size: 11.5px;
      color: #71717a;
      font-weight: 300;
      line-height: 1;
      letter-spacing: -0.01em;
      opacity: 0.85;
    }
    .firby-title-dark {
      display: none;
    }

    /* Stream Time Badge (Estilo Wompi) */
    .firby-stream-time-badge {
      align-self: center;
      font-family: inherit;
      font-size: 11px;
      font-weight: 350;
      color: #71717a;
      margin: 2px 0 10px 0;
      letter-spacing: -0.01em;
      user-select: none;
    }

    /* Message Row con Avatar del Agente a la Izquierda */
    .firby-msg-row {
      display: flex;
      align-items: flex-start;
      gap: 9px;
      width: 100%;
      animation: firbyFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .firby-msg-row-agent {
      justify-content: flex-start;
    }
    .firby-msg-avatar-wrap {
      width: 24px;
      height: 24px;
      background: transparent !important;
      background-color: transparent !important;
      border: none !important;
      box-shadow: none !important;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 4px;
    }
    .firby-msg-avatar-img,
    .firby-msg-avatar-wrap video,
    .firby-msg-avatar-wrap picture {
      width: 22px;
      height: 22px;
      object-fit: contain;
      background: transparent !important;
      background-color: transparent !important;
      border: none !important;
      box-shadow: none !important;
      display: block;
      pointer-events: none;
    }
    .firby-msg-content-wrap {
      display: flex;
      flex-direction: column;
      max-width: calc(100% - 34px);
    }

    /* Message Author Tag (Wompi) */
    .firby-msg-author {
      font-family: inherit;
      font-size: 12px;
      font-weight: 550;
      color: #27272a;
      margin: 0 0 4px 2px;
      letter-spacing: -0.01em;
    }

    /* Policy Bubble Styling: Gris claro, sin trazo */
    .firby-policy-bubble {
      align-self: flex-start;
      background: #eceff2;
      color: #09090b;
      border: none;
      border-radius: 18px 18px 18px 4px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      padding: 14px 16px;
      max-width: 100%;
      font-size: 13.5px;
      line-height: 1.55;
    }
    .firby-policy-title {
      font-family: inherit;
      font-size: 13.5px;
      font-weight: 600;
      color: #09090b;
      margin-bottom: 4px;
      letter-spacing: -0.015em;
    }
    .firby-policy-text {
      font-family: inherit;
      font-size: 13px;
      line-height: 1.55;
      font-weight: 300;
      color: #27272a;
      margin-bottom: 8px;
      letter-spacing: -0.01em;
    }
    .firby-policy-link-row {
      margin-bottom: 8px;
    }
    .firby-policy-link {
      color: #00825a;
      text-decoration: underline;
      font-size: 12.5px;
      font-weight: 500;
      word-break: break-all;
      transition: color 0.15s, opacity 0.15s;
    }
    .firby-policy-link:hover {
      color: #006847;
      opacity: 0.85;
    }
    .firby-msg-meta {
      display: flex;
      justify-content: flex-end;
      margin-top: 4px;
    }
    .firby-msg-time {
      font-size: 10px;
      color: #71717a;
      letter-spacing: 0.01em;
    }

    /* Consent Button (Wompi Tactile Action Style) */
    .firby-consent-container {
      align-self: flex-start;
      margin: 14px 0 6px 0;
      display: flex;
      animation: firbyFadeIn 0.2s ease;
    }
    .firby-consent-btn {
      background: #ffffff;
      color: #09090b;
      border: 1.5px solid #09090b;
      border-radius: 20px;
      padding: 8px 18px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.01em;
      cursor: pointer;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
      transition: all 0.16s cubic-bezier(0.16, 1, 0.3, 1);
      outline: none;
      user-select: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .firby-consent-btn:hover {
      background: #09090b;
      color: #ffffff;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.14);
    }
    .firby-consent-btn:active {
      transform: scale(0.96);
    }
    .firby-close-btn {
      background: rgba(0, 0, 0, 0.04);
      border: 1px solid rgba(0, 0, 0, 0.06);
      color: #71717a;
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s, color 0.15s, transform 0.15s;
    }
    .firby-close-btn:hover {
      background: rgba(0, 0, 0, 0.08);
      color: #09090b;
    }

    /* Messages Stream — Lienzo sutilmente contrastado para que las burbujas blancas resalten */
    .firby-messages-stream {
      flex: 1;
      overflow-y: auto;
      padding: 18px 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background-color: #f6f8fa;
      background-image: radial-gradient(rgba(0, 0, 0, 0.06) 1.1px, transparent 1.1px);
      background-size: 16px 16px;
      scroll-behavior: smooth;
    }

    /* Suggestions Dock — Barra Horizontal Justo Arriba del Input */
    .firby-suggestions-dock {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 8px 14px;
      background: #ffffff;
      border-top: 1px solid rgba(0, 0, 0, 0.06);
      overflow-x: auto;
      white-space: nowrap;
      scrollbar-width: none;
      -ms-overflow-style: none;
      user-select: none;
      transition: opacity 0.18s ease;
    }
    .firby-suggestions-dock::-webkit-scrollbar {
      display: none;
    }
    .firby-chip {
      flex-shrink: 0;
      background: #ffffff;
      border: 1px solid rgba(0, 0, 0, 0.1);
      border-radius: 18px;
      padding: 6px 13px;
      font-size: 12px;
      color: #18181b;
      cursor: pointer;
      font-weight: 500;
      letter-spacing: -0.01em;
      transition: border-color 0.15s, background 0.15s, transform 0.15s, box-shadow 0.15s;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .firby-chip:hover {
      border-color: #09090b;
      background: #f4f5f7;
      transform: translateY(-1px);
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
    }
    .firby-chip:active {
      transform: scale(0.97);
    }

    /* Message Bubbles — Tipografía Light Premium */
    .firby-msg {
      font-family: 'Satoshi', 'General Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 88%;
      padding: 12px 16px;
      font-size: 13.5px;
      font-weight: 300;
      line-height: 1.58;
      word-break: break-word;
      letter-spacing: -0.012em;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      text-rendering: optimizeLegibility;
    }

    /* USER BUBBLE: Blanco puro elevado que resalta del fondo */
    .firby-msg-user {
      align-self: flex-end;
      background: #ffffff;
      color: #09090b;
      font-weight: 350;
      border-radius: 18px 18px 4px 18px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.03);
    }

    /* AGENT BUBBLE: Gris claro, sin trazo */
    .firby-msg-agent {
      align-self: flex-start;
      background: #eceff2;
      color: #09090b;
      font-weight: 300;
      border: none;
      border-radius: 18px 18px 18px 4px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .firby-msg-agent strong {
      color: #09090b;
      font-weight: 550;
    }
    .firby-msg-agent em {
      color: #27272a;
    }

    /* Action Cards */
    .firby-card-container {
      align-self: flex-start;
      margin-top: 4px;
      margin-bottom: 4px;
      width: 100%;
      max-width: 88%;
    }
    .firby-google-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      width: 100%;
      box-sizing: border-box;
      background: #ffffff;
      color: #1f1f1f;
      border: 1px solid #dadce0;
      border-radius: 16px;
      padding: 11px 18px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      transition: transform 0.16s, box-shadow 0.16s, border-color 0.16s;
      cursor: pointer;
    }
    .firby-google-btn:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 18px rgba(66, 133, 244, 0.18);
      border-color: #4285f4;
    }
    .firby-google-btn:active {
      transform: scale(0.98);
    }
    .firby-google-icon {
      flex-shrink: 0;
      width: 18px;
      height: 18px;
    }
    .firby-action-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      width: 100%;
      box-sizing: border-box;
      background: #111216;
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 16px;
      padding: 10px 16px;
      font-size: 13px;
      font-weight: 500;
      text-decoration: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transition: transform 0.16s, background 0.16s;
      cursor: pointer;
    }
    .firby-action-btn:hover {
      transform: translateY(-1px);
      background: #1f2028;
    }

    /* REACT BITS LATTICE LOADER THINKING STATE */
    .firby-orb-thinking {
      align-self: flex-start;
      margin: 6px 0 12px 0;
      display: flex;
      align-items: center;
      background: transparent !important;
      animation: firbyFadeIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes firbyFadeIn {
      from { opacity: 0; transform: scale(0.94); }
      to { opacity: 1; transform: scale(1); }
    }
    .firby-thinking-badge {
      display: inline-flex;
      align-items: center;
      padding: 7px 14px 7px 10px;
      background: #ffffff;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 9999px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
      color: #18181b;
    }
    .lattice-loader {
      --ll-n: 3;
      --ll-cell: 5.5px;
      --ll-gap: 2px;
      --ll-font: 13px;
      --ll-color: currentColor;
      --ll-mark: #22c55e;
      --ll-idle: 0.15;
      --ll-glow: currentColor;
      --ll-mark-glow: #22c55e;
      --ll-peak: 1;
      --ll-cycle: 864ms;
      --ll-ease-out: cubic-bezier(0.23, 1, 0.32, 1);
      --ll-ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

      position: relative;
      display: inline-flex;
      align-items: center;
      gap: calc(var(--ll-font) * 0.625);
      font-family: inherit;
      font-size: var(--ll-font);
      line-height: 1;
    }

    .lattice-loader__grid {
      display: grid;
      flex: none;
    }

    .lattice-loader__layer {
      grid-area: 1 / 1;
      display: grid;
      grid-template-columns: repeat(var(--ll-n), var(--ll-cell));
      gap: var(--ll-gap);
    }

    .lattice-loader__cell {
      width: var(--ll-cell);
      height: var(--ll-cell);
      border-radius: max(1px, calc(var(--ll-cell) * 0.25));
      background: var(--ll-color);
      opacity: var(--ll-idle);
    }

    .lattice-loader[data-shape='round'] .lattice-loader__cell {
      border-radius: 50%;
    }

    .lattice-loader[data-glow] .lattice-loader__run .lattice-loader__cell:not([data-hole]) {
      box-shadow: 0 0 calc(var(--ll-cell) * 1.2) calc(var(--ll-cell) * 0.12) var(--ll-glow);
    }

    .lattice-loader[data-glow] .lattice-loader__mark .lattice-loader__cell[data-on] {
      box-shadow: 0 0 calc(var(--ll-cell) * 1.2) calc(var(--ll-cell) * 0.12) var(--ll-mark-glow);
    }

    .lattice-loader__run {
      transition: opacity 200ms ease;
    }

    .lattice-loader__run .lattice-loader__cell {
      animation: lattice-on var(--ll-cycle) var(--ll-ease-in-out) infinite;
    }

    .lattice-loader__run .lattice-loader__cell[data-lit='45'] {
      animation-name: lattice-on-45;
    }

    .lattice-loader__run .lattice-loader__cell[data-lit='35'] {
      animation-name: lattice-on-35;
    }

    .lattice-loader__run .lattice-loader__cell[data-lit='25'] {
      animation-name: lattice-on-25;
    }

    .lattice-loader__run .lattice-loader__cell[data-hole] {
      animation: none;
      opacity: calc(var(--ll-idle) * 0.47);
    }

    .lattice-loader__mark {
      opacity: 0;
      transform: scale(0.9);
      transform-origin: center;
      transition:
        opacity 160ms var(--ll-ease-out),
        transform 160ms var(--ll-ease-out);
    }

    .lattice-loader__mark .lattice-loader__cell {
      transition:
        opacity 200ms ease,
        background-color 200ms ease;
    }

    .lattice-loader__mark .lattice-loader__cell[data-on] {
      background: var(--ll-mark);
      opacity: var(--ll-peak);
    }

    .lattice-loader:not([data-status='working']) .lattice-loader__run {
      opacity: 0;
    }

    .lattice-loader:not([data-status='working']) .lattice-loader__run .lattice-loader__cell {
      animation-play-state: paused;
    }

    .lattice-loader:not([data-status='working']) .lattice-loader__mark {
      opacity: 1;
      transform: none;
      transition:
        opacity 200ms ease,
        transform 200ms var(--ll-ease-out);
    }

    .lattice-loader__label {
      position: relative;
      display: inline-block;
      font-weight: 500;
    }

    .lattice-loader__text {
      position: absolute;
      top: 0;
      left: 0;
      white-space: nowrap;
      opacity: 0;
      filter: blur(2px);
      transition:
        opacity 200ms ease,
        filter 200ms ease;
    }

    .lattice-loader__text[data-active] {
      position: static;
      opacity: 1;
      filter: blur(0);
    }

    .lattice-loader__timer {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: calc(var(--ll-font) * 0.875);
      font-variant-numeric: tabular-nums;
      opacity: 0.6;
    }

    .lattice-loader__sr {
      position: absolute;
      width: 1px;
      height: 1px;
      margin: -1px;
      padding: 0;
      border: 0;
      overflow: hidden;
      clip: rect(0 0 0 0);
      white-space: nowrap;
    }

    @keyframes lattice-on {
      0%,
      100% {
        opacity: var(--ll-idle);
      }

      18%,
      42% {
        opacity: var(--ll-peak);
      }

      62% {
        opacity: var(--ll-idle);
      }
    }

    @keyframes lattice-on-45 {
      0%,
      100% {
        opacity: var(--ll-idle);
      }

      13%,
      31% {
        opacity: var(--ll-peak);
      }

      45% {
        opacity: var(--ll-idle);
      }
    }

    @keyframes lattice-on-35 {
      0%,
      100% {
        opacity: var(--ll-idle);
      }

      10%,
      24% {
        opacity: var(--ll-peak);
      }

      35% {
        opacity: var(--ll-idle);
      }
    }

    @keyframes lattice-on-25 {
      0%,
      100% {
        opacity: var(--ll-idle);
      }

      7%,
      17% {
        opacity: var(--ll-peak);
      }

      25% {
        opacity: var(--ll-idle);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .lattice-loader__run {
        --ll-peak: 0.7;
      }

      .lattice-loader__run .lattice-loader__cell {
        animation-delay: 0ms !important;
        animation-duration: 1400ms !important;
      }

      .lattice-loader .lattice-loader__mark {
        transform: none;
      }

      .lattice-loader .lattice-loader__text {
        filter: none;
      }
    }

    /* Input Bar */
    .firby-input-bar {
      display: flex;
      align-items: center;
      padding: 10px 12px;
      background: #ffffff;
      border-top: 1px solid rgba(0, 0, 0, 0.06);
      gap: 7px;
      position: relative;
    }
    .firby-input-field {
      flex: 1;
      min-width: 0;
      border: 1px solid #e2e4e8;
      background: #f9fafb;
      border-radius: 20px;
      padding: 9px 15px;
      font-size: 13.5px;
      font-weight: 300;
      letter-spacing: -0.01em;
      font-family: inherit;
      color: #09090b;
      outline: none;
      transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
    }
    .firby-input-field:focus {
      border-color: #09090b;
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(9, 9, 11, 0.05);
    }
    .firby-input-field::placeholder {
      color: #a1a1aa;
      font-weight: 300;
      letter-spacing: -0.01em;
      font-family: inherit;
    }
    .firby-send-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #09090b;
      color: #ffffff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.15s, background 0.15s;
      flex-shrink: 0;
    }
    .firby-send-btn:hover {
      background: #27272a;
      transform: scale(1.05);
    }
    .firby-send-btn:active {
      transform: scale(0.95);
    }

    /* ── FLOW PREMIUM LIVE VOICE BUTTON (ESTILO CHATGPT / GEMINI LIVE) ── */
    .firby-send-btn.firby-flow-mode {
      background: #09090b !important;
      color: #b9fa01 !important;
      border: 1px solid rgba(185, 250, 1, 0.4) !important;
      box-shadow: 0 0 12px rgba(185, 250, 1, 0.25) !important;
      position: relative;
    }
    .firby-send-btn.firby-flow-mode:hover {
      background: #18181b !important;
      transform: scale(1.08) !important;
      box-shadow: 0 0 18px rgba(185, 250, 1, 0.45) !important;
    }
    .firby-send-btn.firby-flow-mode .firby-flow-icon {
      color: #b9fa01 !important;
      stroke: #b9fa01 !important;
      display: block !important;
    }
    .firby-send-btn.firby-flow-mode .firby-send-icon {
      display: none !important;
    }
    .firby-send-btn:not(.firby-flow-mode) .firby-flow-icon {
      display: none !important;
    }
    .firby-send-btn:not(.firby-flow-mode) .firby-send-icon {
      display: block !important;
    }

    /* ── MARCO PERIMETRAL VIVO DE PANTALLA COMPLETA (LIVE VOICE PERIMETER BORDER) ── */
    @property --firby-border-angle {
      syntax: "<angle>";
      inherits: false;
      initial-value: 0deg;
    }

    .firby-live-page-border {
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 999998;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.45s ease;
      box-sizing: border-box;
    }

    .firby-live-page-border.active {
      opacity: 1;
      visibility: visible;
    }

    .firby-live-page-border-glow {
      position: absolute;
      inset: 0;
      pointer-events: none;
      box-shadow: 
        inset 0 0 16px rgba(185, 250, 1, 0.45),
        inset 0 0 32px rgba(250, 204, 21, 0.28),
        inset 0 0 54px rgba(56, 189, 248, 0.18);
      animation: firbyBorderGlowPulse 3.5s ease-in-out infinite alternate;
    }

    .firby-live-page-border-line {
      position: absolute;
      inset: 0;
      box-sizing: border-box;
      padding: 3.5px;
      background: conic-gradient(
        from var(--firby-border-angle, 0deg),
        #facc15 0%,
        #b9fa01 22%,
        #09090b 42%,
        #38bdf8 62%,
        #09090b 78%,
        #b9fa01 90%,
        #facc15 100%
      );
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      animation: firbyRotateBorderAngle 7s linear infinite;
    }

    @keyframes firbyRotateBorderAngle {
      0% {
        --firby-border-angle: 0deg;
        filter: hue-rotate(0deg);
      }
      50% {
        filter: hue-rotate(180deg);
      }
      100% {
        --firby-border-angle: 360deg;
        filter: hue-rotate(360deg);
      }
    }

    @keyframes firbyBorderGlowPulse {
      0% {
        opacity: 0.65;
        filter: brightness(0.95);
      }
      100% {
        opacity: 1;
        filter: brightness(1.2);
      }
    }

    /* ── MODO VOZ 1 A 1 EN VIVO (LIVE VOICE OVERLAY) ── */
    .firby-live-voice-overlay {
      position: absolute;
      inset: 0;
      background: rgba(15, 18, 22, 0.96);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      z-index: 1000;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 24px;
      color: #ffffff;
      border-radius: 20px;
      animation: firbyFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes firbyFadeIn {
      from { opacity: 0; transform: scale(0.98); }
      to { opacity: 1; transform: scale(1); }
    }
    .firby-lvo-header {
      display: flex;
      align-items: center;
      justify-content: flex-end;
    }
    .firby-lvo-close-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.07);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #d4d4d8;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .firby-lvo-close-btn:hover {
      background: rgba(255, 255, 255, 0.16);
      color: #ffffff;
      transform: scale(1.08);
    }
    .firby-lvo-body {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 12px;
      margin: auto 0;
    }
    .firby-lvo-orb-wrapper {
      position: relative;
      width: 120px;
      height: 120px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .firby-lvo-orb {
      width: 96px;
      height: 96px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(185, 250, 1, 0.22) 0%, rgba(18, 22, 26, 0.85) 70%);
      border: 2px solid rgba(185, 250, 1, 0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 32px rgba(185, 250, 1, 0.22);
      transition: transform 0.12s ease-out, box-shadow 0.12s ease-out, border-color 0.25s ease;
      cursor: pointer;
    }
    .firby-lvo-orb.speaking {
      border-color: #b9fa01;
      box-shadow: 0 0 54px rgba(185, 250, 1, 0.55), inset 0 0 24px rgba(185, 250, 1, 0.35);
    }
    .firby-lvo-orb.listening {
      border-color: rgba(185, 250, 1, 0.65);
      box-shadow: 0 0 36px rgba(185, 250, 1, 0.3);
    }
    .firby-lvo-avatar-img {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      object-fit: contain;
      pointer-events: none;
    }
    /* Dynamic Audio-Reactive Canvas Visualizer */
    .firby-lvo-canvas-container {
      width: 100%;
      max-width: 320px;
      height: 65px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0;
    }
    .firby-lvo-canvas {
      width: 100%;
      height: 100%;
      display: block;
      pointer-events: none;
    }
    .firby-lvo-status-text {
      font-size: 14px;
      font-weight: 500;
      color: #d4d4d8;
      letter-spacing: -0.01em;
      min-height: 20px;
      cursor: pointer;
      transition: color 0.2s;
    }
    .firby-lvo-status-text:hover {
      color: #ffffff;
    }
    .firby-lvo-perm-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 9px 22px;
      background: #b9fa01;
      color: #09090b;
      font-weight: 700;
      font-size: 13px;
      border: none;
      border-radius: 100px;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(185, 250, 1, 0.35);
      transition: transform 0.15s ease, background 0.15s ease;
    }
    .firby-lvo-perm-btn:hover {
      background: #a6e000;
      transform: scale(1.04);
    }
    .firby-lvo-transcript-box {
      max-width: 320px;
      max-height: 90px;
      overflow-y: auto;
      font-size: 12.5px;
      line-height: 1.45;
      color: #a1a1aa;
      padding: 0 8px;
    }
    .firby-lvo-transcript-user {
      color: #ffffff;
      font-weight: 500;
      margin-bottom: 4px;
    }
    .firby-lvo-transcript-agent {
      color: #b9fa01;
      font-weight: 400;
    }
    .firby-lvo-footer {
      display: flex;
      align-items: center;
      justify-content: center;
      padding-bottom: 6px;
    }
    .firby-lvo-end-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 9px 26px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #e4e4e7;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .firby-lvo-end-pill:hover {
      background: rgba(239, 68, 68, 0.16);
      border-color: rgba(239, 68, 68, 0.4);
      color: #f87171;
      transform: translateY(-1px);
    }

    /* Botón de Audio / Grabación de voz (Al lado de Enviar) */
    .firby-voice-btn {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: #f4f4f6;
      color: #3f3f46;
      border: 1px solid #e4e4e7;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), background 0.18s, color 0.18s, box-shadow 0.18s;
      flex-shrink: 0;
      padding: 0;
      position: relative;
      outline: none;
    }
    .firby-voice-btn:hover {
      background: #e4e4e7;
      color: #09090b;
      transform: scale(1.05);
    }
    .firby-voice-btn:active {
      transform: scale(0.95);
    }
    .firby-voice-btn.recording {
      background: #09090b !important;
      color: #ffffff !important;
      border-color: rgba(255, 255, 255, 0.25) !important;
      animation: firbyMicPulse 1.4s infinite cubic-bezier(0.4, 0, 0.6, 1);
    }
    @keyframes firbyMicPulse {
      0% {
        box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.35);
      }
      70% {
        box-shadow: 0 0 0 8px rgba(255, 255, 255, 0);
      }
      100% {
        box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
      }
    }
    .firby-voice-active-waves {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 2.5px;
      height: 14px;
    }
    .firby-vw-bar {
      width: 2.5px;
      height: 4px;
      background: #ffffff;
      border-radius: 2px;
      animation: firbyVwAnim 0.7s ease-in-out infinite alternate;
    }
    .firby-vw-bar.vw-1 { animation-delay: 0s; height: 6px; }
    .firby-vw-bar.vw-2 { animation-delay: 0.22s; height: 13px; }
    .firby-vw-bar.vw-3 { animation-delay: 0.44s; height: 8px; }

    @keyframes firbyVwAnim {
      0% { transform: scaleY(0.35); }
      100% { transform: scaleY(1.3); }
    }

    /* Voice Recording Overlay Inside Input Bar - Negro Simple */
    .firby-voice-recording-overlay {
      flex: 1;
      min-width: 0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #09090b !important;
      border: 1px solid rgba(255, 255, 255, 0.14) !important;
      border-radius: 20px;
      padding: 7px 12px;
      gap: 8px;
      animation: firbyRecSlide 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes firbyRecSlide {
      from { opacity: 0; transform: scale(0.97); }
      to { opacity: 1; transform: scale(1); }
    }
    .firby-voice-rec-indicator {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 12.5px;
      font-weight: 600;
      color: #f4f4f5 !important;
      white-space: nowrap;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .firby-rec-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #ffffff !important;
      box-shadow: 0 0 6px rgba(255, 255, 255, 0.6);
      animation: firbyRecBlink 1s infinite ease-in-out;
    }
    @keyframes firbyRecBlink {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.25; transform: scale(0.75); }
    }
    .firby-voice-rec-waves {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 3px;
      height: 16px;
      overflow: hidden;
    }
    .firby-rec-bar {
      width: 2.5px;
      height: 6px;
      background: #a1a1aa !important;
      border-radius: 2px;
      animation: firbyRecWave 0.75s ease-in-out infinite alternate;
    }
    .firby-rec-bar.rb-1 { animation-delay: 0.05s; height: 6px; }
    .firby-rec-bar.rb-2 { animation-delay: 0.25s; height: 14px; }
    .firby-rec-bar.rb-3 { animation-delay: 0.45s; height: 10px; }
    .firby-rec-bar.rb-4 { animation-delay: 0.15s; height: 16px; }
    .firby-rec-bar.rb-5 { animation-delay: 0.35s; height: 8px; }
    .firby-rec-bar.rb-6 { animation-delay: 0.55s; height: 12px; }

    @keyframes firbyRecWave {
      0% { transform: scaleY(0.3); }
      100% { transform: scaleY(1.3); }
    }

    .firby-voice-cancel-btn {
      background: transparent;
      border: none;
      color: #71717a !important;
      cursor: pointer;
      padding: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background 0.15s, color 0.15s;
    }
    .firby-voice-cancel-btn:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: #ffffff !important;
    }

    /* Audio Player Bubble Inside Chat Stream */
    .firby-voice-player {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.04);
      border-radius: 16px;
      margin-top: 4px;
      min-width: 200px;
      user-select: none;
    }
    .firby-msg-user .firby-voice-player {
      background: rgba(255, 255, 255, 0.2);
      color: #ffffff;
    }
    .firby-vp-play-btn {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #09090b;
      color: #ffffff;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: transform 0.15s, background 0.15s;
    }
    .firby-msg-user .firby-vp-play-btn {
      background: #ffffff;
      color: #09090b;
    }
    .firby-vp-play-btn:hover {
      transform: scale(1.08);
    }
    .firby-vp-play-btn:active {
      transform: scale(0.92);
    }
    .firby-vp-track {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 2.5px;
      height: 20px;
      min-width: 90px;
    }
    .firby-vp-waveform {
      display: flex;
      align-items: center;
      gap: 2.5px;
      height: 18px;
      width: 100%;
    }
    .firby-vp-waveform span {
      flex: 1;
      min-width: 2px;
      background: currentColor;
      opacity: 0.4;
      border-radius: 1px;
      transition: opacity 0.15s, transform 0.15s;
    }
    .firby-vp-waveform span.played {
      opacity: 1;
    }
    .firby-vp-time {
      font-size: 11px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      opacity: 0.85;
      white-space: nowrap;
    }
    .firby-voice-note-transcript {
      font-size: 12.5px;
      line-height: 1.4;
      margin-top: 6px;
      opacity: 0.95;
      font-style: italic;
    }

    /* Input Action Buttons (Archivos, Emojis) */
    .firby-input-tool-btn {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: transparent;
      border: none;
      color: #71717a;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.16s cubic-bezier(0.16, 1, 0.3, 1);
      flex-shrink: 0;
      padding: 0;
      position: relative;
      outline: none;
    }
    .firby-input-tool-btn:hover {
      background: rgba(0, 0, 0, 0.05);
      color: #09090b;
      transform: scale(1.06);
    }
    .firby-input-tool-btn:active {
      transform: scale(0.94);
      background: rgba(0, 0, 0, 0.08);
    }
    .firby-input-tool-btn.has-attachment,
    .firby-input-tool-btn.active {
      color: #09090b;
      background: rgba(0, 0, 0, 0.08);
    }
    .firby-input-tool-btn svg {
      width: 17px;
      height: 17px;
      stroke-width: 2;
    }
    /* File Attachment Preview Bar */
    .firby-attachment-bar {
      display: none;
      align-items: center;
      padding: 7px 14px;
      background: #f4f4f5;
      border-top: 1px solid rgba(0, 0, 0, 0.06);
    }
    .firby-attachment-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #ffffff;
      border: 1px solid #e4e4e7;
      border-radius: 8px;
      padding: 4px 9px;
      font-size: 11.5px;
      color: #18181b;
      font-weight: 500;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
      max-width: 280px;
    }
    .firby-attachment-chip svg {
      color: #71717a;
      flex-shrink: 0;
    }
    .firby-attachment-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .firby-attachment-remove {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      border: none;
      color: #71717a;
      cursor: pointer;
      padding: 0;
      margin-left: 2px;
      border-radius: 4px;
      transition: color 0.15s, transform 0.15s;
    }
    .firby-attachment-remove:hover {
      color: #ef4444;
      transform: scale(1.15);
    }

    /* Attached File Badge inside message bubble */
    .firby-msg-file-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(0, 0, 0, 0.05);
      border: 1px solid rgba(0, 0, 0, 0.08);
      padding: 4px 8px;
      border-radius: 8px;
      font-size: 11.5px;
      font-weight: 500;
      margin-top: 5px;
      word-break: break-all;
    }
    .firby-msg-file-badge svg {
      flex-shrink: 0;
      color: #52525b;
    }

    /* ════════════════════════════════════════════════════════════════════════
       FIRBY SAAS PREMIUM DARK MODE SYSTEM — CHAT WIDGET
       Targeting strictly html.dark and html[data-theme="dark"]
       Light mode remains 100% untouched.
       ════════════════════════════════════════════════════════════════════════ */

    /* 1. Main Chat Window Container */
    html.dark .firby-chat-window,
    html[data-theme="dark"] .firby-chat-window {
      background: #101418 !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.8), 0 10px 24px -8px rgba(0, 0, 0, 0.6) !important;
    }

    /* 2. Chat Header — Tactile Executive Surface */
    html.dark .firby-chat-header,
    html[data-theme="dark"] .firby-chat-header {
      background: rgba(24, 28, 32, 0.94) !important;
      backdrop-filter: blur(16px) !important;
      -webkit-backdrop-filter: blur(16px) !important;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
      color: #E7E9EC !important;
    }
    html.dark .firby-header-title,
    html[data-theme="dark"] .firby-header-title {
      color: #E7E9EC !important;
      font-weight: 600 !important;
      letter-spacing: -0.015em !important;
    }
    html.dark .firby-title-default,
    html[data-theme="dark"] .firby-title-default {
      display: none !important;
    }
    html.dark .firby-title-dark,
    html[data-theme="dark"] .firby-title-dark {
      display: inline !important;
    }
    html.dark .firby-header-status,
    html[data-theme="dark"] .firby-header-status {
      display: flex !important;
      align-items: center;
      margin-top: 2px;
    }
    html.dark .firby-status-dot,
    html[data-theme="dark"] .firby-status-dot {
      display: none !important;
    }
    html.dark .firby-status-text,
    html[data-theme="dark"] .firby-status-text {
      font-size: 11.5px;
      color: #A7ADB5 !important;
      font-weight: 300 !important;
      line-height: 1;
      letter-spacing: -0.01em;
    }
    html.dark .firby-more-btn,
    html[data-theme="dark"] .firby-more-btn {
      background: rgba(255, 255, 255, 0.04) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      border-radius: 50% !important;
      width: 32px !important;
      height: 32px !important;
      color: #A7ADB5 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      transition: all 0.18s ease !important;
      cursor: pointer !important;
    }
    html.dark .firby-more-btn:hover,
    html[data-theme="dark"] .firby-more-btn:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: #E7E9EC !important;
      border-color: rgba(255, 255, 255, 0.15) !important;
      transform: scale(1.05) !important;
    }
    html.dark .firby-more-dropdown,
    html[data-theme="dark"] .firby-more-dropdown {
      background: #14191F !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
    }
    html.dark .firby-dropdown-item,
    html[data-theme="dark"] .firby-dropdown-item {
      color: #A7ADB5 !important;
    }
    html.dark .firby-dropdown-item:hover,
    html[data-theme="dark"] .firby-dropdown-item:hover {
      background: rgba(255, 255, 255, 0.06) !important;
      color: #FFFFFF !important;
    }
    html.dark .firby-close-btn,
    html[data-theme="dark"] .firby-close-btn {
      background: rgba(255, 255, 255, 0.04) !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      border-radius: 50% !important;
      width: 32px !important;
      height: 32px !important;
      color: #A7ADB5 !important;
      padding: 0 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      transition: all 0.18s ease !important;
    }
    html.dark .firby-close-btn:hover,
    html[data-theme="dark"] .firby-close-btn:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: #E7E9EC !important;
      border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* 3. Messages Stream Canvas */
    html.dark .firby-messages-stream,
    html[data-theme="dark"] .firby-messages-stream {
      background-color: #0B0F12 !important;
      background-image: radial-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px) !important;
      background-size: 18px 18px !important;
    }
    html.dark .firby-stream-time-badge,
    html[data-theme="dark"] .firby-stream-time-badge {
      color: #747B84 !important;
    }
    html.dark .firby-msg-author,
    html[data-theme="dark"] .firby-msg-author {
      color: #A7ADB5 !important;
    }
    html.dark .firby-msg-time,
    html[data-theme="dark"] .firby-msg-time {
      color: #747B84 !important;
    }

    /* 4. User Messages — Brand Lime Accent, Crisp Dark Text */
    html.dark .firby-msg-user,
    html[data-theme="dark"] .firby-msg-user {
      background: #C9F36A !important;
      color: #101410 !important;
      font-weight: 350 !important;
      border: 1px solid rgba(201, 243, 106, 0.4) !important;
      border-radius: 18px 18px 4px 18px !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
    }
    html.dark .firby-msg-user *,
    html[data-theme="dark"] .firby-msg-user * {
      color: #101410 !important;
    }

    /* 5. Assistant Messages & Policy Bubble — Subtle Elevated Dark Surface */
    html.dark .firby-msg-agent,
    html.dark .firby-policy-bubble,
    html[data-theme="dark"] .firby-msg-agent,
    html[data-theme="dark"] .firby-policy-bubble {
      background: #182026 !important;
      color: #DDE1E6 !important;
      font-weight: 300 !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      border-radius: 18px 18px 18px 4px !important;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.28) !important;
    }
    html.dark .firby-msg-agent strong,
    html[data-theme="dark"] .firby-msg-agent strong {
      color: #E7E9EC !important;
      font-weight: 550 !important;
    }
    html.dark .firby-msg-agent em,
    html[data-theme="dark"] .firby-msg-agent em {
      color: #A7ADB5 !important;
    }
    html.dark .firby-msg-agent a,
    html[data-theme="dark"] .firby-msg-agent a {
      color: #C9F36A !important;
    }
    html.dark .firby-policy-title,
    html[data-theme="dark"] .firby-policy-title {
      color: #E7E9EC !important;
      font-weight: 600 !important;
    }
    html.dark .firby-policy-text,
    html[data-theme="dark"] .firby-policy-text {
      color: #A7ADB5 !important;
      font-weight: 300 !important;
    }
    html.dark .firby-policy-link,
    html[data-theme="dark"] .firby-policy-link {
      color: #C9F36A !important;
    }
    html.dark .firby-policy-link:hover,
    html[data-theme="dark"] .firby-policy-link:hover {
      color: #d7fa85 !important;
    }
    html.dark .firby-consent-btn,
    html[data-theme="dark"] .firby-consent-btn {
      background: #C9F36A !important;
      color: #101410 !important;
      border: 1px solid rgba(201, 243, 106, 0.5) !important;
      border-radius: 20px !important;
      font-weight: 600 !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }
    html.dark .firby-consent-btn:hover,
    html[data-theme="dark"] .firby-consent-btn:hover {
      background: #bbf055 !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 4px 12px rgba(201, 243, 106, 0.25) !important;
    }

    /* 6. Structured Lists & Bullets */
    html.dark .firby-bullet-item,
    html[data-theme="dark"] .firby-bullet-item {
      display: flex !important;
      align-items: flex-start !important;
      gap: 9px !important;
      margin: 6px 0 !important;
      line-height: 1.5 !important;
      color: #DDE1E6 !important;
    }
    html.dark .firby-bullet-dot,
    html[data-theme="dark"] .firby-bullet-dot {
      width: 5px !important;
      height: 5px !important;
      border-radius: 50% !important;
      background-color: #C9F36A !important;
      flex-shrink: 0 !important;
      margin-top: 7px !important;
      box-shadow: 0 0 4px rgba(201, 243, 106, 0.4) !important;
    }

    /* 7. Suggestions Dock & Quick Action Chips */
    html.dark .firby-suggestions-dock,
    html[data-theme="dark"] .firby-suggestions-dock {
      background: #101418 !important;
      border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    html.dark .firby-chip,
    html[data-theme="dark"] .firby-chip {
      background: #182026 !important;
      border: 1px solid rgba(255, 255, 255, 0.09) !important;
      color: #A7ADB5 !important;
      border-radius: 18px !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
      transition: all 0.16s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    html.dark .firby-chip:hover,
    html[data-theme="dark"] .firby-chip:hover {
      background: #202830 !important;
      border-color: rgba(201, 243, 106, 0.3) !important;
      color: #E7E9EC !important;
      transform: translateY(-1px) !important;
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.4) !important;
    }
    html.dark .firby-chip:active,
    html[data-theme="dark"] .firby-chip:active {
      transform: scale(0.97) !important;
      background: #182026 !important;
    }

    /* 8. Composer Bar & Input Controls */
    html.dark .firby-input-bar,
    html[data-theme="dark"] .firby-input-bar {
      background: rgba(19, 23, 27, 0.96) !important;
      border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    html.dark .firby-input-field,
    html[data-theme="dark"] .firby-input-field {
      background: #171C21 !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      color: #E7E9EC !important;
      border-radius: 20px !important;
      font-weight: 300 !important;
      letter-spacing: -0.01em !important;
    }
    html.dark .firby-input-field::placeholder,
    html[data-theme="dark"] .firby-input-field::placeholder {
      color: #7D848D !important;
      font-weight: 300 !important;
    }
    html.dark .firby-input-field:focus,
    html[data-theme="dark"] .firby-input-field:focus {
      background: #1c2229 !important;
      border-color: rgba(201, 243, 106, 0.45) !important;
      box-shadow: 0 0 0 2px rgba(201, 243, 106, 0.08) !important;
    }
    html.dark .firby-input-tool-btn,
    html[data-theme="dark"] .firby-input-tool-btn {
      color: #747B84 !important;
      background: transparent !important;
    }
    html.dark .firby-input-tool-btn:hover,
    html[data-theme="dark"] .firby-input-tool-btn:hover {
      color: #A7ADB5 !important;
      background: rgba(255, 255, 255, 0.06) !important;
    }
    html.dark .firby-input-tool-btn.has-attachment,
    html.dark .firby-input-tool-btn.active,
    html[data-theme="dark"] .firby-input-tool-btn.has-attachment,
    html[data-theme="dark"] .firby-input-tool-btn.active {
      background: rgba(201, 243, 106, 0.12) !important;
      color: #C9F36A !important;
    }
    html.dark .firby-voice-btn,
    html[data-theme="dark"] .firby-voice-btn {
      background: transparent !important;
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      color: #747B84 !important;
      border-radius: 50% !important;
    }
    html.dark .firby-voice-btn:hover,
    html[data-theme="dark"] .firby-voice-btn:hover {
      background: rgba(255, 255, 255, 0.06) !important;
      color: #A7ADB5 !important;
      border-color: rgba(255, 255, 255, 0.12) !important;
    }
    html.dark .firby-send-btn,
    html[data-theme="dark"] .firby-send-btn {
      background: #C9F36A !important;
      color: #101410 !important;
      border: none !important;
      border-radius: 50% !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
    }
    html.dark .firby-send-btn svg,
    html[data-theme="dark"] .firby-send-btn:not(.firby-flow-mode) svg {
      color: #101410 !important;
      stroke: #101410 !important;
    }
    html.dark .firby-send-btn:hover,
    html[data-theme="dark"] .firby-send-btn:hover {
      background: #bbf055 !important;
      transform: scale(1.04) !important;
    }
    html.dark .firby-send-btn.firby-flow-mode,
    html[data-theme="dark"] .firby-send-btn.firby-flow-mode {
      background: #181c20 !important;
      color: #b9fa01 !important;
      border: 1px solid rgba(185, 250, 1, 0.4) !important;
      box-shadow: 0 0 16px rgba(185, 250, 1, 0.25) !important;
    }
    html.dark .firby-send-btn.firby-flow-mode:hover,
    html[data-theme="dark"] .firby-send-btn.firby-flow-mode:hover {
      background: #242930 !important;
      box-shadow: 0 0 22px rgba(185, 250, 1, 0.45) !important;
      transform: scale(1.06) !important;
    }
    html.dark .firby-send-btn.firby-flow-mode .firby-flow-icon,
    html[data-theme="dark"] .firby-send-btn.firby-flow-mode .firby-flow-icon {
      color: #b9fa01 !important;
      stroke: #b9fa01 !important;
    }

    /* 9. Attachment Bar & Voice Overlay */
    html.dark .firby-attachment-bar,
    html[data-theme="dark"] .firby-attachment-bar {
      background: #171C21 !important;
      border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    html.dark .firby-attachment-chip,
    html[data-theme="dark"] .firby-attachment-chip {
      background: #182026 !important;
      border: 1px solid rgba(255, 255, 255, 0.09) !important;
      color: #DDE1E6 !important;
    }
    html.dark .firby-voice-btn.recording,
    html[data-theme="dark"] .firby-voice-btn.recording {
      background: #09090b !important;
      color: #ffffff !important;
      border-color: rgba(255, 255, 255, 0.25) !important;
    }
    html.dark .firby-voice-recording-overlay,
    html[data-theme="dark"] .firby-voice-recording-overlay {
      background: #09090b !important;
      border-color: rgba(255, 255, 255, 0.14) !important;
    }
    html.dark .firby-voice-rec-indicator,
    html[data-theme="dark"] .firby-voice-rec-indicator {
      color: #f4f4f5 !important;
    }
    html.dark .firby-voice-cancel-btn,
    html[data-theme="dark"] .firby-voice-cancel-btn {
      color: #71717a !important;
    }
    html.dark .firby-voice-cancel-btn:hover,
    html[data-theme="dark"] .firby-voice-cancel-btn:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: #ffffff !important;
    }
    html.dark .firby-voice-player,
    html[data-theme="dark"] .firby-voice-player {
      background: rgba(255, 255, 255, 0.08) !important;
    }

    /* 10. Thinking State, Action Cards & Launcher Items */
    html.dark .firby-thinking-badge,
    html[data-theme="dark"] .firby-thinking-badge {
      background: #182026 !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
      color: #f4f4f5 !important;
    }
    html.dark .firby-google-btn,
    html[data-theme="dark"] .firby-google-btn,
    html.dark .firby-action-btn,
    html[data-theme="dark"] .firby-action-btn {
      background: #182026 !important;
      color: #E7E9EC !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    html.dark .bws-hw-item,
    html[data-theme="dark"] .bws-hw-item {
      background: #182026 !important;
      border: 1.5px solid rgba(255, 255, 255, 0.14) !important;
      color: #E7E9EC !important;
      box-shadow: 0 10px 28px -4px rgba(0, 0, 0, 0.6) !important;
    }
    html.dark .bws-hw-item:hover,
    html[data-theme="dark"] .bws-hw-item:hover {
      background: #24303a !important;
      border-color: rgba(255, 255, 255, 0.25) !important;
    }
    html.dark .bws-hw-item > img:not([alt="WhatsApp"]),
    html[data-theme="dark"] .bws-hw-item > img:not([alt="WhatsApp"]) {
      filter: brightness(0) invert(1) !important;
    }
    html.dark .bws-hw-item > svg,
    html[data-theme="dark"] .bws-hw-item > svg {
      color: #E7E9EC !important;
    }
    html.dark .bws-hw-item .bws-hw-text,
    html[data-theme="dark"] .bws-hw-item .bws-hw-text {
      background: #182026 !important;
      color: #E7E9EC !important;
      border: 1px solid rgba(255, 255, 255, 0.14) !important;
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5) !important;
    }
    html.dark .bws-hw-item:hover .bws-hw-text,
    html[data-theme="dark"] .bws-hw-item:hover .bws-hw-text {
      background: #24303a !important;
      color: #FFFFFF !important;
    }
    html.dark .bws-hw-floating-btn,
    html[data-theme="dark"] .bws-hw-floating-btn {
      background: #182026 !important;
      border: 1px solid rgba(255, 255, 255, 0.14) !important;
      box-shadow: 0 12px 32px -4px rgba(0, 0, 0, 0.6) !important;
    }
    html.dark .firby-btn-question-icon svg,
    html[data-theme="dark"] .firby-btn-question-icon svg {
      stroke: #E7E9EC !important;
    }
    html.dark .firby-btn-close-icon svg path,
    html[data-theme="dark"] .firby-btn-close-icon svg path {
      fill: #ffffff !important;
    }
    html.dark .firby-btn-chat-icon,
    html[data-theme="dark"] .firby-btn-chat-icon {
      color: #b9fa01 !important;
    }
    html.dark .firby-btn-chat-icon svg path,
    html[data-theme="dark"] .firby-btn-chat-icon svg path {
      fill: #b9fa01 !important;
    }
    html.dark .firby-chat-activity-bar.active,
    html[data-theme="dark"] .firby-chat-activity-bar.active {
      background: rgba(201, 243, 106, 0.06) !important;
      border-bottom-color: rgba(201, 243, 106, 0.15) !important;
    }
    html.dark .firby-activity-dot,
    html[data-theme="dark"] .firby-activity-dot {
      background: #C9F36A !important;
    }
    html.dark .firby-activity-brand,
    html[data-theme="dark"] .firby-activity-brand {
      color: #E7E9EC !important;
    }
    html.dark .firby-activity-text,
    html[data-theme="dark"] .firby-activity-text {
      color: #A7ADB5 !important;
    }
    html.dark .firby-activity-divider,
    html[data-theme="dark"] .firby-activity-divider {
      background: rgba(255, 255, 255, 0.14) !important;
    }
    html.dark .firby-activity-cancel,
    html[data-theme="dark"] .firby-activity-cancel {
      color: #A7ADB5 !important;
    }
    html.dark .firby-activity-cancel:hover,
    html[data-theme="dark"] .firby-activity-cancel:hover {
      background: rgba(255, 255, 255, 0.1) !important;
      color: #ffffff !important;
    }
    html.dark .firby-scroll-bottom-pill,
    html[data-theme="dark"] .firby-scroll-bottom-pill {
      background: rgba(24, 32, 38, 0.92) !important;
      border-color: rgba(255, 255, 255, 0.15) !important;
      color: #E7E9EC !important;
    }

    /* ═══ MOBILE RESPONSIVE SAAS PREMIUM ═══ */
    @media (max-width: 768px) {
      .firby-widget-container,
      .bws-hw {
        bottom: max(92px, env(safe-area-inset-bottom, 92px));
        right: 14px !important;
        left: auto !important;
      }
      .bws-hw-floating-btn,
      .firby-launcher-btn,
      .bws-hw-item {
        width: 56px;
        height: 56px;
      }
      .bws-hw-floating-btn .bws-hw-icon img,
      .firby-launcher-btn .bws-hw-icon img {
        width: 26px;
        max-width: 26px;
      }
      .bws-hw-item > img {
        width: 24px;
        max-width: 24px;
      }
      .bws-hw-item .bws-hw-text {
        right: 66px;
        font-size: 13px;
        padding: 6px 13px;
      }
      .bws-hw.bws-hw-active .bws-hw-item:nth-child(1) {
        transform: translate3d(0, -350px, 0);
      }
      .bws-hw.bws-hw-active .bws-hw-item:nth-child(2) {
        transform: translate3d(0, -280px, 0);
      }
      .bws-hw.bws-hw-active .bws-hw-item:nth-child(3) {
        transform: translate3d(0, -210px, 0);
      }
      .bws-hw.bws-hw-active .bws-hw-item:nth-child(4) {
        transform: translate3d(0, -140px, 0);
      }
      .bws-hw.bws-hw-active .bws-hw-item:nth-child(5) {
        transform: translate3d(0, -70px, 0);
      }
      .bws-hw.bws-hw-active .bws-hw-item {
        z-index: 100 !important;
      }
      .bws-hw.bws-hw-active .bws-hw-item .bws-hw-text {
        z-index: 101 !important;
      }
      .firby-teaser-pill {
        display: none !important;
      }

      /* Cuando el chat está abierto en móvil, se oculta el launcher flotante para evitar colisión con el input y botón enviar */
      .bws-hw.chat-open .bws-hw-floating-btn {
        display: none !important;
      }
      .bws-hw.chat-open .bws-hw-menu {
        display: none !important;
      }

      /* Mobile Chat Window: Floating Sheet taking nearly full useful space */
      .firby-chat-window {
        position: fixed !important;
        top: max(10px, env(safe-area-inset-top, 10px)) !important;
        bottom: max(12px, env(safe-area-inset-bottom, 12px)) !important;
        left: 8px !important;
        right: 8px !important;
        width: auto !important;
        max-width: calc(100vw - 16px) !important;
        height: auto !important;
        max-height: none !important;
        border-radius: 24px !important;
        transform-origin: bottom center !important;
        transform: translateY(28px) scale(0.96);
        filter: blur(6px);
        opacity: 0;
        pointer-events: none;
        contain: none !important;
        visibility: hidden;
      }
      .firby-chat-window.open {
        opacity: 1 !important;
        pointer-events: auto !important;
        transform: translateY(0) scale(1) !important;
        filter: blur(0px) !important;
        z-index: 10000000 !important;
        display: flex !important;
        visibility: visible !important;
      }

      .firby-mobile-drag-handle {
        display: flex !important;
        align-items: center;
        justify-content: center;
        padding: 8px 0 2px 0;
        width: 100%;
        cursor: grab;
        touch-action: none;
        background: transparent;
      }
      .firby-drag-pill {
        width: 36px;
        height: 4.5px;
        border-radius: 9999px;
        background: rgba(0, 0, 0, 0.16);
      }
      html.dark .firby-drag-pill,
      html[data-theme="dark"] .firby-drag-pill {
        background: rgba(255, 255, 255, 0.22);
      }

      .firby-chat-header {
        padding: 8px 16px 10px 16px;
      }
      .firby-messages-stream {
        padding: 12px 14px;
        gap: 10px;
      }
      .firby-msg {
        font-size: 14px;
        line-height: 1.52;
        padding: 10px 14px;
        max-width: 88%;
        font-weight: 300;
        letter-spacing: -0.012em;
      }
      .firby-input-bar {
        padding: 8px 12px;
        padding-bottom: max(10px, env(safe-area-inset-bottom, 10px));
      }
      .firby-input-field {
        font-size: 15px !important; /* Evita zoom forzado en Safari iOS */
        padding: 10px 15px;
        font-weight: 300;
        letter-spacing: -0.01em;
      }
      .firby-send-btn,
      .firby-voice-btn {
        width: 40px;
        height: 40px;
      }
      .firby-chip {
        font-size: 12px;
        padding: 6px 12px;
      }
    }
  `;
  document.head.appendChild(styleEl);

  // Initial Content & Dynamic Timestamp (Wompi Style)
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  const formattedTime = `${hours}:${minutes} ${ampm}`;

  const initialChips = isLanding
    ? [
        'Cómo funciona Firby',
        'Ver planes y precios',
        'Cómo se instala',
        'Crear mi cuenta'
      ]
    : [
        'Agendar una cita',
        'Horarios de atención',
        'Servicios disponibles',
        'Hablar con un asesor'
      ];



  // DOM Container (bws-help-widget Wompi System)
  const container = document.createElement('div');
  container.className = 'firby-widget-container bws-hw' + (isChatOnlyLauncher ? ' bws-hw-chat-only' : '');
  container.id = 'bws-help-widget';
  container.innerHTML = `
    <!-- Chat Window -->
    <div class="firby-chat-window" id="firby-chat-window">
      <!-- Mobile Drag Handle -->
      <div class="firby-mobile-drag-handle" id="firby-mobile-drag-handle" aria-hidden="true">
        <span class="firby-drag-pill"></span>
      </div>

      <div class="firby-chat-header">
        <div class="firby-header-profile">
          <div class="firby-header-avatar-wrap">
            ${getFirbyAvatarHtml(true)}
          </div>
          <div>
            <h4 class="firby-header-title">${OPERATOR_TITLE}</h4>
            <div class="firby-header-status"><span class="firby-status-text">Asistente virtual</span></div>
          </div>
        </div>
        <div class="firby-header-actions">
          <div class="firby-header-menu-wrap" style="position: relative;">
            <button type="button" class="firby-more-btn" id="firby-more-btn" aria-label="Más opciones" title="Opciones">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <circle cx="12" cy="5" r="1.75"></circle>
                <circle cx="12" cy="12" r="1.75"></circle>
                <circle cx="12" cy="19" r="1.75"></circle>
              </svg>
            </button>
            <div class="firby-more-dropdown" id="firby-more-dropdown">
              <button type="button" class="firby-dropdown-item" id="firby-reset-chat-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                  <path d="M21 3v5h-5"></path>
                  <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                  <path d="M8 16H3v5"></path>
                </svg>
                <span>Nueva conversación</span>
              </button>
            </div>
          </div>
          <button class="firby-close-btn" id="firby-close-btn" aria-label="Cerrar chat">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Integrated Agent Surface Activity Bar (Dentro del Chat) -->
      <div class="firby-chat-activity-bar" id="firby-chat-activity-bar" aria-live="polite">
        <div class="firby-activity-inner">
          <div class="firby-activity-presence">
            <span class="firby-activity-dot" aria-hidden="true"></span>
            <span class="firby-activity-brand">Firby</span>
          </div>
          <div class="firby-activity-divider" aria-hidden="true"></div>
          <span class="firby-activity-text" id="firby-activity-text"></span>
          <button type="button" class="firby-activity-cancel" id="firby-activity-cancel" aria-label="Detener acción" title="Detener">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <div class="firby-messages-stream" id="firby-messages-stream">
        <div class="firby-stream-time-badge">${formattedTime}</div>
        <div class="firby-msg-row firby-msg-row-agent" id="firby-initial-policy-row">
          <div class="firby-msg-avatar-wrap">
            ${getFirbyAvatarHtml(false)}
          </div>
          <div class="firby-msg-content-wrap">
            <div class="firby-msg-author">Firby</div>
            <div class="firby-msg firby-msg-agent firby-policy-bubble">
              <div class="firby-policy-title">Aceptas términos y condiciones</div>
              <div class="firby-policy-text">Para continuar y brindarte atención personalizada, acepta nuestros términos y condiciones y política de tratamiento de datos.</div>
              <div class="firby-policy-link-row">
                <a href="/terms" target="_blank" rel="noopener noreferrer" class="firby-policy-link">Términos y condiciones</a> · 
                <a href="/privacidad" target="_blank" rel="noopener noreferrer" class="firby-policy-link">Política de privacidad</a>
              </div>
            </div>
            <div class="firby-consent-container" id="firby-consent-container">
              <button type="button" class="firby-consent-btn" id="firby-consent-btn">
                Sí, acepto
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Scroll-to-Bottom Pill for New Messages -->
      <button type="button" class="firby-scroll-bottom-pill" id="firby-scroll-bottom-pill" aria-label="Ver nuevos mensajes">
        <span>Nuevos mensajes</span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"></polyline></svg>
      </button>

      <!-- DOCK DE SUGERENCIAS HORIZONTAL JUSTO ARRIBA DEL INPUT -->
      <div class="firby-suggestions-dock" id="firby-suggestions-dock"></div>

      <!-- Barra de Vista Previa de Archivo Adjunto -->
      <div class="firby-attachment-bar" id="firby-attachment-bar">
        <div class="firby-attachment-chip">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <span class="firby-attachment-name" id="firby-attachment-name"></span>
          <button type="button" class="firby-attachment-remove" id="firby-attachment-remove" title="Quitar archivo" aria-label="Quitar archivo">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <form class="firby-input-bar" id="firby-input-form">
        <!-- Input de archivo oculto -->
        <input type="file" id="firby-file-input" style="display:none;" accept="image/*,.pdf,.doc,.docx,.txt" />

        <!-- Botón Adjuntar Archivo -->
        <button type="button" class="firby-input-tool-btn firby-attach-btn" id="firby-attach-btn" title="Adjuntar archivo" aria-label="Adjuntar archivo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
          </svg>
        </button>

        <!-- Dynamic Recording Bar Overlay (when recording voice) -->
        <div class="firby-voice-recording-overlay" id="firby-voice-recording-overlay" style="display: none;">
          <div class="firby-voice-rec-indicator">
            <span class="firby-rec-dot"></span>
            <span class="firby-rec-time" id="firby-rec-timer">0:00</span>
          </div>
          <div class="firby-voice-rec-waves">
            <span class="firby-rec-bar rb-1"></span>
            <span class="firby-rec-bar rb-2"></span>
            <span class="firby-rec-bar rb-3"></span>
            <span class="firby-rec-bar rb-4"></span>
            <span class="firby-rec-bar rb-5"></span>
            <span class="firby-rec-bar rb-6"></span>
          </div>
          <button type="button" class="firby-voice-cancel-btn" id="firby-voice-cancel-btn" title="Descartar grabación" aria-label="Descartar grabación">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <!-- Input de texto -->
        <input type="text" class="firby-input-field" id="firby-input" placeholder="Escribe un mensaje..." autocomplete="off" />

        <!-- Botón Enviar Audio (al lado de enviar) -->
        <button type="button" class="firby-voice-btn" id="firby-voice-btn" title="Grabar mensaje de voz" aria-label="Grabar mensaje de voz">
          <div class="firby-voice-btn-icon" id="firby-voice-btn-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="22"></line>
            </svg>
          </div>
          <div class="firby-voice-active-waves" id="firby-voice-active-waves" style="display: none;">
            <span class="firby-vw-bar vw-1"></span>
            <span class="firby-vw-bar vw-2"></span>
            <span class="firby-vw-bar vw-3"></span>
          </div>
        </button>

        <!-- Botón Enviar / Modo Live Voz Flow Premium -->
        <button type="button" class="firby-send-btn firby-flow-mode" id="firby-send" aria-label="Modo voz en vivo (1 a 1)" title="Modo voz en vivo (1 a 1)">
          <!-- Icono Flow Premium (ChatGPT Voice Mode / Gemini Live Waveform) -->
          <svg class="firby-flow-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round">
            <line x1="4" y1="10" x2="4" y2="14"></line>
            <line x1="9" y1="6" x2="9" y2="18"></line>
            <line x1="14" y1="3" x2="14" y2="21"></line>
            <line x1="19" y1="8" x2="19" y2="16"></line>
          </svg>
          <!-- Icono Enviar Normal -->
          <svg class="firby-send-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>

      <!-- Live Voice 1-to-1 Mode Overlay (ChatGPT / Gemini Live Experience) -->
      <div class="firby-live-voice-overlay" id="firby-live-voice-overlay" style="display: none;">
        <div class="firby-lvo-header">
          <button type="button" class="firby-lvo-close-btn" id="firby-lvo-close-btn" aria-label="Finalizar llamada de voz" title="Salir de modo voz">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div class="firby-lvo-body">
          <div class="firby-lvo-orb-wrapper">
            <div class="firby-lvo-orb" id="firby-lvo-orb">
              <picture class="firby-lvo-avatar-pic">
                <source srcset="/assets/eyes.webp?v=20261009_eyes_v2" type="image/webp">
                <img src="/assets/eyes.webp?v=20261009_eyes_v2" alt="Firby" class="firby-lvo-avatar-img" />
              </picture>
            </div>
          </div>

          <!-- Dynamic Audio-Reactive Canvas Visualizer (Live Microphone AnalyserNode) -->
          <div class="firby-lvo-canvas-container">
            <canvas id="firby-lvo-canvas" class="firby-lvo-canvas" width="320" height="65"></canvas>
          </div>

          <div class="firby-lvo-status-text" id="firby-lvo-status-text">Te escucho. Habla con naturalidad...</div>
          <button type="button" class="firby-lvo-perm-btn" id="firby-lvo-perm-btn" style="display: none;">
            Permitir micrófono
          </button>
          <div class="firby-lvo-transcript-box" id="firby-lvo-transcript-box">
            <div class="firby-lvo-transcript-user" id="firby-lvo-user-text"></div>
            <div class="firby-lvo-transcript-agent" id="firby-lvo-agent-text"></div>
          </div>
        </div>

        <div class="firby-lvo-footer">
          <button type="button" class="firby-lvo-end-pill" id="firby-lvo-end-btn" title="Finalizar llamada">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
              <rect x="5" y="5" width="14" height="14" rx="2"></rect>
            </svg>
            <span>Finalizar</span>
          </button>
        </div>
      </div>


    </div>

    ${isChatOnlyLauncher ? '' : `
    <!-- Menu de opciones flotantes idéntico a Wompi -->
    <menu class="bws-hw-menu" id="bws-hw-menu">
      <a class="bws-hw-item" href="javascript:;" id="waiChatLauncher" role="button" aria-haspopup="dialog" aria-label="Chatea con Firby">
        <img src="/assets/chat/chat-desktop.svg" alt="Chatea con Firby" />
        <span class="bws-hw-text">Chatea con Firby</span>
      </a>
      <a class="bws-hw-item" href="/about-us" id="aboutLauncher" aria-label="Sobre nosotros">
        <img src="/assets/chat/icon-nosotros.svg" alt="Sobre nosotros" />
        <span class="bws-hw-text">Sobre nosotros</span>
      </a>
      <a class="bws-hw-item" href="/faq" id="faqLauncher" aria-label="Preguntas frecuentes">
        <img src="/assets/chat/icon-preguntas.svg" alt="Preguntas frecuentes" />
        <span class="bws-hw-text">Preguntas frecuentes</span>
      </a>
      <a class="bws-hw-item" href="mailto:contacto@firbyai.com" aria-label="Escríbenos">
        <img src="/assets/chat/icon-escribenos.svg" alt="Escríbenos" />
        <span class="bws-hw-text">Escríbenos</span>
      </a>
      <a class="bws-hw-item bws-hw-whatsapp" href="https://api.whatsapp.com/send/?phone=573243699856&text=Hola%20Firby" target="_blank" rel="noopener noreferrer" id="whatsappLauncher" aria-label="WhatsApp">
        <img src="/assets/chat/icon-whatsapp.svg" alt="WhatsApp" />
        <span class="bws-hw-text">WhatsApp</span>
      </a>
    </menu>
    `}

    <!-- Floating Launcher Button: Icono Chatea con Firby o Pregunta '?' -->
    <a class="bws-hw-floating-btn firby-launcher-btn" id="bws-hw-btn" href="javascript:;" role="button" aria-label="${isChatOnlyLauncher ? 'Chatea con Firby' : 'Atención y Asesoría'}" title="${isChatOnlyLauncher ? 'Chatea con Firby' : 'Atención y Preguntas'}">
      ${isChatOnlyLauncher ? `
      <div class="firby-btn-icon firby-btn-chat-icon">
        <svg width="29" height="24" viewBox="0 0 36 29" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M18 3.75C18 2.78575 18.7857 2 19.75 2H32C32.9643 2 33.75 2.78575 33.75 3.75V7.25C33.75 8.21425 32.9643 9 32 9H25.5128L23.25 11.2628V9H19.75C18.7857 9 18 8.21425 18 7.25V3.75ZM21.5 10.75V15.4873L26.2372 10.75H32C33.9303 10.75 35.5 9.18025 35.5 7.25V3.75C35.5 1.81975 33.9303 0.25 32 0.25H19.75C17.8197 0.25 16.25 1.81975 16.25 3.75V7.25C16.25 9.18025 17.8197 10.75 19.75 10.75H21.5Z" fill="currentColor"/>
          <path d="M22.375 5.5C22.375 5.98325 21.9832 6.375 21.5 6.375C21.0168 6.375 20.625 5.98325 20.625 5.5C20.625 5.01675 21.0168 4.625 21.5 4.625C21.9832 4.625 22.375 5.01675 22.375 5.5Z" fill="currentColor"/>
          <path d="M26.75 5.5C26.75 5.98325 26.3582 6.375 25.875 6.375C25.3918 6.375 25 5.98325 25 5.5C25 5.01675 25.3918 4.625 25.875 4.625C26.3582 4.625 26.75 5.01675 26.75 5.5Z" fill="currentColor"/>
          <path d="M31.125 5.5C31.125 5.98325 30.7332 6.375 30.25 6.375C29.7668 6.375 29.375 5.98325 29.375 5.5C29.375 5.01675 29.7668 4.625 30.25 4.625C30.7332 4.625 31.125 5.01675 31.125 5.5Z" fill="currentColor"/>
          <path fill-rule="evenodd" clip-rule="evenodd" d="M14.5 3.75H7.5C5.56975 3.75 4 5.31975 4 7.25V23H0.5V24.75C0.5 26.6803 2.06975 28.25 4 28.25H32C33.9303 28.25 35.5 26.6803 35.5 24.75V23H32V12.5H30.25V23H5.75V7.25C5.75 6.28575 6.534 5.5 7.5 5.5H14.5V3.75ZM2.25 24.75C2.25 25.7142 3.034 26.5 4 26.5H32C32.966 26.5 33.75 25.7142 33.75 24.75H2.25Z" fill="currentColor"/>
        </svg>
      </div>
      ` : `
      <div class="firby-btn-icon firby-btn-question-icon">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#2C2A29" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      </div>
      `}
      <div class="firby-btn-icon firby-btn-close-icon">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0.991666 23.2333L0 22.2417L10.625 11.6167L0 0.991666L0.991666 0L11.6167 10.625L22.2417 0L23.2333 0.991666L12.6083 11.6167L23.2333 22.2417L22.2417 23.2333L11.6167 12.6083L0.991666 23.2333Z" fill="currentColor"/>
        </svg>
      </div>
    </a>
    <button id="firby-launcher-btn" style="display:none;" aria-hidden="true"></button>
  `;
  document.body.appendChild(container);

  // Marco perimetral vivo de pantalla completa (Estilo Comet / Gemini Live)
  let livePageBorder = document.getElementById('firby-live-page-border');
  if (!livePageBorder) {
    livePageBorder = document.createElement('div');
    livePageBorder.id = 'firby-live-page-border';
    livePageBorder.className = 'firby-live-page-border';
    livePageBorder.setAttribute('aria-hidden', 'true');
    livePageBorder.innerHTML = `
      <div class="firby-live-page-border-glow"></div>
      <div class="firby-live-page-border-line"></div>
    `;
    document.body.appendChild(livePageBorder);
  }

  // Live Dark Theme Observer for Launcher Button
  const updateWidgetTheme = () => {
    try {
      const isDark = document.documentElement.classList.contains('dark') ||
                     document.documentElement.getAttribute('data-theme') === 'dark' ||
                     (document.body && document.body.classList.contains('dark')) ||
                     (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (isDark) {
        container.classList.add('firby-dark-mode');
      } else {
        container.classList.remove('firby-dark-mode');
      }
    } catch (e) {}
  };
  updateWidgetTheme();
  try {
    const themeObserver = new MutationObserver(updateWidgetTheme);
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    if (document.body) {
      themeObserver.observe(document.body, { attributes: true, attributeFilter: ['class', 'data-theme'] });
    }
  } catch (e) {}

  // References
  const windowEl = document.getElementById('firby-chat-window');
  const launcherBtn = document.getElementById('bws-hw-btn');
  const proxyLauncherBtn = document.getElementById('firby-launcher-btn');
  const bwsHW = container;
  const chatLauncher = document.getElementById('waiChatLauncher');
  const aboutLauncher = document.getElementById('aboutLauncher');
  const faqLauncher = document.getElementById('faqLauncher');
  const closeBtn = document.getElementById('firby-close-btn');
  const moreBtn = document.getElementById('firby-more-btn');
  const moreDropdown = document.getElementById('firby-more-dropdown');
  const resetChatBtn = document.getElementById('firby-reset-chat-btn');
  const teaserPill = document.getElementById('firby-teaser-pill');
  const liveVoiceOverlay = document.getElementById('firby-live-voice-overlay');
  const lvoCloseBtn = document.getElementById('firby-lvo-close-btn');
  const lvoOrb = document.getElementById('firby-lvo-orb');
  const lvoStatusText = document.getElementById('firby-lvo-status-text');
  const lvoUserText = document.getElementById('firby-lvo-user-text');
  const lvoAgentText = document.getElementById('firby-lvo-agent-text');
  const lvoMicToggle = document.getElementById('firby-lvo-mic-toggle');
  const lvoEndBtn = document.getElementById('firby-lvo-end-btn');
  const lvoPermBtn = document.getElementById('firby-lvo-perm-btn');
  const streamEl = document.getElementById('firby-messages-stream');
  if (streamEl) streamEl.setAttribute('data-lenis-prevent', 'true');
  if (bwsHW) bwsHW.setAttribute('data-lenis-prevent', 'true');
  const suggestionsDock = document.getElementById('firby-suggestions-dock');
  const inputForm = document.getElementById('firby-input-form');
  const inputEl = document.getElementById('firby-input');
  const sendBtn = document.getElementById('firby-send');
  const consentContainer = document.getElementById('firby-consent-container');
  const consentBtn = document.getElementById('firby-consent-btn');

  // References: Attachments & Emojis
  const attachBtn = document.getElementById('firby-attach-btn');
  const fileInput = document.getElementById('firby-file-input');
  const attachmentBar = document.getElementById('firby-attachment-bar');
  const attachmentName = document.getElementById('firby-attachment-name');
  const attachmentRemoveBtn = document.getElementById('firby-attachment-remove');

  // References: Audio / Voice Recording
  const voiceBtn = document.getElementById('firby-voice-btn');
  const voiceBtnIcon = document.getElementById('firby-voice-btn-icon');
  const voiceActiveWaves = document.getElementById('firby-voice-active-waves');
  const voiceRecordingOverlay = document.getElementById('firby-voice-recording-overlay');
  const voiceRecTimer = document.getElementById('firby-rec-timer');
  const voiceCancelBtn = document.getElementById('firby-voice-cancel-btn');

  // References: Integrated Agent Surface, Mobile Drag & Smart Scroll Pill
  const activityBar = document.getElementById('firby-chat-activity-bar');
  const activityText = document.getElementById('firby-activity-text');
  const activityCancelBtn = document.getElementById('firby-activity-cancel');
  const scrollBottomPill = document.getElementById('firby-scroll-bottom-pill');
  const dragHandle = document.getElementById('firby-mobile-drag-handle');

  let isOpen = false;

  function openChat() {
    bwsHW.classList.remove('bws-hw-active');
    bwsHW.classList.add('chat-open');
    windowEl.classList.add('open');
    launcherBtn.classList.add('is-open');
    if (teaserPill) teaserPill.classList.add('hide');
    isOpen = true;
    if (window.FirbyAgentSurface && typeof window.FirbyAgentSurface.hide === 'function') {
      window.FirbyAgentSurface.hide();
    }
    syncMobileViewport();
    setTimeout(() => { if (inputEl) inputEl.focus(); }, 150);
  }

  function closeChat() {
    if (isLiveVoiceActive) {
      closeLiveVoiceMode();
    }
    windowEl.classList.remove('open');
    launcherBtn.classList.remove('is-open');
    bwsHW.classList.remove('chat-open');
    bwsHW.classList.remove('bws-hw-active');
    isOpen = false;
    closeEmojiPopover();
    if (moreDropdown) moreDropdown.classList.remove('show');
    resetMobileViewportStyles();
    try {
      if (typeof sessionStorage !== 'undefined') {
        sessionStorage.removeItem('firby_keep_open');
      }
    } catch (e) {}
  }

  function toggleMenu() {
    if (isOpen) {
      closeChat();
    } else {
      bwsHW.classList.toggle('bws-hw-active');
    }
  }

  function toggleChat() {
    if (isOpen) {
      closeChat();
    } else {
      openChat();
    }
  }

  launcherBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    if (isChatOnlyLauncher) {
      toggleChat();
    } else {
      toggleMenu();
    }
  });

  if (proxyLauncherBtn) {
    proxyLauncherBtn.addEventListener('click', function(e) {
      e.preventDefault();
      openChat();
    });
  }

  closeBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    closeChat();
  });

  if (moreBtn && moreDropdown) {
    moreBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      moreDropdown.classList.toggle('show');
    });

    document.addEventListener('click', function(e) {
      if (moreDropdown.classList.contains('show') && !moreDropdown.contains(e.target) && e.target !== moreBtn) {
        moreDropdown.classList.remove('show');
      }
    });
  }

  // ── VOZ EN TIEMPO REAL CON ELEVENLABS SPEECH ENGINE ──
  let currentVoiceAudio = null;
  let sharedVoiceAudio = null;
  let currentPlayingSourceNode = null;
  let firbyVoiceEnabled = true;

  function unlockAudioPlayback() {
    try {
      if (!sharedVoiceAudio) {
        sharedVoiceAudio = new Audio();
        sharedVoiceAudio.preload = 'auto';
      }
      sharedVoiceAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAP8A';
      sharedVoiceAudio.play().then(() => {
        try { sharedVoiceAudio.pause(); } catch(_) {}
      }).catch(() => {});

      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) {
        if (!liveAudioCtx || liveAudioCtx.state === 'closed') {
          liveAudioCtx = new AudioCtxClass();
        }
        if (liveAudioCtx.state === 'suspended') {
          liveAudioCtx.resume().catch(() => {});
        }
      }
    } catch (_) {}
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // MODO VOZ 1 A 1 EN TIEMPO REAL (LIVE VOICE MODE - CHATGPT / GEMINI LIVE)
  // ═══════════════════════════════════════════════════════════════════════════
  // ═══════════════════════════════════════════════════════════════════════════
  // MODO VOZ 1 A 1 EN TIEMPO REAL (LIVE VOICE MODE - AUDIO REACTIVE VISUALIZER)
  // ═══════════════════════════════════════════════════════════════════════════
  let isLiveVoiceActive = false;
  let isLiveVoiceMuted = false;
  let isFirbyBusy = false;
  let liveSpeechRecognizer = null;
  let isRecognitionRunning = false;
  let recognitionRestartTimer = null;
  let turnSilenceTimer = null;
  let liveVoiceAudio = null;
  let liveAudioStream = null;
  let liveAudioCtx = null;
  let liveAnalyser = null;
  let liveSource = null;
  let liveVisualizerAnimId = null;
  let liveMediaRecorder = null;
  let liveRecordedChunks = [];
  let isVADSpeaking = false;
  let currentTurnTranscript = '';
  const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
  const hasNativeSpeechRecognition = Boolean(SpeechRecognitionAPI);

  async function requestMicAccess() {
    if (!isLiveVoiceActive || isLiveVoiceMuted) return false;

    if (lvoPermBtn) lvoPermBtn.style.display = 'none';
    if (lvoStatusText) lvoStatusText.textContent = 'Iniciando micrófono...';

    // Llamar a getUserMedia directamente para preservar el User Activation (gesto del usuario)
    // Esto asegura que Google Chrome, Safari y navegadores móviles muestren la notificación nativa de permitir micrófono.
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      if (lvoStatusText) lvoStatusText.textContent = 'Tu navegador no permite captura de audio en esta sesión.';
      if (lvoPermBtn) {
        lvoPermBtn.textContent = 'Reintentar activación';
        lvoPermBtn.style.display = 'inline-flex';
      }
      return false;
    }

    try {
      if (!liveAudioStream || !liveAudioStream.active) {
        liveAudioStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          }
        });
        console.log('[Live Voice] Mic access granted with echo cancellation & noise suppression.');
      }
    } catch (err) {
      console.warn('[Live Voice] getUserMedia error:', err);
      const errName = err && (err.name || err.code);
      if (errName === 'NotAllowedError' || errName === 'PermissionDeniedError') {
        if (lvoStatusText) {
          lvoStatusText.textContent = 'Micrófono bloqueado. Toca el candado o ajustes junto a la URL para permitirlo.';
        }
        if (lvoPermBtn) {
          lvoPermBtn.textContent = 'Reintentar activación';
          lvoPermBtn.style.display = 'inline-flex';
        }
        return false;
      } else if (errName === 'NotFoundError' || errName === 'DevicesNotFoundError') {
        if (lvoStatusText) {
          lvoStatusText.textContent = 'No se detectó un micrófono disponible en tu dispositivo.';
        }
        if (lvoPermBtn) {
          lvoPermBtn.textContent = 'Reintentar detección';
          lvoPermBtn.style.display = 'inline-flex';
        }
        return false;
      } else {
        if (lvoStatusText) {
          lvoStatusText.textContent = 'No se pudo conectar al micrófono. Revisa los permisos.';
        }
        if (lvoPermBtn) {
          lvoPermBtn.textContent = 'Reintentar activación';
          lvoPermBtn.style.display = 'inline-flex';
        }
        return false;
      }
    }

    if (liveAudioStream) {
      // Iniciar el visualizador reactivo de audio por Web Audio API AnalyserNode
      startAudioVisualizer(liveAudioStream);
      // Iniciar grabador continuo de respaldo para VAD
      startLiveMediaRecorder(liveAudioStream);
    }

    if (lvoStatusText) lvoStatusText.textContent = 'Te escucho. Habla con naturalidad...';
    if (lvoOrb) lvoOrb.className = 'firby-lvo-orb listening';
    initSpeechRecognition();
    return true;
  }

  function startAudioVisualizer(stream) {
    try {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtxClass) return;
      if (!liveAudioCtx || liveAudioCtx.state === 'closed') {
        liveAudioCtx = new AudioCtxClass();
      }
      if (liveAudioCtx.state === 'suspended') {
        liveAudioCtx.resume();
      }

      if (liveSource) {
        try { liveSource.disconnect(); } catch (_) {}
      }
      liveSource = liveAudioCtx.createMediaStreamSource(stream);
      liveAnalyser = liveAudioCtx.createAnalyser();
      liveAnalyser.fftSize = 256;
      liveAnalyser.smoothingTimeConstant = 0.72;
      liveSource.connect(liveAnalyser);

      const canvas = document.getElementById('firby-lvo-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const bufferLength = liveAnalyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      let phase = 0;
      let smoothedVolume = 0;
      let smoothedBass = 0;

      function renderWave() {
        if (!isLiveVoiceActive) return;
        liveVisualizerAnimId = requestAnimationFrame(renderWave);

        liveAnalyser.getByteFrequencyData(dataArray);

        // Separar bandas de frecuencia (Vocal bass y volumen general)
        let totalSum = 0;
        let bassSum = 0;
        for (let i = 0; i < bufferLength; i++) {
          totalSum += dataArray[i];
          if (i < 12) bassSum += dataArray[i];
        }
        const currentVolume = totalSum / bufferLength; // 0..255
        const currentBass = bassSum / 12; // 0..255

        smoothedVolume += (currentVolume - smoothedVolume) * 0.25;
        smoothedBass += (currentBass - smoothedBass) * 0.28;

        // VAD: Si el volumen supera el umbral mientras el usuario habla y Firby no está activo
        const isAudioPlaying = (currentPlayingSourceNode !== null) || (liveVoiceAudio && !liveVoiceAudio.paused);
        const isFirbyActive = isFirbyBusy || isAudioPlaying;
        if (currentVolume > 15 && !isFirbyActive) {
          isVADSpeaking = true;
          // Solo si el navegador NO cuenta con Web Speech API nativo, delegar captura por VAD
          if (!hasNativeSpeechRecognition) {
            handleVadDirectAudioTurn();
          }
        }

        // Retina / Hi-DPI scaling dinámico
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const rect = canvas.getBoundingClientRect();
        const cssW = rect.width || 320;
        const cssH = rect.height || 65;
        const targetW = Math.round(cssW * dpr);
        const targetH = Math.round(cssH * dpr);

        if (canvas.width !== targetW || canvas.height !== targetH) {
          canvas.width = targetW;
          canvas.height = targetH;
        }

        ctx.save();
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, cssW, cssH);

        const centerY = cssH / 2;
        const normVol = smoothedVolume / 255;
        const normBass = smoothedBass / 255;

        // Velocidad y fase de animación fluida reactiva
        const speed = 0.05 + normVol * 0.14;
        phase += speed;

        const baseAmp = 3.5 + Math.sin(phase * 0.5) * 1.5;
        const voiceAmp = normVol * (cssH * 0.44);
        const totalAmp = isFirbyActive ? (13 + Math.sin(phase * 1.6) * 9) : (baseAmp + voiceAmp);

        // Modulación física del orbe en vivo con la voz
        if (lvoOrb) {
          const orbScale = 1 + Math.min(0.18, normBass * 0.35);
          const orbGlow = 22 + Math.min(55, normVol * 85);
          lvoOrb.style.transform = `scale(${orbScale.toFixed(3)})`;
          lvoOrb.style.boxShadow = `0 0 ${orbGlow.toFixed(1)}px rgba(185, 250, 1, ${(0.25 + normVol * 0.5).toFixed(2)})`;
        }

        // 4 capas armónicas fluidas estilo Apple Siri / Gemini Live (Curvas de Bézier seno con Bell Envelope)
        const waves = [
          { color: 'rgba(185, 250, 1, 0.95)', lineWidth: 2.2, freq: 0.032, ampMult: 1.0, phaseOff: 0, glow: 12 },
          { color: 'rgba(163, 230, 53, 0.75)', lineWidth: 1.8, freq: 0.042, ampMult: 0.78, phaseOff: 1.35, glow: 8 },
          { color: 'rgba(250, 204, 21, 0.45)', lineWidth: 1.4, freq: 0.024, ampMult: 0.58, phaseOff: 2.7, glow: 5 },
          { color: 'rgba(185, 250, 1, 0.30)', lineWidth: 1.2, freq: 0.018, ampMult: 0.38, phaseOff: 4.1, glow: 0 }
        ];

        waves.forEach(wave => {
          ctx.beginPath();
          ctx.lineWidth = wave.lineWidth;
          ctx.strokeStyle = wave.color;
          ctx.lineCap = 'round';
          ctx.lineJoin = 'round';
          ctx.shadowBlur = smoothedVolume > 14 ? wave.glow : Math.floor(wave.glow * 0.5);
          ctx.shadowColor = 'rgba(185, 250, 1, 0.55)';

          for (let x = 0; x <= cssW; x += 2) {
            const normX = x / cssW; // 0..1
            // Bell curve envelope: sin(pi * x)^2 para caída suave hacia los bordes
            const envelope = Math.pow(Math.sin(Math.PI * normX), 2);
            const y = centerY + Math.sin(x * wave.freq + phase + wave.phaseOff) * totalAmp * wave.ampMult * envelope;
            if (x === 0) {
              ctx.moveTo(x, y);
            } else {
              ctx.lineTo(x, y);
            }
          }
          ctx.stroke();
        });

        ctx.restore();
      }

      if (liveVisualizerAnimId) cancelAnimationFrame(liveVisualizerAnimId);
      renderWave();
    } catch (e) {
      console.warn('[Live Voice] Visualizer init error:', e);
    }
  }

  function startLiveMediaRecorder(stream) {
    if (!window.MediaRecorder || !stream) return;
    try {
      if (liveMediaRecorder && liveMediaRecorder.state !== 'inactive') {
        try { liveMediaRecorder.stop(); } catch(_) {}
      }

      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : (MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' : '');
      }

      liveRecordedChunks = [];
      liveMediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      liveMediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          liveRecordedChunks.push(e.data);
        }
      };
      liveMediaRecorder.start(250);
    } catch(e) {
      console.warn('[Live Voice] MediaRecorder start error:', e);
    }
  }

  function handleVadDirectAudioTurn() {
    if (!isLiveVoiceActive || isLiveVoiceMuted || isFirbyBusy) return;
    if (currentPlayingSourceNode || (liveVoiceAudio && !liveVoiceAudio.paused)) return;

    clearTimeout(turnSilenceTimer);
    turnSilenceTimer = setTimeout(async () => {
      const isAudioPlaying = (currentPlayingSourceNode !== null) || (liveVoiceAudio && !liveVoiceAudio.paused);
      if (isLiveVoiceActive && !isLiveVoiceMuted && !isFirbyBusy && !isAudioPlaying) {
        if (liveRecordedChunks.length > 0 && isVADSpeaking) {
          isVADSpeaking = false;
          const mime = liveMediaRecorder ? (liveMediaRecorder.mimeType || 'audio/webm') : 'audio/webm';
          let recordedBlob = null;
          if (liveMediaRecorder && liveMediaRecorder.state !== 'inactive') {
            recordedBlob = await new Promise((resolve) => {
              liveMediaRecorder.onstop = () => {
                const b = new Blob(liveRecordedChunks, { type: mime });
                liveRecordedChunks = [];
                resolve(b);
              };
              try {
                if (liveMediaRecorder.state === 'recording') {
                  liveMediaRecorder.requestData();
                }
                liveMediaRecorder.stop();
              } catch (_) {
                resolve(new Blob(liveRecordedChunks, { type: mime }));
              }
            });
            if (liveAudioStream) {
              setTimeout(() => { if (isLiveVoiceActive && !isLiveVoiceMuted && !isFirbyBusy) startLiveMediaRecorder(liveAudioStream); }, 150);
            }
          } else {
            recordedBlob = new Blob(liveRecordedChunks, { type: mime });
            liveRecordedChunks = [];
          }

          if (recordedBlob && recordedBlob.size > 2000) {
            const b64 = await blobToBase64(recordedBlob);
            handleLiveVoiceTurn('', b64, mime);
          }
        }
        isVADSpeaking = false;
      }
    }, 850);
  }

  function initSpeechRecognition() {
    if (!isLiveVoiceActive || isLiveVoiceMuted || !hasNativeSpeechRecognition) return;

    if (liveSpeechRecognizer) {
      try {
        liveSpeechRecognizer.onend = null;
        liveSpeechRecognizer.onerror = null;
        liveSpeechRecognizer.onresult = null;
        liveSpeechRecognizer.onstart = null;
        liveSpeechRecognizer.stop();
      } catch(_) {}
      liveSpeechRecognizer = null;
      isRecognitionRunning = false;
    }

    try {
      liveSpeechRecognizer = new SpeechRecognitionAPI();
      liveSpeechRecognizer.continuous = true;
      liveSpeechRecognizer.interimResults = true;
      liveSpeechRecognizer.lang = 'es-419';

      liveSpeechRecognizer.onstart = () => {
        isRecognitionRunning = true;
        if (isLiveVoiceActive && !isFirbyBusy) {
          if (lvoStatusText) lvoStatusText.textContent = 'Te escucho. Habla con naturalidad...';
          if (lvoOrb) lvoOrb.className = 'firby-lvo-orb listening';
          if (lvoPermBtn) lvoPermBtn.style.display = 'none';
        }
      };

      liveSpeechRecognizer.onresult = (event) => {
        if (!isLiveVoiceActive || isLiveVoiceMuted || isFirbyBusy) return;

        let interim = '';
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }

        const currentSpeech = (finalTranscript || interim).trim();
        const hasFinal = Boolean((finalTranscript || '').trim());
        if (currentSpeech) {
          currentTurnTranscript = currentSpeech;
          if (lvoUserText) lvoUserText.textContent = `Tú: "${currentSpeech}"`;
          if (lvoOrb && !isFirbyBusy) lvoOrb.className = 'firby-lvo-orb listening';

          scheduleTurnSubmission(hasFinal);
        }
      };

      liveSpeechRecognizer.onerror = (e) => {
        console.warn('[Live Voice] Recognition error:', e.error);
        if (e.error === 'not-allowed') {
          isRecognitionRunning = false;
          if (lvoStatusText) lvoStatusText.textContent = 'Permiso de micrófono requerido en tu navegador.';
          if (lvoPermBtn) {
            lvoPermBtn.textContent = 'Permitir micrófono';
            lvoPermBtn.style.display = 'inline-flex';
          }
          return;
        }
        if (e.error === 'no-speech') return;

        isRecognitionRunning = false;
        if (isLiveVoiceActive && !isLiveVoiceMuted && !isFirbyBusy) {
          clearTimeout(recognitionRestartTimer);
          recognitionRestartTimer = setTimeout(() => {
            safeStartRecognition();
          }, 250);
        }
      };

      liveSpeechRecognizer.onend = () => {
        isRecognitionRunning = false;
        if (isLiveVoiceActive && !isLiveVoiceMuted && !isFirbyBusy) {
          clearTimeout(recognitionRestartTimer);
          recognitionRestartTimer = setTimeout(() => {
            safeStartRecognition();
          }, 100);
        }
      };

      safeStartRecognition();
    } catch (err) {
      console.warn('[Live Voice] SpeechRecognition setup error:', err);
    }
  }

  function safeStartRecognition() {
    if (!liveSpeechRecognizer || !isLiveVoiceActive || isLiveVoiceMuted || isFirbyBusy || isRecognitionRunning) return;
    try {
      liveSpeechRecognizer.start();
      isRecognitionRunning = true;
    } catch (e) {
      if (e && (e.name === 'InvalidStateError' || (e.message && e.message.includes('already started')))) {
        isRecognitionRunning = true;
      } else {
        console.warn('[Live Voice] safeStartRecognition error:', e);
      }
    }
  }

  function safeStopRecognition() {
    if (!liveSpeechRecognizer) return;
    try {
      liveSpeechRecognizer.stop();
    } catch (_) {}
    isRecognitionRunning = false;
  }

  function scheduleTurnSubmission(isFinal) {
    if (!isLiveVoiceActive || isLiveVoiceMuted || isFirbyBusy) return;

    clearTimeout(turnSilenceTimer);
    const delay = isFinal ? 550 : 1200;
    turnSilenceTimer = setTimeout(() => {
      if (!isLiveVoiceActive || isLiveVoiceMuted || isFirbyBusy) return;
      const textToSend = (currentTurnTranscript || '').trim();
      if (textToSend.length >= 2) {
        console.log('[Live Voice] Enviando turno conversacional reconocido:', textToSend);
        currentTurnTranscript = '';
        handleLiveVoiceTurn(textToSend);
      }
    }, delay);
  }

  function startLiveVoiceRecognition() {
    if (hasNativeSpeechRecognition) {
      if (!liveSpeechRecognizer) {
        initSpeechRecognition();
      } else {
        safeStartRecognition();
      }
    } else if (liveAudioStream) {
      startLiveMediaRecorder(liveAudioStream);
    }
  }

  function openLiveVoiceMode() {
    if (!liveVoiceOverlay) return;
    unlockAudioPlayback();
    isLiveVoiceActive = true;
    isLiveVoiceMuted = false;
    isFirbyBusy = false;
    currentTurnTranscript = '';
    liveVoiceOverlay.style.display = 'flex';
    if (livePageBorder) {
      livePageBorder.classList.add('active');
    }
    if (lvoStatusText) lvoStatusText.textContent = 'Conectando con Firby...';
    if (lvoUserText) lvoUserText.textContent = '';
    if (lvoAgentText) lvoAgentText.textContent = '';
    if (lvoOrb) lvoOrb.className = 'firby-lvo-orb listening';
    if (lvoPermBtn) lvoPermBtn.style.display = 'none';

    requestMicAccess();
  }

  function closeLiveVoiceMode() {
    isLiveVoiceActive = false;
    isFirbyBusy = false;
    clearTimeout(turnSilenceTimer);
    clearTimeout(recognitionRestartTimer);
    if (livePageBorder) {
      livePageBorder.classList.remove('active');
    }
    if (liveVisualizerAnimId) {
      cancelAnimationFrame(liveVisualizerAnimId);
      liveVisualizerAnimId = null;
    }
    if (liveVoiceOverlay) liveVoiceOverlay.style.display = 'none';
    if (liveSpeechRecognizer) {
      try {
        liveSpeechRecognizer.onend = null;
        liveSpeechRecognizer.onerror = null;
        liveSpeechRecognizer.onresult = null;
        liveSpeechRecognizer.onstart = null;
        liveSpeechRecognizer.abort();
      } catch(_) {}
      liveSpeechRecognizer = null;
      isRecognitionRunning = false;
    }
    if (currentPlayingSourceNode) {
      try { currentPlayingSourceNode.stop(); } catch(_) {}
      currentPlayingSourceNode = null;
    }
    if (liveVoiceAudio) {
      try { liveVoiceAudio.pause(); } catch(e){}
      liveVoiceAudio = null;
    }
    if (liveMediaRecorder && liveMediaRecorder.state !== 'inactive') {
      try { liveMediaRecorder.stop(); } catch(e){}
      liveMediaRecorder = null;
    }
    if (liveAudioStream) {
      try {
        liveAudioStream.getTracks().forEach(track => track.stop());
      } catch(e){}
      liveAudioStream = null;
    }
    if (liveAudioCtx && liveAudioCtx.state !== 'closed') {
      try { liveAudioCtx.close(); } catch(e){}
      liveAudioCtx = null;
    }
    if (lvoOrb) {
      lvoOrb.className = 'firby-lvo-orb';
      lvoOrb.style.transform = '';
      lvoOrb.style.boxShadow = '';
    }
  }

  function stopLiveVoiceRecognition() {
    safeStopRecognition();
  }

  if (lvoCloseBtn) lvoCloseBtn.addEventListener('click', closeLiveVoiceMode);
  if (lvoEndBtn) lvoEndBtn.addEventListener('click', closeLiveVoiceMode);

  if (lvoPermBtn) {
    lvoPermBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      unlockAudioPlayback();
      requestMicAccess();
    });
  }

  // Barge-in / Interrupt y reintento de conexión
  if (lvoOrb) {
    lvoOrb.addEventListener('click', () => {
      const isSpeaking = (currentPlayingSourceNode !== null) || (liveVoiceAudio && !liveVoiceAudio.paused) || isFirbyBusy;
      if (isSpeaking) {
        if (currentPlayingSourceNode) {
          try { currentPlayingSourceNode.stop(); } catch(_) {}
          currentPlayingSourceNode = null;
        }
        if (liveVoiceAudio) {
          try { liveVoiceAudio.pause(); } catch(e){}
          liveVoiceAudio = null;
        }
        isFirbyBusy = false;
        currentTurnTranscript = '';
        if (lvoStatusText) lvoStatusText.textContent = 'Te escucho. Habla con naturalidad...';
        if (lvoOrb) lvoOrb.className = 'firby-lvo-orb listening';
        safeStartRecognition();
      } else if (!liveAudioStream) {
        unlockAudioPlayback();
        requestMicAccess();
      }
    });
  }

  if (lvoStatusText) {
    lvoStatusText.addEventListener('click', () => {
      if (!liveAudioStream) {
        unlockAudioPlayback();
        requestMicAccess();
      }
    });
  }

  async function handleLiveVoiceTurn(userText, audioBase64 = null, audioMime = 'audio/webm') {
    if ((!userText && !audioBase64) || !isLiveVoiceActive) return;

    isFirbyBusy = true;
    clearTimeout(turnSilenceTimer);
    safeStopRecognition();

    if (lvoStatusText) lvoStatusText.textContent = 'Firby pensando...';
    if (lvoOrb) lvoOrb.className = 'firby-lvo-orb';

    try {
      const payload = {
        voice_mode: true,
        session_id: sessionId,
        org_id: ORG_ID,
        message: userText || (currentTurnTranscript || 'Mensaje de voz'),
        client_transcript: userText || currentTurnTranscript || '',
        web_context: {
          current_url: window.location.pathname,
          page_title: document.title
        }
      };

      if (audioBase64) {
        payload.audio_base64 = audioBase64;
        payload.audio_mime = audioMime;
      }

      const res = await fetch(`${API_HOST}/api/widget/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        if (lvoStatusText) lvoStatusText.textContent = 'Error de conexión. Reintentando...';
        return;
      }

      const data = await res.json();

      let uiAction = data.ui_action || data.action;

      const recognizedQuery = userText || data.user_message || data.transcribed_audio || '';
      if (!uiAction && recognizedQuery) {
        const lowerQ = recognizedQuery.toLowerCase();
        if (/\b(plan|planes|precio|precios|cu[aá]nto\s+cuesta|starter|pro|equipos)\b/.test(lowerQ)) {
          uiAction = { type: 'navigate_to_section', target: '#planes' };
        } else if (/\b(c[oó]mo\s+funciona|qu[eé]\s+hace|c[oó]mo\s+opera|funcionamiento|integraci[oó]n)\b/.test(lowerQ)) {
          uiAction = { type: 'navigate_to_section', target: '#como-funciona' };
        } else if (/\b(equipo|roles|empleados?\s+digital|asistente|recepcionista)\b/.test(lowerQ)) {
          uiAction = { type: 'navigate_to_section', target: '#equipo-digital' };
        } else if (/\b(canal|canales|whatsapp)\b/.test(lowerQ)) {
          uiAction = { type: 'navigate_to_section', target: '#canales' };
        } else if (/\b(contacto|probar|empezar|agenda|agendar|demo)\b/.test(lowerQ)) {
          uiAction = { type: 'navigate_to_section', target: '#contacto' };
        }
      }

      if (uiAction) {
        try { executeUiAction(uiAction); } catch(e){}
      }

      const bubbles = data.bubbles || [];
      let replyText = bubbles.length > 0 ? bubbles.join(' ') : (data.response || 'Entendido.');
      replyText = replyText
        .replace(/^(?:thought|thinking|pensamiento)[\s\S]*?(?:\n\n|\n[¿¡\[A-Z]|\b(?:profesionalismo|directo|calma)\.\s*(?=[A-Z¿¡\[]))/i, '')
        .replace(/^thought\s+/i, '')
        .trim() || replyText.replace(/^thought\s*/i, '').trim();

      const displayUserText = userText || recognizedQuery || '';
      if (displayUserText && displayUserText !== 'Mensaje de voz') {
        if (lvoUserText) lvoUserText.textContent = `Tú: "${displayUserText}"`;
        appendMessage(displayUserText, true, null, false);
      }
      appendMessage(replyText, false, null, false);

      // Limpiar texto para subtítulos visuales en el orbe
      const displayReply = replyText
        .replace(/\[(?:chuckles|laughs|risas?)\]/gi, '')
        .replace(/\[(?:pauses?|pausa|silence)\]/gi, '...')
        .replace(/\[(?:deep breath|respiraci[oó]n|sighs?|suspiro)\]/gi, '')
        .replace(/\[(?:clears throat|carraspeo)\]/gi, '')
        .replace(/\[(?:thinking|pensando|thoughtful pause)\]/gi, '')
        .replace(/\[(?:CHIPS|ACTION)[^\]]*\]/gi, '')
        .replace(/[#*_`~]/g, '')
        .replace(/\s+/g, ' ')
        .trim();

      if (lvoAgentText) lvoAgentText.textContent = `Firby: "${displayReply}"`;
      if (lvoStatusText) lvoStatusText.textContent = 'Firby hablando...';
      if (lvoOrb) lvoOrb.className = 'firby-lvo-orb speaking';

      // Transformar tags de modulación vocal para el motor neuronal ElevenLabs (voz de Rafa N)
      let cleanVoiceText = replyText
        .replace(/\[(?:chuckles|laughs|risas?)\]/gi, 'jaja, ')
        .replace(/\[(?:pauses?|pausa|silence)\]/gi, '... ')
        .replace(/\[(?:deep breath|respiraci[oó]n|sighs?|suspiro)\]/gi, '... uf... ')
        .replace(/\[(?:clears throat|carraspeo)\]/gi, '... a ver... ')
        .replace(/\[(?:thinking|pensando|thoughtful pause)\]/gi, '... déjame ver... ')
        .replace(/\[(?:CHIPS|ACTION)[^\]]*\]/gi, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/\[[^\]]*\]/g, '')
        .replace(/[#*_`~]/g, '')
        .replace(/\s+/g, ' ')
        .trim();

      // REPRODUCCIÓN ULTRA FIABLE Y SIN BLOQUEOS DE AUTOPLAY (WEB AUDIO API + BLOB AUDIO)
      if (currentPlayingSourceNode) {
        try { currentPlayingSourceNode.stop(); } catch(_) {}
        currentPlayingSourceNode = null;
      }
      if (liveVoiceAudio) {
        try { liveVoiceAudio.pause(); } catch(e){}
        liveVoiceAudio = null;
      }

      await playLiveVoiceAudio(cleanVoiceText);

    } catch(err) {
      console.warn('[Live Voice] Error in turn:', err);
    } finally {
      isFirbyBusy = false;
      currentTurnTranscript = '';
      if (isLiveVoiceActive && !isLiveVoiceMuted) {
        if (lvoStatusText) lvoStatusText.textContent = 'Te escucho. Habla con naturalidad...';
        if (lvoOrb) lvoOrb.className = 'firby-lvo-orb listening';
        setTimeout(() => {
          if (isLiveVoiceActive && !isFirbyBusy) {
            safeStartRecognition();
          }
        }, 120);
      }
    }
  }

  async function playLiveVoiceAudio(textToSpeak) {
    if (!textToSpeak) return false;
    try {
      const resp = await fetch('/api/speech-engine/tts-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: textToSpeak,
          voice_id: 'cjVigY5qzO86Huf0OWal'
        })
      });

      if (!resp.ok) {
        console.warn('[Live Voice] TTS error HTTP:', resp.status);
        return false;
      }

      const arrayBuffer = await resp.arrayBuffer();
      if (!arrayBuffer || arrayBuffer.byteLength < 250) {
        return false;
      }

      // 1. Primario: Web Audio API (Cero bloqueos de autoplay y sincronizado con el visualizador)
      if (liveAudioCtx && liveAudioCtx.state !== 'closed') {
        try {
          if (liveAudioCtx.state === 'suspended') {
            await liveAudioCtx.resume();
          }
          const audioBuffer = await liveAudioCtx.decodeAudioData(arrayBuffer.slice(0));
          const sourceNode = liveAudioCtx.createBufferSource();
          sourceNode.buffer = audioBuffer;

          if (liveAnalyser) {
            sourceNode.connect(liveAnalyser);
          }
          sourceNode.connect(liveAudioCtx.destination);
          currentPlayingSourceNode = sourceNode;
          return await new Promise((resolve) => {
            sourceNode.onended = () => {
              try { sourceNode.disconnect(); } catch (_) {}
              currentPlayingSourceNode = null;
              setTimeout(() => resolve(true), 200);
            };
            sourceNode.start(0);
          });
        } catch (ctxErr) {
          console.warn('[Live Voice] Web Audio decode fallback:', ctxErr);
        }
      }

      // 2. Secundario: HTML5 Audio con Blob URL y elemento pre-activado
      const blob = new Blob([arrayBuffer], { type: 'audio/mpeg' });
      const blobUrl = URL.createObjectURL(blob);
      const audioEl = sharedVoiceAudio || new Audio();
      liveVoiceAudio = audioEl;
      audioEl.src = blobUrl;

      return await new Promise((resolve) => {
        audioEl.onended = () => {
          URL.revokeObjectURL(blobUrl);
          liveVoiceAudio = null;
          setTimeout(() => resolve(true), 200);
        };
        audioEl.onerror = () => {
          URL.revokeObjectURL(blobUrl);
          liveVoiceAudio = null;
          resolve(false);
        };
        audioEl.play().catch((e) => {
          console.warn('[Live Voice] HTML5 play blocked:', e);
          URL.revokeObjectURL(blobUrl);
          liveVoiceAudio = null;
          resolve(false);
        });
      });
    } catch (err) {
      console.warn('[Live Voice] Error reproduciendo voz:', err);
      return false;
    }
  }

  window.FirbyLiveVoice = {
    open: openLiveVoiceMode,
    close: closeLiveVoiceMode,
    handleTurn: handleLiveVoiceTurn,
    requestMic: requestMicAccess
  };

  async function playFirbyVoice(text) {
    if (!text) return;
    const cleanText = text
      .replace(/\[(?:chuckles|laughs|risas?)\]/gi, '')
      .replace(/\[(?:pauses?|pausa|silence)\]/gi, '...')
      .replace(/\[(?:deep breath|respiraci[oó]n|sighs?|suspiro)\]/gi, '')
      .replace(/\[(?:clears throat|carraspeo)\]/gi, '')
      .replace(/\[(?:thinking|pensando|thoughtful pause)\]/gi, '')
      .replace(/\[(?:CHIPS|ACTION)[^\]]*\]/gi, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/\[[^\]]*\]/g, '')
      .replace(/[#*_`~]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    if (!cleanText) return;

    try {
      if (currentVoiceAudio) {
        try { currentVoiceAudio.pause(); } catch(e){}
        currentVoiceAudio = null;
      }
      const response = await fetch('/api/speech-engine/tts-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: cleanText,
          voice_id: 'cjVigY5qzO86Huf0OWal'
        })
      });
      if (!response.ok) return;

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
      currentVoiceAudio = new Audio(audioUrl);
      currentVoiceAudio.play().catch(function(err) {
        console.warn('[Firby Voice] Reproducción bloqueada por política del navegador:', err);
      });
    } catch (err) {
      console.warn('[Firby Voice] Error reproduciendo voz:', err);
    }
  }

  // Sincronización WebSocket para acciones visuales transmitidas por Speech Engine
  function initSpeechEngineWebSync() {
    try {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${proto}//${window.location.host}/api/speech-engine/web-sync/${sessionId}`;
      const ws = new WebSocket(wsUrl);
      ws.onmessage = function(event) {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'firby_action' && data.action) {
            console.log('[Firby Voice Sync] Acción ejecutada en vivo:', data.action);
            executeUiAction(data.action);
          }
        } catch (e) {}
      };
      ws.onclose = function() {
        setTimeout(initSpeechEngineWebSync, 10000);
      };
    } catch (e) {}
  }
  initSpeechEngineWebSync();

  function resetChatSession() {
    sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    try {
      localStorage.setItem(SESSION_KEY, sessionId);
      sessionStorage.removeItem('firby_chat_history');
      sessionStorage.removeItem('firby_session_id');
    } catch (e) {}
    chatHistoryState = [];
    if (streamEl) {
      const timeBadge = streamEl.querySelector('.firby-stream-time-badge');
      const policyRow = streamEl.querySelector('#firby-initial-policy-row');
      streamEl.innerHTML = '';
      if (timeBadge) streamEl.appendChild(timeBadge);
      if (policyRow) streamEl.appendChild(policyRow);
    }
  }

  if (resetChatBtn) {
    resetChatBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      if (moreDropdown) moreDropdown.classList.remove('show');
      resetChatSession();
    });
  }

  if (chatLauncher) {
    chatLauncher.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      openChat();
    });
  }

  if (aboutLauncher) {
    aboutLauncher.addEventListener('click', function(e) {
      bwsHW.classList.remove('bws-hw-active');
      window.location.href = '/about-us';
    });
  }

  if (faqLauncher) {
    faqLauncher.addEventListener('click', function(e) {
      bwsHW.classList.remove('bws-hw-active');
      window.location.href = '/faq';
    });
  }

  const whatsappLauncher = document.getElementById('whatsappLauncher');
  if (whatsappLauncher) {
    whatsappLauncher.addEventListener('click', function(e) {
      bwsHW.classList.remove('bws-hw-active');
    });
  }

  // Cerrar menú al hacer clic afuera
  document.addEventListener('click', function(e) {
    if (bwsHW.classList.contains('bws-hw-active') && !bwsHW.contains(e.target)) {
      bwsHW.classList.remove('bws-hw-active');
    }
  });

  if (teaserPill) {
    teaserPill.addEventListener('click', function(e) {
      e.preventDefault();
      openChat();
    });
  }

  // Interacción botón de consentimiento ("Sí, acepto")
  if (consentBtn) {
    consentBtn.addEventListener('click', () => {
      if (consentContainer) consentContainer.style.display = 'none';
      try { localStorage.setItem('firby_privacy_accepted', 'true'); } catch (_) {}
      updateSuggestionsDock(isLanding ? ['Ver cómo funciona', 'Ver planes y precios', 'Cómo se instala'] : ['Horarios de atención', 'Agendar cita', 'Servicios']);
      sendMessage('Sí, acepto');
      if (inputEl) inputEl.focus();
    });
  }

  // Actualizar el Dock de Sugerencias Horizontal con Soporte para Action Chips
  function updateSuggestionsDock(chips, actionChips = null) {
    if (!suggestionsDock) return;
    if ((!chips || chips.length === 0) && (!actionChips || actionChips.length === 0)) {
      suggestionsDock.innerHTML = '';
      suggestionsDock.style.display = 'none';
      return;
    }
    suggestionsDock.style.display = 'flex';
    
    if (actionChips && actionChips.length > 0) {
      suggestionsDock.innerHTML = actionChips
        .map(ac => {
          const type = ac.action_type || '';
          const target = ac.action_target || '';
          return `<button class="firby-chip firby-action-chip" type="button" data-msg="${ac.label}" data-action-type="${type}" data-action-target="${target}">${ac.label}</button>`;
        })
        .join('');
    } else {
      suggestionsDock.innerHTML = chips
        .map(c => `<button class="firby-chip" type="button" data-msg="${c}">${c}</button>`)
        .join('');
    }
    suggestionsDock.scrollLeft = 0;
  }

  // Delegación de eventos en el Dock de Sugerencias
  if (suggestionsDock) {
    suggestionsDock.addEventListener('click', (e) => {
      const btn = e.target.closest('.firby-chip');
      if (!btn) return;
      const msg = btn.getAttribute('data-msg');

      if (msg) {
        updateSuggestionsDock([]);
        sendMessage(msg);
      }
    });
  }

  // Inicialmente si ya aceptó la política mostramos los chips de solución
  if (typeof localStorage !== 'undefined' && localStorage.getItem('firby_privacy_accepted') === 'true') {
    updateSuggestionsDock(isLanding ? ['Ver cómo funciona', 'Ver planes y precios', 'Cómo se instala'] : ['Horarios de atención', 'Agendar cita', 'Servicios']);
  } else {
    updateSuggestionsDock([]);
  }

  // ── Persistencia del Historial de Conversación en Sesión ──
  let chatHistoryState = [];

  function saveChatHistory() {
    try {
      if (typeof sessionStorage !== 'undefined') {
        sessionStorage.setItem('firby_chat_history', JSON.stringify(chatHistoryState));
        sessionStorage.setItem('firby_session_id', sessionId);
      }
    } catch (e) {}
  }

  // ── Smart Physics-based Scroll & New Message Pill ──
  function isUserNearBottom() {
    if (!streamEl) return true;
    const threshold = 110;
    return (streamEl.scrollHeight - streamEl.scrollTop - streamEl.clientHeight) <= threshold;
  }

  function scrollToBottom(smooth = true) {
    if (!streamEl) return;
    if (smooth && typeof streamEl.scrollTo === 'function') {
      streamEl.scrollTo({ top: streamEl.scrollHeight, behavior: 'smooth' });
    } else {
      streamEl.scrollTop = streamEl.scrollHeight;
    }
    if (scrollBottomPill) {
      scrollBottomPill.classList.remove('visible');
    }
  }

  function handleAutoScroll(force = false) {
    if (force || isUserNearBottom()) {
      scrollToBottom(!force);
    } else {
      if (scrollBottomPill) {
        scrollBottomPill.classList.add('visible');
      }
    }
  }

  function renderMessageDOM(text, isUser = false, attachment = null) {
    if (isUser) {
      const msgEl = document.createElement('div');
      msgEl.className = 'firby-msg firby-msg-user';
      if (text) {
        const textSpan = document.createElement('div');
        textSpan.textContent = text;
        msgEl.appendChild(textSpan);
      }
      if (attachment) {
        if (attachment.isAudio || (attachment.name && attachment.name.startsWith('nota_de_voz'))) {
          const playerEl = document.createElement('div');
          playerEl.className = 'firby-voice-player';
          const audioUrl = attachment.url || '';
          const duration = attachment.duration || '0:03';

          playerEl.innerHTML = `
            <button type="button" class="firby-vp-play-btn" aria-label="Reproducir mensaje de voz">
              <svg class="firby-vp-icon-play" width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="6 4 20 12 6 20 6 4"></polygon>
              </svg>
              <svg class="firby-vp-icon-pause" width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="display:none;">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
            </button>
            <div class="firby-vp-track">
              <div class="firby-vp-waveform">
                <span style="height:35%;"></span>
                <span style="height:60%;"></span>
                <span style="height:85%;"></span>
                <span style="height:50%;"></span>
                <span style="height:80%;"></span>
                <span style="height:100%;"></span>
                <span style="height:70%;"></span>
                <span style="height:45%;"></span>
                <span style="height:90%;"></span>
                <span style="height:65%;"></span>
                <span style="height:95%;"></span>
                <span style="height:40%;"></span>
                <span style="height:75%;"></span>
                <span style="height:100%;"></span>
                <span style="height:55%;"></span>
                <span style="height:80%;"></span>
                <span style="height:35%;"></span>
              </div>
            </div>
            <span class="firby-vp-time">${duration}</span>
          `;

          if (audioUrl) {
            const playBtn = playerEl.querySelector('.firby-vp-play-btn');
            const playIcon = playerEl.querySelector('.firby-vp-icon-play');
            const pauseIcon = playerEl.querySelector('.firby-vp-icon-pause');
            const bars = playerEl.querySelectorAll('.firby-vp-waveform span');
            const timeEl = playerEl.querySelector('.firby-vp-time');

            let audio = new Audio(audioUrl);
            let isPlaying = false;

            playBtn.addEventListener('click', (e) => {
              e.preventDefault();
              e.stopPropagation();
              if (!isPlaying) {
                audio.play().then(() => {
                  isPlaying = true;
                  playIcon.style.display = 'none';
                  pauseIcon.style.display = 'block';
                }).catch((err) => {
                  console.warn('Playback error:', err);
                });
              } else {
                audio.pause();
                isPlaying = false;
                playIcon.style.display = 'block';
                pauseIcon.style.display = 'none';
              }
            });

            audio.addEventListener('timeupdate', () => {
              if (!audio.duration) return;
              const progress = audio.currentTime / audio.duration;
              const activeCount = Math.floor(progress * bars.length);
              bars.forEach((bar, idx) => {
                if (idx <= activeCount) {
                  bar.classList.add('played');
                } else {
                  bar.classList.remove('played');
                }
              });
              const rem = Math.max(0, Math.ceil(audio.duration - audio.currentTime));
              const m = Math.floor(rem / 60);
              const s = (rem % 60).toString().padStart(2, '0');
              timeEl.textContent = `${m}:${s}`;
            });

            audio.addEventListener('ended', () => {
              isPlaying = false;
              playIcon.style.display = 'block';
              pauseIcon.style.display = 'none';
              bars.forEach(b => b.classList.remove('played'));
              timeEl.textContent = duration;
            });
          }

          msgEl.appendChild(playerEl);
        } else {
          const fileChip = document.createElement('div');
          fileChip.className = 'firby-msg-file-badge';
          fileChip.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <span>${attachment.name || attachment}</span>
          `;
          msgEl.appendChild(fileChip);
        }
      }
      streamEl.appendChild(msgEl);
    } else {
      const rowEl = document.createElement('div');
      rowEl.className = 'firby-msg-row firby-msg-row-agent';
      rowEl.innerHTML = `
        <div class="firby-msg-avatar-wrap">
          ${getFirbyAvatarHtml(false)}
        </div>
        <div class="firby-msg-content-wrap">
          <div class="firby-msg firby-msg-agent">
            ${formatMarkdown(text)}
          </div>
        </div>
      `;
      streamEl.appendChild(rowEl);
    }
    if (isUser) {
      handleAutoScroll(true);
    } else {
      handleAutoScroll(false);
    }
  }

  function appendMessage(text, isUser = false, attachment = null, skipPersist = false) {
    if (!isUser && typeof text === 'string') {
      text = text
        .replace(/^(?:thought|thinking|pensamiento)[\s\S]*?(?:\n\n|\n[¿¡\[A-Z]|\b(?:profesionalismo|directo|calma)\.\s*(?=[A-Z¿¡\[]))/i, '')
        .replace(/^thought\s+/i, '')
        .trim() || text.replace(/^thought\s*/i, '').trim();
    }
    if (!skipPersist) {
      chatHistoryState.push({
        type: 'message',
        text: text,
        isUser: isUser,
        attachment: attachment ? {
          name: attachment.name || attachment,
          url: attachment.url || '',
          duration: attachment.duration || '',
          isAudio: !!attachment.isAudio,
          transcript: attachment.transcript || ''
        } : null,
        timestamp: Date.now()
      });
      saveChatHistory();
    }
    renderMessageDOM(text, isUser, attachment);
  }

  function appendActionCard(card, skipPersist = false) {
    if (!card) return;
    if (!skipPersist) {
      chatHistoryState.push({
        type: 'card',
        card: card,
        timestamp: Date.now()
      });
      saveChatHistory();
    }
    const wrap = document.createElement('div');
    wrap.className = 'firby-msg-row firby-msg-row-agent firby-card-row';

    if (card.type === 'consent_terms') {
      wrap.innerHTML = `
        <div class="firby-msg-avatar-wrap" style="visibility: hidden;"></div>
        <div class="firby-msg-content-wrap" style="width: 100%;">
          <div class="firby-consent-container" style="margin: 4px 0 6px 0;">
            <button type="button" class="firby-consent-btn firby-dynamic-consent-btn">
              ${card.label || 'Sí, acepto'}
            </button>
          </div>
        </div>
      `;
      const btn = wrap.querySelector('.firby-dynamic-consent-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          try { localStorage.setItem('firby_privacy_accepted', 'true'); } catch (_) {}
          updateSuggestionsDock(isLanding ? ['Ver cómo funciona', 'Ver planes y precios', 'Cómo se instala'] : ['Horarios de atención', 'Agendar cita', 'Servicios']);
          btn.disabled = true;
          btn.style.opacity = '0.5';
          btn.style.pointerEvents = 'none';
          sendMessage('Sí, acepto');
          if (inputEl) inputEl.focus();
        });
      }
      streamEl.appendChild(wrap);
      handleAutoScroll(false);
      return;
    }

    const cardContent = card.type === 'google_auth' ? `
      <a href="${card.url}" class="firby-google-btn" target="_blank" rel="noopener">
        <svg class="firby-google-icon" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        <span>${card.label || 'Continuar con Google'}</span>
      </a>
    ` : `
      <a href="${card.url}" class="firby-action-btn" target="_blank" rel="noopener">
        <span>${card.label || 'Continuar'}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
      </a>
    `;

    wrap.innerHTML = `
      <div class="firby-msg-avatar-wrap" style="visibility: hidden;"></div>
      <div class="firby-msg-content-wrap" style="width: 100%;">
        <div class="firby-card-container">${cardContent}</div>
      </div>
    `;
    streamEl.appendChild(wrap);
    handleAutoScroll(false);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // MOTOR SHADER LIQUID ORB 3D NATIVO (100% TRANSPARENTE, ZERO LATENCIA)
  // Estados: idle (reposo suave) y thinking (flujo líquido acelerado con aura)
  // ═══════════════════════════════════════════════════════════════════════════
  let activeOrbEngine = null;

  function createLiquidOrb(canvas, isThinking = true) {
    if (!canvas) return null;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;

    let running = true;
    let animId = null;
    let start = performance.now();

    const w = canvas.width;
    const h = canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const baseR = w * 0.32;

    function loop(now) {
      if (!running) return;
      const t = (now - start) * 0.0035;
      ctx.clearRect(0, 0, w, h);

      // 1. Resplandor exterior suave Siri (Aura #956CFF / #82F4FF)
      const pulse = Math.sin(t * 3.0) * 0.08 + 1.0;
      const rOuter = baseR * 1.35 * pulse;
      const glowGrad = ctx.createRadialGradient(cx, cy, baseR * 0.2, cx, cy, rOuter);
      glowGrad.addColorStop(0, "rgba(142, 108, 255, 0.45)");
      glowGrad.addColorStop(0.5, "rgba(130, 244, 255, 0.25)");
      glowGrad.addColorStop(1, "rgba(149, 108, 255, 0)");
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, rOuter, 0, Math.PI * 2);
      ctx.fill();

      // 2. Núcleo líquido orgánico con deformación armónica Siri
      ctx.save();
      ctx.translate(cx, cy);
      ctx.beginPath();
      const points = 36;
      for (let i = 0; i <= points; i++) {
        const angle = (i / points) * Math.PI * 2;
        const wave1 = Math.sin(angle * 3 + t * 4.2) * 3.2;
        const wave2 = Math.cos(angle * 5 - t * 3.1) * 2.2;
        const wave3 = Math.sin(angle * 2 + t * 2.0) * 1.5;
        const r = (baseR * pulse) + wave1 + wave2 + wave3;
        const x = Math.cos(angle) * r;
        const y = Math.sin(angle) * r;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();

      // Gradiente cromático Siri (#FFD86B solar -> #FF7BD5 pink -> #82F4FF cyan -> #8E6CFF purple)
      const coreGrad = ctx.createRadialGradient(-baseR * 0.3, -baseR * 0.3, baseR * 0.08, 0, 0, baseR * 1.15);
      coreGrad.addColorStop(0, "#FFFFFF");
      coreGrad.addColorStop(0.2, "#FFD86B");
      coreGrad.addColorStop(0.5, "#FF7BD5");
      coreGrad.addColorStop(0.78, "#82F4FF");
      coreGrad.addColorStop(1.0, "#8E6CFF");
      ctx.fillStyle = coreGrad;
      ctx.fill();

      // Destello especular satinado
      ctx.beginPath();
      ctx.ellipse(-baseR * 0.26, -baseR * 0.26, baseR * 0.32, baseR * 0.18, Math.PI / 4, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 255, 255, 0.55)";
      ctx.fill();
      ctx.restore();

      animId = requestAnimationFrame(loop);
    }
    animId = requestAnimationFrame(loop);

    return {
      stop: () => {
        running = false;
        if (animId) cancelAnimationFrame(animId);
      }
    };
  }

  let activeLatticeTimer = null;

  function showTyping() {
    hideTyping();
    const typing = document.createElement('div');
    typing.className = 'firby-msg-row firby-msg-row-agent firby-orb-thinking';
    typing.id = 'firby-typing-indicator';
    typing.innerHTML = `
      <div class="firby-msg-avatar-wrap">
        ${getFirbyAvatarHtml(false)}
      </div>
      <div class="firby-thinking-badge">
        <span role="status" class="lattice-loader" data-status="working" data-shape="round" style="--ll-n: 3; --ll-cell: 5.5px; --ll-gap: 2px; --ll-font: 13px; --ll-color: currentColor; --ll-mark: #22c55e; --ll-idle: 0.15; --ll-glow: currentColor; --ll-mark-glow: #22c55e; --ll-cycle: 864ms;">
          <span class="lattice-loader__grid" aria-hidden="true">
            <span class="lattice-loader__layer lattice-loader__run">
              <span class="lattice-loader__cell" style="animation-delay: 0ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 108ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 216ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 756ms;"></span>
              <span class="lattice-loader__cell" data-hole=""></span>
              <span class="lattice-loader__cell" style="animation-delay: 324ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 648ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 540ms;"></span>
              <span class="lattice-loader__cell" style="animation-delay: 432ms;"></span>
            </span>
            <span class="lattice-loader__layer lattice-loader__mark">
              <span class="lattice-loader__cell"></span>
              <span class="lattice-loader__cell"></span>
              <span class="lattice-loader__cell" data-on=""></span>
              <span class="lattice-loader__cell" data-on=""></span>
              <span class="lattice-loader__cell"></span>
              <span class="lattice-loader__cell" data-on=""></span>
              <span class="lattice-loader__cell"></span>
              <span class="lattice-loader__cell" data-on=""></span>
              <span class="lattice-loader__cell"></span>
            </span>
          </span>
          <span class="lattice-loader__label" aria-hidden="true">
            <span class="lattice-loader__text" data-active="">Thinking</span>
            <span class="lattice-loader__text">Done in</span>
            <span class="lattice-loader__text">Failed after</span>
          </span>
          <span class="lattice-loader__timer" id="firby-lattice-timer" aria-hidden="true">0.0s</span>
          <span class="lattice-loader__sr">Thinking, in progress</span>
        </span>
      </div>
    `;
    streamEl.appendChild(typing);
    handleAutoScroll(false);

    const timerEl = typing.querySelector('#firby-lattice-timer');
    const startTime = performance.now();
    activeLatticeTimer = setInterval(() => {
      if (!timerEl) return;
      const ds = Math.floor((performance.now() - startTime) / 100);
      timerEl.textContent = ds < 600 ? `${(ds / 10).toFixed(1)}s` : `${Math.floor(ds / 600)}m ${((ds % 600) / 10).toFixed(1)}s`;
    }, 100);
  }

  function hideTyping() {
    if (activeLatticeTimer) {
      clearInterval(activeLatticeTimer);
      activeLatticeTimer = null;
    }
    const el = document.getElementById('firby-typing-indicator');
    if (el) el.remove();
  }

  function formatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Bold y Cursiva: Regla inquebrantable de CERO BOLD (Santiago)
    html = html.replace(/\*\*(.*?)\*\*/g, '$1');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Procesar líneas con viñetas "-" o "•" para estructura limpia estilo Sierra AI
    const lines = html.split('\n');
    const formattedLines = lines.map(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
        const itemContent = trimmed.substring(2).trim();
        return `<div class="firby-bullet-item"><span class="firby-bullet-dot"></span><span>${itemContent}</span></div>`;
      }
      return line;
    });

    html = formattedLines.join('<br/>');
    html = html.replace(/(<\/div>)<br\/>/g, '$1');
    html = html.replace(/<br\/>(<div class="firby-bullet-item">)/g, '$1');
    return html;
  }

  // ── Copilot UI Actions & Spotlight Engine ──
  // ── Estado y Verificación de Eventos del Agente (Agent Events & Feedback Loop) ──
  let lastNavigationEvent = {
    status: 'idle',
    target: null,
    timestamp: Date.now()
  };

  // ── Copilot UI Actions & Spotlight Engine ──
  function premiumSmoothScroll(targetEl) {
    if (!targetEl) return;
    const startY = window.pageYOffset || document.documentElement.scrollTop;
    const rect = targetEl.getBoundingClientRect();
    const offset = 84; // Offset para evitar que el header fijo tape el título
    const targetY = Math.max(0, startY + rect.top - offset);
    const distance = Math.abs(targetY - startY);

    // Duración adaptativa cinematográfica según distancia física real:
    // Si está en la página principal / Hero (>3000px), scroll lento y profesional (2.9s - 3.4s)
    // Si está una página arriba (800px - 2500px), scroll pausado (2.0s - 2.6s)
    let duration = 1250;
    if (distance > 3000) {
      duration = Math.min(3400, Math.round(2900 + (distance - 3000) * 0.15));
    } else if (distance > 1200) {
      duration = Math.min(2900, Math.round(2200 + (distance - 1200) * 0.35));
    } else if (distance > 350) {
      duration = Math.min(2200, Math.round(1800 + (distance - 350) * 0.45));
    }
    let startTime = null;

    // Disparar eventos de navegación y sección solicitada
    try {
      window.dispatchEvent(new CustomEvent('firby:agent.navigation.requested', {
        detail: { target: targetEl.id, distance, duration }
      }));
      window.dispatchEvent(new CustomEvent('firby:agent.section.requested', {
        detail: { target: targetEl.id, distance }
      }));
    } catch (e) {}

    function easeInOutCubic(t) {
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    // Si Lenis está activo en la página, usar su motor para sincronizar la inercia
    if (window.lenis && typeof window.lenis.scrollTo === 'function') {
      window.lenis.scrollTo(targetEl, {
        offset: -offset,
        duration: duration / 1000,
        easing: easeInOutCubic,
        onComplete: () => {
          highlightElement(targetEl);
          lastNavigationEvent = {
            status: 'section_reached',
            target: targetEl.id,
            timestamp: Date.now()
          };
          try {
            window.dispatchEvent(new CustomEvent('firby:agent.section.reached', {
              detail: { target: targetEl.id, finalY: targetY }
            }));
            window.dispatchEvent(new CustomEvent('firby:agent.navigation.completed', {
              detail: { target: targetEl.id }
            }));
            window.dispatchEvent(new CustomEvent('firby:agent.action.completed', {
              detail: { type: 'navigate_to_section', target: targetEl.id }
            }));
            try {
              if (window.location.hash !== '#' + targetEl.id) {
                history.replaceState(null, '', '#' + targetEl.id);
              }
            } catch (e) {}
          } catch (e) {}
        }
      });
      return;
    }

    function step(currentTime) {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = easeInOutCubic(progress);
      window.scrollTo(0, startY + ((targetY - startY) * ease));

      if (elapsed < duration) {
        requestAnimationFrame(step);
      } else {
        window.scrollTo(0, targetY);
        highlightElement(targetEl);
        lastNavigationEvent = {
          status: 'section_reached',
          target: targetEl.id,
          timestamp: Date.now()
        };
        try {
          window.dispatchEvent(new CustomEvent('firby:agent.section.reached', {
            detail: { target: targetEl.id, finalY: targetY }
          }));
          window.dispatchEvent(new CustomEvent('firby:agent.navigation.completed', {
            detail: { target: targetEl.id }
          }));
          window.dispatchEvent(new CustomEvent('firby:agent.action.completed', {
            detail: { type: 'navigate_to_section', target: targetEl.id }
          }));
          try {
            if (window.location.hash !== '#' + targetEl.id) {
              history.replaceState(null, '', '#' + targetEl.id);
            }
          } catch (e) {}
        } catch (e) {}
      }
    }

    requestAnimationFrame(step);
  }

  function executeUiAction(action) {
    return new Promise((resolve) => {
      if (!action) {
        return resolve({ success: false, status: 'no_action', error: 'No action provided' });
      }
      const type = action.type;
      const target = action.target || action.route;
      if (!target) {
        return resolve({ success: false, status: 'no_target', error: 'No target specified' });
      }

      try {
        window.dispatchEvent(new CustomEvent('firby:agent.action.started', {
          detail: { action }
        }));
      } catch (e) {}

      if (type === 'navigate_to' || (type === 'navigate' && !target.startsWith('#'))) {
        try {
          window.__firby_navigating = true;
          if (typeof sessionStorage !== 'undefined') {
            sessionStorage.setItem('firby_keep_open', 'true');
            sessionStorage.setItem('firby_pending_nav', JSON.stringify({
              target: target,
              from: window.location.pathname,
              timestamp: Date.now()
            }));
            saveChatHistory();
            const parts = target.split('#');
            if (parts[1]) {
              sessionStorage.setItem('firby_pending_target', '#' + parts[1]);
            }
          }
          if (window.location.pathname !== target.split('#')[0]) {
            const cleanPath = target.split('#')[0];
            const targetName = cleanPath.replace('/', '').replace(/-/g, ' ');
            const capTarget = targetName ? targetName.charAt(0).toUpperCase() + targetName.slice(1) : 'página';
            const navPill = document.createElement('div');
            navPill.className = 'firby-copilot-nav-badge';
            navPill.innerHTML = `<span class="firby-copilot-spinner"></span> Llevándote a ${capTarget}...`;
            streamEl.appendChild(navPill);
            handleAutoScroll(false);

            try {
              window.dispatchEvent(new CustomEvent('firby:agent.navigation.requested', {
                detail: { target, type: 'cross_page' }
              }));
            } catch (e) {}

            document.documentElement.style.transition = 'opacity 0.4s ease';
            setTimeout(() => {
              document.documentElement.style.opacity = '0.7';
            }, 350);

            setTimeout(() => {
              window.location.href = target;
            }, 850);
            return resolve({ success: true, status: 'cross_page_navigation_initiated', target: target });
          } else {
            return resolve({ success: true, status: 'already_on_page', target: target });
          }
        } catch (e) {
          window.location.href = target;
          return resolve({ success: true, status: 'navigated_direct', target: target });
        }
      } else if (type === 'navigate_to_section' || type === 'scroll_to' || (type === 'navigate' && target.startsWith('#'))) {
        try {
          const secSelector = target.startsWith('#') ? target : '#' + target;
          let el = document.querySelector(secSelector) || document.getElementById(target.replace('#', ''));
          if (!el && window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
            executeUiAction({
              type: 'navigate_to',
              target: '/' + target
            }).then(resolve);
            return;
          }

          if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.navigateToElement === 'function') {
            const navDuration = action.duration || (action.params && action.params.duration) || (action.slow ? 2.8 : undefined);
            const navSlow = action.slow || (action.params && action.params.slow) || false;
            window.FirbyMotionEngine.navigateToElement(target, {
              label: action.label,
              duration: navDuration,
              slow: navSlow
            }).then((obs) => {
              const isSuccess = (typeof obs === 'object' && obs !== null) ? !!obs.success : !!obs;
              const obsStatus = (typeof obs === 'object' && obs !== null) ? obs.status : (isSuccess ? 'scroll_completed' : 'target_not_found');

              if (isSuccess) {
                try {
                  const targetClean = String(target).replace('#', '');
                  if (window.location.hash !== '#' + targetClean) {
                    history.replaceState(null, '', '#' + targetClean);
                  }
                } catch (e) {}
              }

              lastNavigationEvent = {
                status: obsStatus,
                target: target,
                timestamp: Date.now(),
                details: (typeof obs === 'object' && obs !== null) ? obs : {}
              };

              if (!isSuccess) {
                try {
                  window.dispatchEvent(new CustomEvent('firby:agent.navigation.failed', {
                    detail: { target, reason: (obs && obs.error) || obsStatus }
                  }));
                  window.dispatchEvent(new CustomEvent('firby:agent.action.failed', {
                    detail: { action, reason: obsStatus }
                  }));
                } catch (e) {}
                return resolve({
                  success: false,
                  status: obsStatus,
                  target: target,
                  target_found: obs && obs.target_found !== undefined ? obs.target_found : false,
                  target_visible: obs && obs.target_visible !== undefined ? obs.target_visible : false,
                  scroll_completed: false,
                  section_id: (obs && obs.section_id) || target,
                  final_scroll_position: (obs && obs.final_scroll_position) || window.pageYOffset || 0,
                  error: (obs && obs.error) || 'Navigation failed or interrupted'
                });
              } else {
                try {
                  window.dispatchEvent(new CustomEvent('firby:agent.action.completed', {
                    detail: { action, status: obsStatus }
                  }));
                  window.dispatchEvent(new CustomEvent('firby:agent.content.verified', {
                    detail: { target, status: 'verified' }
                  }));
                } catch (e) {}
                return resolve({
                  success: true,
                  status: obsStatus,
                  target: target,
                  target_found: obs && obs.target_found !== undefined ? obs.target_found : true,
                  target_visible: obs && obs.target_visible !== undefined ? obs.target_visible : true,
                  scroll_completed: obs && obs.scroll_completed !== undefined ? obs.scroll_completed : true,
                  section_id: (obs && obs.section_id) || target,
                  final_scroll_position: (obs && obs.final_scroll_position) || window.pageYOffset || 0,
                  distance: obs && obs.distance !== undefined ? obs.distance : 0,
                  drift: obs && obs.drift !== undefined ? obs.drift : 0
                });
              }
            });
          } else {
            if (el) {
              premiumSmoothScroll(el);
              lastNavigationEvent = {
                status: 'section_reached',
                target: target,
                timestamp: Date.now()
              };
              try {
                window.dispatchEvent(new CustomEvent('firby:agent.action.completed', {
                  detail: { action, status: 'completed' }
                }));
                window.dispatchEvent(new CustomEvent('firby:agent.content.verified', {
                  detail: { target, status: 'verified' }
                }));
              } catch (e) {}
              return resolve({
                success: true,
                status: 'section_reached',
                target: target
              });
            } else {
              lastNavigationEvent = {
                status: 'section_target_missing',
                target: target,
                timestamp: Date.now()
              };
              try {
                window.dispatchEvent(new CustomEvent('firby:agent.navigation.failed', {
                  detail: { target, reason: 'section_target_not_found' }
                }));
                window.dispatchEvent(new CustomEvent('firby:agent.action.failed', {
                  detail: { action, reason: 'section_target_not_found' }
                }));
                window.dispatchEvent(new CustomEvent('firby:agent.content.failed', {
                  detail: { target, reason: 'section_target_not_found' }
                }));
              } catch (e) {}
              return resolve({
                success: false,
                status: 'section_target_missing',
                target: target,
                error: 'Element not found in DOM'
              });
            }
          }
        } catch (e) {
          console.warn('[Firby Copilot] Navigation error:', e);
          return resolve({ success: false, status: 'navigation_error', target: target, error: String(e) });
        }
      } else if (type === 'highlight') {
        try {
          const el = document.querySelector(target) || document.getElementById(target.replace('#', ''));
          if (el) {
            highlightElement(el);
            window.dispatchEvent(new CustomEvent('firby:agent.highlight.requested', { detail: { target } }));
          }
          return resolve({ success: !!el, status: el ? 'highlighted' : 'not_found', target: target });
        } catch (e) {
          return resolve({ success: false, status: 'error', error: String(e) });
        }
      } else if (type === 'focus_element') {
        try {
          const el = document.querySelector(target) || document.getElementById(target.replace('#', ''));
          if (el && typeof el.focus === 'function') {
            el.focus();
            window.dispatchEvent(new CustomEvent('firby:agent.form.requested', { detail: { target } }));
          }
          return resolve({ success: !!el, status: el ? 'focused' : 'not_found', target: target });
        } catch (e) {
          return resolve({ success: false, status: 'error', error: String(e) });
        }
      } else {
        return resolve({ success: true, status: 'unknown_action_ignored' });
      }
    });
  }

  function highlightElement(el) {
    if (!el) return;
    el.classList.remove('firby-copilot-highlight');
    void el.offsetWidth;
    el.classList.add('firby-copilot-highlight');
    setTimeout(() => {
      el.classList.remove('firby-copilot-highlight');
    }, 3800);
  }

  // ── Visión en Tiempo Real: Detección Continua de Sección Activa ──
  let currentActiveSection = '#hero';
  const trackedSections = [
    'hero', 'problema', 'sub-costo-oculto', 'como-funciona',
    'sobre-nosotros', 'equipo-digital', 'canales',
    'seguridad-cumplimiento', 'planes', 'experiencia-conversacional', 'contacto'
  ];

  try {
    if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
      const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
            currentActiveSection = '#' + entry.target.id;
          }
        });
      }, { threshold: [0.2, 0.5] });

      trackedSections.forEach(id => {
        const el = document.getElementById(id);
        if (el) sectionObserver.observe(el);
      });
    }
  } catch (e) {}

  // ── Ciclo de Vida del Agente: Máquina de Estados Estricta (Bloque 1) ──
  const AgentClientState = {
    IDLE: 'IDLE',
    MESSAGE_RECEIVED: 'MESSAGE_RECEIVED',
    THINKING: 'THINKING',
    DECIDING: 'DECIDING',
    ACTION_REQUESTED: 'ACTION_REQUESTED',
    ACTION_STARTED: 'ACTION_STARTED',
    ACTION_COMPLETED: 'ACTION_COMPLETED',
    ACTION_FAILED: 'ACTION_FAILED',
    VERIFYING: 'VERIFYING',
    RESPONDING: 'RESPONDING',
    DONE: 'DONE',
    ERROR: 'ERROR'
  };
  let currentAgentState = AgentClientState.IDLE;

  // ── Cola FIFO de Turnos Conversacionales (Garantía de Orden Estricto) ──
  let isTurnInFlight = false;
  const turnQueue = [];

  async function processTurnQueue() {
    if (isTurnInFlight || turnQueue.length === 0) return;
    isTurnInFlight = true;
    const nextTurn = turnQueue.shift();
    try {
      await executeTurn(nextTurn.text, nextTurn.attachment, nextTurn.runId);
    } catch (err) {
      console.error('[Firby Copilot] Error en executeTurn:', err);
    } finally {
      isTurnInFlight = false;
      if (turnQueue.length > 0) {
        processTurnQueue();
      }
    }
  }

  async function sendMessage(text, attachment = null) {
    if ((!text || !text.trim()) && !attachment) return;
    if (consentContainer) consentContainer.style.display = 'none';

    // Generar Run ID único para este ciclo de ejecución
    const runId = 'run_' + Math.random().toString(36).substring(2, 11) + Date.now().toString(36);

    // 0. Renderizar mensaje del usuario inmediatamente en el chat
    appendMessage(text, true, attachment);
    updateSuggestionsDock([]);

    // Encolar y procesar con garantía secuencial FIFO
    turnQueue.push({ text, attachment, runId });
    processTurnQueue();
  }

  async function executeTurn(text, attachment, runId) {
    currentAgentState = AgentClientState.MESSAGE_RECEIVED;
    try {
      window.dispatchEvent(new CustomEvent('firby:agent.message.received', {
        detail: { run_id: runId, query: text }
      }));
    } catch (e) {}

    // 1. Mostrar estado Thinking y emitir evento formal (sin mover la página)
    currentAgentState = AgentClientState.THINKING;
    try {
      window.dispatchEvent(new CustomEvent('firby:agent.thinking.started', {
        detail: { run_id: runId }
      }));
    } catch (e) {}

    showTyping();

    try {
      const payloadText = text || (attachment ? `[Archivo adjunto: ${attachment.name}]` : '');
      const endpoint = `${API_HOST}/api/widget/chat`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          run_id: runId,
          message: payloadText,
          audio_base64: attachment && attachment.audioBase64 ? attachment.audioBase64 : undefined,
          audio_mime: attachment && attachment.mimeType ? attachment.mimeType : undefined,
          client_transcript: attachment && attachment.transcript ? attachment.transcript : undefined,
          attachment_name: attachment ? attachment.name : undefined,
          session_id: sessionId,
          org_id: ORG_ID,
          web_context: {
            run_id: runId,
            current_url: window.location.pathname + window.location.hash,
            current_section: currentActiveSection,
            current_scroll_y: window.pageYOffset || document.documentElement.scrollTop,
            viewport_height: window.innerHeight,
            viewport_width: window.innerWidth,
            page_title: document.title,
            available_sections: trackedSections.map(s => '#' + s),
            last_navigation_event: lastNavigationEvent
          }
        })
      });

      if (!res.ok) {
        hideTyping();
        currentAgentState = AgentClientState.ERROR;
        try {
          window.dispatchEvent(new CustomEvent('firby:agent.run.failed', { detail: { run_id: runId } }));
        } catch (e) {}
        appendMessage('Hubo un problema temporal al procesar la solicitud. Por favor intenta de nuevo.', false);
        return;
      }

      const data = await res.json();

      if (data.transcribed_audio && attachment && attachment.isAudio && streamEl) {
        try {
          const userBubbles = streamEl.querySelectorAll('.firby-msg-user');
          if (userBubbles.length > 0) {
            const lastUserBubble = userBubbles[userBubbles.length - 1];
            let transEl = lastUserBubble.querySelector('.firby-audio-transcript');
            if (!transEl) {
              transEl = document.createElement('div');
              transEl.className = 'firby-audio-transcript';
              transEl.style.fontSize = '12px';
              transEl.style.lineHeight = '1.4';
              transEl.style.opacity = '0.9';
              transEl.style.marginTop = '6px';
              transEl.style.padding = '4px 8px';
              transEl.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
              transEl.style.borderRadius = '6px';
              transEl.style.borderLeft = '2px solid #b9fa01';
              lastUserBubble.appendChild(transEl);
            }
            transEl.textContent = `"${data.transcribed_audio}"`;
          }
        } catch (_) {}
      }

      // ── PROTOCOLO DE DOS FASES: Agent Runtime <-> Agent Surface ──
      if (data.state === 'ACTION_REQUESTED' && (data.action || data.ui_action)) {
        const actionToExecute = data.action || data.ui_action;
        currentAgentState = AgentClientState.ACTION_REQUESTED;

        try {
          window.dispatchEvent(new CustomEvent('firby:agent.action.requested', {
            detail: {
              run_id: data.run_id || runId,
              action: actionToExecute,
              step_id: data.step_id || 1,
              requires_verification: true
            }
          }));
        } catch (e) {}

        // Iniciar ejecución de acción en la UI mientras el orbe mantiene retroalimentación
        currentAgentState = AgentClientState.ACTION_STARTED;
        const obsResult = await executeUiAction(actionToExecute);

        // Crear reporte formal de observación
        currentAgentState = obsResult.success ? AgentClientState.ACTION_COMPLETED : AgentClientState.ACTION_FAILED;
        const observationPayload = {
          run_id: data.run_id || runId,
          step_id: data.step_id || 1,
          status: obsResult.status,
          target: obsResult.target,
          success: obsResult.success,
          target_found: obsResult.target_found !== undefined ? obsResult.target_found : obsResult.success,
          target_visible: obsResult.target_visible !== undefined ? obsResult.target_visible : obsResult.success,
          scroll_completed: obsResult.scroll_completed !== undefined ? obsResult.scroll_completed : obsResult.success,
          section_id: obsResult.section_id || obsResult.target,
          final_scroll_position: obsResult.final_scroll_position !== undefined ? obsResult.final_scroll_position : (window.pageYOffset || 0),
          error: obsResult.error
        };

        try {
          window.dispatchEvent(new CustomEvent('firby:agent.observation.created', {
            detail: observationPayload
          }));
        } catch (e) {}

        // Enviar observación al runtime para verificación y replanificación
        currentAgentState = AgentClientState.VERIFYING;
        try {
          window.dispatchEvent(new CustomEvent('firby:agent.verification.started', {
            detail: { run_id: data.run_id || runId }
          }));
        } catch (e) {}

        const verifyRes = await fetch(`${API_HOST}/api/widget/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            run_id: data.run_id || runId,
            step_id: data.step_id || 1,
            observation: observationPayload,
            session_id: sessionId,
            org_id: ORG_ID
          })
        });

        hideTyping();

        if (verifyRes.ok) {
          const verifiedData = await verifyRes.json();
          currentAgentState = AgentClientState.RESPONDING;

          try {
            window.dispatchEvent(new CustomEvent('firby:agent.verification.completed', {
              detail: {
                run_id: verifiedData.run_id || runId,
                status: obsResult.success ? 'verified' : 'replanned'
              }
            }));
            window.dispatchEvent(new CustomEvent('firby:agent.response.created', {
              detail: { run_id: verifiedData.run_id || runId }
            }));
          } catch (e) {}

          // Renderizar respuesta verificada
          let voiceText = '';
          if (verifiedData.bubbles && verifiedData.bubbles.length > 0) {
            voiceText = verifiedData.bubbles.join('\n\n');
            appendMessage(voiceText, false);
          } else if (verifiedData.response) {
            voiceText = verifiedData.response;
            appendMessage(voiceText, false);
          }

          if (attachment && attachment.isAudio && voiceText) {
            playFirbyVoice(voiceText);
          }

          if (verifiedData.intent === 'terms_consent') {
            try { localStorage.setItem('firby_privacy_accepted', 'true'); } catch (_) {}
            const initConsent = document.getElementById('firby-consent-container');
            if (initConsent) initConsent.style.display = 'none';
          } else if (verifiedData.intent === 'terms_required' || verifiedData.intent === 'terms_rejected') {
            try { localStorage.removeItem('firby_privacy_accepted'); } catch (_) {}
          }

          if (verifiedData.action_card) {
            appendActionCard(verifiedData.action_card);
          }

          if ((verifiedData.action_chips && verifiedData.action_chips.length > 0) || (verifiedData.chips && verifiedData.chips.length > 0)) {
            updateSuggestionsDock(verifiedData.chips || [], verifiedData.action_chips || []);
          } else {
            updateSuggestionsDock([]);
          }

          currentAgentState = AgentClientState.DONE;
          try {
            window.dispatchEvent(new CustomEvent('firby:agent.run.completed', {
              detail: { run_id: verifiedData.run_id || runId }
            }));
          } catch (e) {}
        } else {
          currentAgentState = AgentClientState.ERROR;
          appendMessage('No fue posible completar la verificación de la acción.', false);
        }
      } else {
        // ── FLUJO SIN ACCIÓN DE INTERFAZ O CON ACCIÓN DIRECTA ──
        if (data.ui_action || data.action) {
          try {
            executeUiAction(data.ui_action || data.action);
          } catch (e) {}
        }
        hideTyping();
        currentAgentState = AgentClientState.RESPONDING;

        try {
          window.dispatchEvent(new CustomEvent('firby:agent.response.created', {
            detail: { run_id: data.run_id || runId }
          }));
        } catch (e) {}

        let voiceText = '';
        if (data.bubbles && data.bubbles.length > 0) {
          voiceText = data.bubbles.join('\n\n');
          appendMessage(voiceText, false);
        } else if (data.response) {
          voiceText = data.response;
          appendMessage(voiceText, false);
        } else {
          voiceText = 'Acción procesada con éxito.';
          appendMessage(voiceText, false);
        }

        if (attachment && attachment.isAudio && voiceText) {
          playFirbyVoice(voiceText);
        }

        if (data.intent === 'terms_consent') {
          try { localStorage.setItem('firby_privacy_accepted', 'true'); } catch (_) {}
          const initConsent = document.getElementById('firby-consent-container');
          if (initConsent) initConsent.style.display = 'none';
        } else if (data.intent === 'terms_required' || data.intent === 'terms_rejected') {
          try { localStorage.removeItem('firby_privacy_accepted'); } catch (_) {}
        }

        if (data.action_card) {
          appendActionCard(data.action_card);
        }

        if ((data.action_chips && data.action_chips.length > 0) || (data.chips && data.chips.length > 0)) {
          updateSuggestionsDock(data.chips || [], data.action_chips || []);
        } else {
          updateSuggestionsDock([]);
        }

        currentAgentState = AgentClientState.DONE;
        try {
          window.dispatchEvent(new CustomEvent('firby:agent.run.completed', {
            detail: { run_id: data.run_id || runId }
          }));
        } catch (e) {}
      }

    } catch (err) {
      hideTyping();
      currentAgentState = AgentClientState.ERROR;
      if (window.__firby_navigating || (err && (err.name === 'AbortError' || err.message === 'Failed to fetch' && document.hidden))) {
        console.info('[Firby Copilot] Navegación en curso o solicitud abortada; omitiendo alerta de error.');
        return;
      }
      appendMessage('No se pudo conectar con el servicio. Por favor verifica tu conexión.', false);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // ═══════════════════════════════════════════════════════════════════════════
  // MANEJO DE ARCHIVOS ADJUNTOS (DISEÑO ELEGANTE Y COMPACTO)
  // ═══════════════════════════════════════════════════════════════════════════
  function closeEmojiPopover() {}

  // Manejo de Adjuntos (Archivos)
  let currentAttachment = null;

  if (attachBtn && fileInput) {
    attachBtn.addEventListener('click', (e) => {
      e.preventDefault();
      fileInput.click();
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        currentAttachment = fileInput.files[0];
        if (attachmentBar && attachmentName) {
          attachmentName.textContent = currentAttachment.name;
          attachmentBar.style.display = 'flex';
        }
        attachBtn.classList.add('has-attachment');
        if (inputEl) inputEl.focus();
      }
    });
  }

  if (attachmentRemoveBtn) {
    attachmentRemoveBtn.addEventListener('click', (e) => {
      e.preventDefault();
      currentAttachment = null;
      if (fileInput) fileInput.value = '';
      if (attachmentBar) attachmentBar.style.display = 'none';
      if (attachBtn) attachBtn.classList.remove('has-attachment');
      if (inputEl) inputEl.focus();
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // ═══════════════════════════════════════════════════════════════════════════
  // AUDIO / VOICE RECORDING ENGINE (DUAL-MODE: PUSH-TO-TALK + TAP-TO-TALK)
  // ═══════════════════════════════════════════════════════════════════════════
  let mediaRecorder = null;
  let activeAudioStream = null;
  let audioChunks = [];
  let isRecordingAudio = false;
  let isStartingRecording = false;
  let recordingTimerInterval = null;
  let recordingSeconds = 0;
  let pointerPressStartTime = 0;
  let isPointerHeld = false;

  function formatDuration(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function resetAudioRecordingUI() {
    isRecordingAudio = false;
    isStartingRecording = false;
    isPointerHeld = false;
    pointerPressStartTime = 0;
    clearInterval(recordingTimerInterval);
    recordingSeconds = 0;
    audioChunks = [];
    if (activeAudioStream) {
      try { activeAudioStream.getTracks().forEach(t => t.stop()); } catch (_) {}
      activeAudioStream = null;
    }
    if (voiceBtn) {
      voiceBtn.classList.remove('recording');
      voiceBtn.classList.remove('holding');
      voiceBtn.setAttribute('title', 'Grabar mensaje de voz (mantén o toca)');
    }
    if (voiceBtnIcon) voiceBtnIcon.style.display = 'block';
    if (voiceActiveWaves) voiceActiveWaves.style.display = 'none';
    if (voiceRecordingOverlay) voiceRecordingOverlay.style.display = 'none';
    if (inputEl) inputEl.style.display = 'block';
  }

  async function startAudioRecording() {
    if (isRecordingAudio || isStartingRecording) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert('Tu navegador no soporta grabación de audio.');
      return;
    }

    isStartingRecording = true;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // Si el usuario canceló mientras pedíamos permiso
      if (!isStartingRecording && !isPointerHeld && !isRecordingAudio) {
        stream.getTracks().forEach(t => t.stop());
        return;
      }

      activeAudioStream = stream;
      audioChunks = [];
      recordingSeconds = 0;

      let mimeType = 'audio/webm';
      let options = {};
      if (window.MediaRecorder) {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          mimeType = 'audio/webm;codecs=opus';
          options = { mimeType };
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          mimeType = 'audio/webm';
          options = { mimeType };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
          options = { mimeType };
        } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
          mimeType = 'audio/ogg;codecs=opus';
          options = { mimeType };
        }
      }

      mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.start(100);
      isRecordingAudio = true;
      isStartingRecording = false;

      // Actualizar UI de grabación
      if (voiceBtn) {
        voiceBtn.classList.add('recording');
        voiceBtn.setAttribute('title', 'Toca para enviar mensaje de voz');
      }
      if (voiceBtnIcon) voiceBtnIcon.style.display = 'none';
      if (voiceActiveWaves) voiceActiveWaves.style.display = 'flex';
      if (inputEl) inputEl.style.display = 'none';
      if (voiceRecordingOverlay) voiceRecordingOverlay.style.display = 'flex';
      if (voiceRecTimer) voiceRecTimer.textContent = '0:00';

      clearInterval(recordingTimerInterval);
      recordingTimerInterval = setInterval(() => {
        recordingSeconds++;
        if (voiceRecTimer) {
          voiceRecTimer.textContent = formatDuration(recordingSeconds);
        }
        if (recordingSeconds >= 90) {
          stopAndSendAudioRecording();
        }
      }, 1000);

    } catch (err) {
      console.warn('[Firby Audio] Error accediendo al micrófono:', err);
      isStartingRecording = false;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        alert('Por favor habilita el permiso de micrófono en tu navegador para enviar notas de voz.');
      } else {
        alert('No se pudo acceder al micrófono. Por favor verifica los permisos.');
      }
      resetAudioRecordingUI();
    }
  }

  function cancelAudioRecording() {
    isStartingRecording = false;
    isPointerHeld = false;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try {
        mediaRecorder.onstop = null;
        mediaRecorder.stop();
      } catch (_) {}
    }
    resetAudioRecordingUI();
  }

  function blobToBase64(blob) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result || '';
        const commaIdx = dataUrl.indexOf(',');
        resolve(commaIdx !== -1 ? dataUrl.slice(commaIdx + 1) : dataUrl);
      };
      reader.onerror = () => resolve('');
      reader.readAsDataURL(blob);
    });
  }

  async function stopAndSendAudioRecording() {
    if (!isRecordingAudio && !isStartingRecording) return;

    // Si aún está inicializando el stream de micrófono, esperar brevemente
    if (isStartingRecording && !mediaRecorder) {
      let waitCount = 0;
      while (isStartingRecording && !mediaRecorder && waitCount < 8) {
        await new Promise(r => setTimeout(r, 50));
        waitCount++;
      }
    }

    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
      resetAudioRecordingUI();
      return;
    }

    const recordedDuration = formatDuration(recordingSeconds || 1);

    // Detener de forma asíncrona garantizando que todos los chunks lleguen
    const recordedBlob = await new Promise((resolve) => {
      mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder.mimeType || 'audio/webm';
        const blob = new Blob(audioChunks, { type: mimeType });
        resolve(blob);
      };
      try {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.requestData();
        }
        mediaRecorder.stop();
      } catch (e) {
        resolve(null);
      }
    });

    if (activeAudioStream) {
      try {
        activeAudioStream.getTracks().forEach(t => t.stop());
        activeAudioStream = null;
      } catch (_) {}
    }

    if (!recordedBlob || recordedBlob.size < 600) {
      // Audio demasiado corto o vacío (ej. click accidental de 0.1s)
      console.warn('[Firby Audio] Audio descartado por ser demasiado corto o vacío:', recordedBlob ? recordedBlob.size : 0);
      resetAudioRecordingUI();
      if (inputEl) {
        const oldPh = inputEl.placeholder;
        inputEl.placeholder = 'Mantén presionado para hablar o toca para grabar';
        setTimeout(() => { if (inputEl) inputEl.placeholder = oldPh; }, 2600);
      }
      return;
    }

    const mimeType = recordedBlob.type || 'audio/webm';
    const audioUrl = URL.createObjectURL(recordedBlob);
    const audioBase64 = await blobToBase64(recordedBlob);

    const sendText = `Mensaje de voz (${recordedDuration})`;

    const audioAttachment = {
      name: `nota_de_voz_${Date.now()}.${mimeType.includes('mp4') ? 'mp4' : 'webm'}`,
      url: audioUrl,
      duration: recordedDuration,
      isAudio: true,
      audioBase64: audioBase64,
      mimeType: mimeType
    };

    resetAudioRecordingUI();
    sendMessage(sendText, audioAttachment);
  }

  if (voiceBtn) {
    // 1. Soporte Push-To-Talk (Presionar y mantener)
    voiceBtn.addEventListener('pointerdown', (e) => {
      if (e.button !== undefined && e.button !== 0) return;
      e.preventDefault();
      unlockAudioPlayback();
      
      pointerPressStartTime = Date.now();
      isPointerHeld = true;

      if (!isRecordingAudio) {
        startAudioRecording();
      }
    });

    // 2. Liberación global del puntero (Soltar para enviar en modo Push-To-Talk)
    window.addEventListener('pointerup', (e) => {
      if (!isPointerHeld) return;
      isPointerHeld = false;
      const holdDuration = Date.now() - pointerPressStartTime;

      if (holdDuration >= 600) {
        // Estilo Push-To-Talk: soltó después de hablar -> ENVIAR
        stopAndSendAudioRecording();
      } else {
        // Estilo Tap-To-Talk: fue un toque corto -> Mantener grabando
      }
    });

    window.addEventListener('pointercancel', () => {
      if (isPointerHeld) {
        isPointerHeld = false;
        cancelAudioRecording();
      }
    });

    // 3. Soporte Tap-To-Talk (Clic normal / Segundo clic para enviar)
    voiceBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const clickDuration = Date.now() - pointerPressStartTime;

      // Si ya estuvo presionado por más de 500ms, pointerup ya lo procesó
      if (clickDuration > 500 && !isRecordingAudio) {
        return;
      }

      if (isRecordingAudio) {
        // Segundo clic: enviar la grabación en curso
        stopAndSendAudioRecording();
      }
    });
  }

  if (voiceCancelBtn) {
    voiceCancelBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      cancelAudioRecording();
    });
  }

  inputForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (isRecordingAudio) {
      stopAndSendAudioRecording();
      return;
    }
    const val = inputEl.value.trim();
    const att = currentAttachment;
    if (!val && !att) return;
    
    inputEl.value = '';
    closeEmojiPopover();
    updateSendButtonState();

    if (att) {
      currentAttachment = null;
      if (fileInput) fileInput.value = '';
      if (attachmentBar) attachmentBar.style.display = 'none';
      if (attachBtn) attachBtn.classList.remove('has-attachment');
      updateSendButtonState();
    }

    sendMessage(val, att);
  });

  // ── DUAL STATE SEND / FLOW PREMIUM LIVE VOICE BUTTON (ESTILO CHATGPT / GEMINI) ──
  function updateSendButtonState() {
    if (!sendBtn || !inputEl) return;
    const hasText = inputEl.value.trim().length > 0 || Boolean(currentAttachment);
    if (hasText) {
      sendBtn.classList.remove('firby-flow-mode');
      sendBtn.setAttribute('type', 'submit');
      sendBtn.setAttribute('title', 'Enviar mensaje');
      sendBtn.setAttribute('aria-label', 'Enviar mensaje');
    } else {
      sendBtn.classList.add('firby-flow-mode');
      sendBtn.setAttribute('type', 'button');
      sendBtn.setAttribute('title', 'Modo voz en vivo (1 a 1)');
      sendBtn.setAttribute('aria-label', 'Modo voz en vivo (1 a 1)');
    }
  }

  inputEl.addEventListener('input', updateSendButtonState);
  updateSendButtonState();

  if (sendBtn) {
    sendBtn.addEventListener('click', (e) => {
      if (sendBtn.classList.contains('firby-flow-mode')) {
        e.preventDefault();
        e.stopPropagation();
        openLiveVoiceMode();
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // INTEGRATED AGENT SURFACE, SMART SCROLL PILL & MOBILE TOUCH GESTURES
  // ═══════════════════════════════════════════════════════════════════════════

  function humanizeSection(target) {
    if (!target) return 'Navegando';
    const clean = String(target).replace(/^[#/]+/, '').toLowerCase();
    const map = {
      'planes': 'Mostrando planes y precios',
      'pricing': 'Mostrando planes y precios',
      'precios': 'Mostrando planes y precios',
      'como-funciona': 'Mostrando cómo funciona',
      'how-it-works': 'Mostrando cómo funciona',
      'seguridad-cumplimiento': 'Mostrando seguridad',
      'seguridad': 'Mostrando seguridad',
      'security': 'Mostrando seguridad',
      'canales': 'Mostrando canales de atención',
      'channels': 'Mostrando canales de atención',
      'faq': 'Mostrando preguntas frecuentes',
      'preguntas': 'Mostrando preguntas frecuentes',
      'sobre-nosotros': 'Abriendo Sobre Nosotros',
      'about': 'Abriendo Sobre Nosotros',
      'hero': 'Mostrando inicio'
    };
    if (map[clean]) return map[clean];
    const readable = clean.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return 'Mostrando ' + readable;
  }

  function humanizeSuccess(target) {
    if (!target) return 'Listo';
    const clean = String(target).replace(/^[#/]+/, '').toLowerCase();
    const map = {
      'planes': 'Planes y precios',
      'pricing': 'Planes y precios',
      'precios': 'Planes y precios',
      'como-funciona': 'Cómo funciona',
      'how-it-works': 'Cómo funciona',
      'seguridad-cumplimiento': 'Seguridad y cumplimiento',
      'seguridad': 'Seguridad',
      'security': 'Seguridad',
      'canales': 'Canales de atención',
      'channels': 'Canales de atención',
      'faq': 'Preguntas frecuentes',
      'preguntas': 'Preguntas frecuentes',
      'sobre-nosotros': 'Sobre Nosotros',
      'hero': 'Inicio'
    };
    if (map[clean]) return map[clean];
    return clean.replace(/[-_]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  let activityFadeTimer = null;

  function showActivityBar(text) {
    if (!activityBar || !activityText) return;
    if (activityFadeTimer) {
      clearTimeout(activityFadeTimer);
      activityFadeTimer = null;
    }
    activityText.textContent = text;
    activityBar.classList.add('active');
  }

  function hideActivityBar(delayMs = 0) {
    if (!activityBar) return;
    if (activityFadeTimer) {
      clearTimeout(activityFadeTimer);
      activityFadeTimer = null;
    }
    if (delayMs > 0) {
      activityFadeTimer = setTimeout(() => {
        if (activityBar) activityBar.classList.remove('active');
      }, delayMs);
    } else {
      activityBar.classList.remove('active');
    }
  }

  function setupIntegratedActivityBar() {
    window.addEventListener('firby:agent.navigation.requested', (e) => {
      const detail = e.detail || {};
      const msg = detail.label || humanizeSection(detail.target);
      showActivityBar(msg);
    });

    window.addEventListener('firby:agent.section.reached', (e) => {
      const detail = e.detail || {};
      const successTitle = humanizeSuccess(detail.target);
      if (activityText) {
        activityText.textContent = successTitle;
      }
      hideActivityBar(1200);
    });

    window.addEventListener('firby:agent.navigation.cancelled', () => {
      hideActivityBar(0);
    });

    window.addEventListener('firby:agent.navigation.failed', () => {
      if (activityText) {
        activityText.textContent = 'Sección no disponible';
      }
      hideActivityBar(1500);
    });

    if (activityCancelBtn) {
      activityCancelBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.cancelNavigation === 'function') {
          window.FirbyMotionEngine.cancelNavigation('user_chat_cancel');
        }
        hideActivityBar(0);
      });
    }
  }

  function setupScrollBottomPill() {
    if (streamEl) {
      streamEl.addEventListener('scroll', () => {
        if (isUserNearBottom() && scrollBottomPill) {
          scrollBottomPill.classList.remove('visible');
        }
      }, { passive: true });
    }

    if (scrollBottomPill) {
      scrollBottomPill.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        scrollToBottom(true);
      });
    }
  }

  function resetMobileViewportStyles() {
    if (!windowEl) return;
    windowEl.style.height = '';
    windowEl.style.top = '';
    windowEl.style.bottom = '';
    windowEl.style.maxHeight = '';
    windowEl.style.transform = '';
  }

  function syncMobileViewport() {
    if (!isOpen || !windowEl) return;
    if (window.innerWidth <= 768 && window.visualViewport) {
      const vv = window.visualViewport;
      const isKeyboardOpen = vv.height < (window.innerHeight - 80);
      if (isKeyboardOpen) {
        const targetHeight = Math.max(260, Math.floor(vv.height - 14));
        windowEl.style.height = `${targetHeight}px`;
        windowEl.style.maxHeight = `${targetHeight}px`;
        windowEl.style.top = `${Math.floor(vv.offsetTop + 6)}px`;
        windowEl.style.bottom = 'auto';
        windowEl.style.transform = 'none';
        scrollToBottom(false);
      } else {
        resetMobileViewportStyles();
      }
    }
  }

  function setupMobileViewportSync() {
    if (typeof window !== 'undefined' && window.visualViewport) {
      window.visualViewport.addEventListener('resize', syncMobileViewport);
      window.visualViewport.addEventListener('scroll', syncMobileViewport);
    }
  }

  function setupMobileSwipeToDismiss() {
    const handle = dragHandle || document.getElementById('firby-mobile-drag-handle');
    const header = document.querySelector('.firby-chat-header');
    const touchTargets = [handle, header].filter(Boolean);

    let touchStartY = 0;
    let touchCurrentY = 0;
    let isDragging = false;

    function onTouchStart(e) {
      if (window.innerWidth > 768) return;
      if (e.target.closest('button') || e.target.closest('a')) return;

      const touch = e.touches[0];
      touchStartY = touch.clientY;
      touchCurrentY = touchStartY;
      isDragging = true;
      if (windowEl) windowEl.style.transition = 'none';
    }

    function onTouchMove(e) {
      if (!isDragging || !windowEl) return;
      const touch = e.touches[0];
      touchCurrentY = touch.clientY;
      const deltaY = touchCurrentY - touchStartY;

      if (deltaY > 0) {
        const damped = Math.pow(deltaY, 0.88);
        windowEl.style.transform = `translateY(${damped}px)`;
        if (e.cancelable) e.preventDefault();
      } else {
        windowEl.style.transform = `translateY(${deltaY * 0.15}px)`;
      }
    }

    function onTouchEnd() {
      if (!isDragging || !windowEl) return;
      isDragging = false;
      const deltaY = touchCurrentY - touchStartY;

      windowEl.style.transition = 'transform 0.28s cubic-bezier(0.16, 1, 0.3, 1)';

      if (deltaY > 80) {
        windowEl.style.transform = 'translateY(100%)';
        setTimeout(() => {
          closeChat();
          if (windowEl) {
            windowEl.style.transform = '';
            windowEl.style.transition = '';
          }
        }, 260);
      } else {
        windowEl.style.transform = '';
        setTimeout(() => {
          if (windowEl) windowEl.style.transition = '';
        }, 280);
      }
    }

    touchTargets.forEach(target => {
      target.addEventListener('touchstart', onTouchStart, { passive: true });
      target.addEventListener('touchmove', onTouchMove, { passive: false });
      target.addEventListener('touchend', onTouchEnd, { passive: true });
      target.addEventListener('touchcancel', onTouchEnd, { passive: true });
    });
  }

  // Inicializar Subsistemas del Chat
  setupIntegratedActivityBar();
  setupScrollBottomPill();
  setupMobileViewportSync();
  setupMobileSwipeToDismiss();

  // ── Copilot Transition: Restaurar historial y mantener widget abierto entre cambios de página ──
  try {
    if (typeof sessionStorage !== 'undefined') {
      const savedHistory = sessionStorage.getItem('firby_chat_history');
      if (savedHistory) {
        try {
          const parsed = JSON.parse(savedHistory);
          if (Array.isArray(parsed) && parsed.length > 0) {
            chatHistoryState = parsed;
            // Ocultar banner inicial de política si ya hay conversación activa
            const policyRow = document.getElementById('firby-initial-policy-row');
            if (policyRow) policyRow.style.display = 'none';

            // Restaurar mensajes en el stream sin duplicar en storage
            parsed.forEach(item => {
              if (item.type === 'message') {
                renderMessageDOM(item.text, item.isUser, item.attachment);
              } else if (item.type === 'card' && item.card) {
                appendActionCard(item.card, true);
              }
            });
            streamEl.scrollTop = streamEl.scrollHeight;
          }
        } catch (errHistory) {
          console.warn('[Firby Copilot] Error parseando historial guardado:', errHistory);
        }
      }

      if (sessionStorage.getItem('firby_keep_open') === 'true') {
        setTimeout(() => {
          openChat();
        }, 180);
      }

      // Post-navegación: Verificación de ruta y contenido (Copiloto)
      const pendingNav = sessionStorage.getItem('firby_pending_nav');
      if (pendingNav) {
        sessionStorage.removeItem('firby_pending_nav');
        try {
          const navData = JSON.parse(pendingNav);
          const target = navData.target || '';
          const targetPath = target.split('#')[0];
          const curPath = window.location.pathname;
          const routeMatches = !targetPath || curPath === targetPath || (targetPath === '/' && (curPath === '/' || curPath === '/index.html'));
          if (routeMatches) {
            window.dispatchEvent(new CustomEvent('firby:agent.content.verified', {
              detail: { target, status: 'verified', crossPage: true }
            }));
          } else {
            window.dispatchEvent(new CustomEvent('firby:agent.content.failed', {
              detail: { target, reason: 'route_mismatch', crossPage: true }
            }));
          }
        } catch (eNav) {}
      }

      // Si hubo una navegación asistida hacia un ancla específica programada por el agente
      const pendingTarget = sessionStorage.getItem('firby_pending_target');
      if (pendingTarget) {
        sessionStorage.removeItem('firby_pending_target');
        setTimeout(() => {
          if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.navigateToElement === 'function') {
            window.FirbyMotionEngine.navigateToElement(pendingTarget).then(found => {
              if (found) {
                window.dispatchEvent(new CustomEvent('firby:agent.content.verified', {
                  detail: { target: pendingTarget, status: 'verified' }
                }));
              } else {
                window.dispatchEvent(new CustomEvent('firby:agent.content.failed', {
                  detail: { target: pendingTarget, reason: 'anchor_target_not_found' }
                }));
              }
            });
          }
        }, 550);
      }
    }
  } catch (e) {}

})();
