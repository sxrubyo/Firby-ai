/**
 * Firby AI - Universal Autonomous Operator Embed SDK (v2.0)
 * ==========================================================
 * Benchmark: Sierra AI / Decagon AI / Stripe Elements
 * 
 * 1-Click Universal Installation for any website (WordPress, Shopify, Webflow, React, HTML).
 * Uses Shadow DOM to guarantee 100% style isolation (zero CSS collisions with client sites).
 * 
 * Usage:
 * <script 
 *   src="https://dev.firbyai.com/firby-embed.js" 
 *   data-firby-id="default" 
 *   async>
 * </script>
 */

(function() {
  'use strict';

  // Evitar doble inyección si el script ya fue cargado
  if (window.__FIRBY_EMBED_INITIALIZED__) return;
  window.__FIRBY_EMBED_INITIALIZED__ = true;

  // 1. Detectar script y atributos
  const currentScript = document.currentScript || (function() {
    const scripts = document.getElementsByTagName('script');
    for (let i = scripts.length - 1; i >= 0; i--) {
      if (scripts[i].src && scripts[i].src.indexOf('firby-embed.js') !== -1) {
        return scripts[i];
      }
    }
    return scripts[scripts.length - 1];
  })();

  const scriptSrc = currentScript ? currentScript.src : '';
  let hostUrl = 'https://dev.firbyai.com';
  try {
    if (scriptSrc) {
      const parsed = new URL(scriptSrc);
      hostUrl = parsed.origin;
    }
  } catch (e) {}

  const ORG_ID = (currentScript && currentScript.getAttribute('data-firby-id')) || 'default';
  const PRIMARY_COLOR = (currentScript && currentScript.getAttribute('data-primary-color')) || '#00825a';
  const POSITION = (currentScript && currentScript.getAttribute('data-position')) || 'right';

  // Cargar dependencias de presencia y scroll cinemático si no existen en la página anfitriona
  if (typeof window !== 'undefined') {
    if (!window.FirbyScrollDirector) {
      const s = document.createElement('script');
      s.src = `${hostUrl}/firby-scroll-director.js`;
      s.async = true;
      document.head.appendChild(s);
    }
    if (!window.FirbyAgentSurface) {
      const s2 = document.createElement('script');
      s2.src = `${hostUrl}/firby-agent-surface.js`;
      s2.async = true;
      document.head.appendChild(s2);
    }
  }

  // 2. Crear Custom Element Host
  const hostElement = document.createElement('firby-operator-root');
  hostElement.style.cssText = 'position: fixed; z-index: 2147483647; bottom: 0; right: 0; pointer-events: none;';
  document.body.appendChild(hostElement);

  // 3. Inicializar Shadow DOM (Aislamiento Total de CSS)
  const shadow = hostElement.attachShadow({ mode: 'open' });

  // 4. Inyectar Estilos Encapsulados
  const style = document.createElement('style');
  style.textContent = `
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    .firby-wrapper {
      position: fixed;
      bottom: 24px;
      ${POSITION === 'left' ? 'left: 24px;' : 'right: 24px;'}
      pointer-events: auto;
      display: flex;
      flex-direction: column;
      align-items: ${POSITION === 'left' ? 'flex-start' : 'flex-end'};
      z-index: 2147483647;
    }

    /* Launcher Button 2D */
    .firby-launcher {
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: #09090b;
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
      position: relative;
      user-select: none;
    }

    .firby-launcher:hover {
      transform: scale(1.05);
      box-shadow: 0 14px 28px -4px rgba(0, 0, 0, 0.4);
    }

    .firby-launcher:active {
      transform: scale(0.96);
    }

    .firby-launcher-icon {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      transition: transform 0.25s ease, opacity 0.2s ease;
    }

    .firby-badge-pulse {
      position: absolute;
      top: -2px;
      right: -2px;
      width: 14px;
      height: 14px;
      background: #10b981;
      border: 2px solid #09090b;
      border-radius: 50%;
    }

    /* Chat Window Container */
    .firby-window {
      width: 380px;
      max-width: calc(100vw - 32px);
      height: 580px;
      max-height: calc(100vh - 100px);
      background: #ffffff;
      border-radius: 20px;
      box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      margin-bottom: 14px;
      opacity: 0;
      transform: scale(0.92) translateY(16px);
      transform-origin: bottom ${POSITION === 'left' ? 'left' : 'right'};
      pointer-events: none;
      transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .firby-window.is-open {
      opacity: 1;
      transform: scale(1) translateY(0);
      pointer-events: auto;
    }

    /* Header */
    .firby-header {
      padding: 16px 20px;
      background: #09090b;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .firby-header-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .firby-avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: #18181b;
      border: 1px solid rgba(255, 255, 255, 0.15);
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .firby-avatar img {
      width: 24px;
      height: 24px;
      object-fit: contain;
    }

    .firby-header-title {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .firby-status-pill {
      font-size: 10px;
      font-weight: 500;
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      padding: 1px 6px;
      border-radius: 9999px;
      letter-spacing: 0.02em;
    }

    .firby-header-subtitle {
      font-size: 12px;
      color: #a1a1aa;
      margin-top: 1px;
    }

    .firby-close-btn {
      background: transparent;
      border: none;
      color: #a1a1aa;
      cursor: pointer;
      padding: 6px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s, color 0.15s;
    }

    .firby-close-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #ffffff;
    }

    /* Message Stream */
    .firby-stream {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #fafafa;
    }

    .firby-stream::-webkit-scrollbar {
      width: 5px;
    }
    .firby-stream::-webkit-scrollbar-thumb {
      background: #e4e4e7;
      border-radius: 4px;
    }

    .firby-msg {
      max-width: 82%;
      padding: 12px 15px;
      font-size: 13.5px;
      line-height: 1.45;
      word-wrap: break-word;
      animation: firby-msg-fade 0.2s ease-out;
    }

    @keyframes firby-msg-fade {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .firby-msg-bot {
      align-self: flex-start;
      background: #ffffff;
      color: #18181b;
      border-radius: 16px 16px 16px 4px;
      border: 1px solid #e4e4e7;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }

    .firby-msg-user {
      align-self: flex-end;
      background: ${PRIMARY_COLOR};
      color: #ffffff;
      border-radius: 16px 16px 4px 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Chips Container */
    .firby-chips-container {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 8px 16px;
      background: #ffffff;
      border-top: 1px solid #f4f4f5;
    }

    .firby-chips-container::-webkit-scrollbar {
      display: none;
    }

    .firby-chip {
      white-space: nowrap;
      background: #f4f4f5;
      border: 1px solid #e4e4e7;
      border-radius: 9999px;
      padding: 6px 12px;
      font-size: 11.5px;
      color: #27272a;
      cursor: pointer;
      transition: all 0.15s ease;
      user-select: none;
    }

    .firby-chip:hover {
      background: #09090b;
      color: #ffffff;
      border-color: #09090b;
    }

    /* Typing Indicator */
    .firby-typing {
      align-self: flex-start;
      background: #ffffff;
      border: 1px solid #e4e4e7;
      border-radius: 16px 16px 16px 4px;
      padding: 10px 14px;
      display: flex;
      gap: 4px;
      align-items: center;
    }

    .firby-typing-dot {
      width: 6px;
      height: 6px;
      background: #a1a1aa;
      border-radius: 50%;
      animation: firby-blink 1.4s infinite both;
    }

    .firby-typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .firby-typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes firby-blink {
      0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
      40% { opacity: 1; transform: scale(1.1); }
    }

    /* Footer Input */
    .firby-footer {
      padding: 12px 16px;
      background: #ffffff;
      border-top: 1px solid #f4f4f5;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .firby-input {
      flex: 1;
      height: 42px;
      background: #f4f4f5;
      border: 1px solid #e4e4e7;
      border-radius: 12px;
      padding: 0 14px;
      font-size: 13.5px;
      color: #18181b;
      outline: none;
      transition: border-color 0.15s;
    }

    .firby-input:focus {
      border-color: #09090b;
      background: #ffffff;
    }

    .firby-send-btn {
      width: 42px;
      height: 42px;
      background: #09090b;
      color: #ffffff;
      border: none;
      border-radius: 12px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: opacity 0.15s, transform 0.1s;
    }

    .firby-send-btn:hover {
      opacity: 0.9;
    }

    .firby-send-btn:active {
      transform: scale(0.95);
    }

    .firby-send-btn:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
  `;

  // 5. Template HTML
  const container = document.createElement('div');
  container.className = 'firby-wrapper';
  container.innerHTML = `
    <div class="firby-window" id="firby-window">
      <div class="firby-header">
        <div class="firby-header-info">
          <div class="firby-avatar">
            <img src="${hostUrl}/brand-assets/firby-isotype.png" alt="Firby" id="firby-avatar-img">
          </div>
          <div>
            <div class="firby-header-title">
              <span id="firby-title">Firby</span>
              <span class="firby-status-pill">En vivo</span>
            </div>
            <div class="firby-header-subtitle" id="firby-subtitle">Operador Autónomo</div>
          </div>
        </div>
        <button class="firby-close-btn" id="firby-close" aria-label="Cerrar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="firby-stream" id="firby-stream"></div>

      <div class="firby-chips-container" id="firby-chips" style="display: none;"></div>

      <div class="firby-footer">
        <input type="text" class="firby-input" id="firby-input" placeholder="Escribe tu mensaje..." autocomplete="off">
        <button class="firby-send-btn" id="firby-send" aria-label="Enviar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>

    <div class="firby-launcher" id="firby-launcher" role="button" aria-label="Abrir asistente">
      <div class="firby-launcher-icon" id="firby-launcher-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
      <div class="firby-badge-pulse"></div>
    </div>
  `;

  shadow.appendChild(style);
  shadow.appendChild(container);

  // 6. Lógica de Interacción y Comunicación
  const windowEl = shadow.getElementById('firby-window');
  const launcherEl = shadow.getElementById('firby-launcher');
  const closeEl = shadow.getElementById('firby-close');
  const streamEl = shadow.getElementById('firby-stream');
  const inputEl = shadow.getElementById('firby-input');
  const sendEl = shadow.getElementById('firby-send');
  const chipsEl = shadow.getElementById('firby-chips');
  const titleEl = shadow.getElementById('firby-title');
  const subtitleEl = shadow.getElementById('firby-subtitle');

  let isOpen = false;
  let isSending = false;

  // Sesión única del visitante en localStorage
  let sessionId = localStorage.getItem('firby_embed_session_' + ORG_ID);
  if (!sessionId) {
    sessionId = 'lead_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();
    localStorage.setItem('firby_embed_session_' + ORG_ID, sessionId);
  }

  function toggleChat() {
    isOpen = !isOpen;
    if (isOpen) {
      windowEl.classList.add('is-open');
      setTimeout(() => inputEl.focus(), 150);
    } else {
      windowEl.classList.remove('is-open');
    }
  }

  launcherEl.addEventListener('click', toggleChat);
  closeEl.addEventListener('click', toggleChat);

  function appendMessage(text, isUser = false) {
    const msg = document.createElement('div');
    msg.className = `firby-msg ${isUser ? 'firby-msg-user' : 'firby-msg-bot'}`;
    msg.textContent = text;
    streamEl.appendChild(msg);
    streamEl.scrollTop = streamEl.scrollHeight;
  }

  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'firby-typing';
    typing.id = 'firby-typing-indicator';
    typing.innerHTML = '<div class="firby-typing-dot"></div><div class="firby-typing-dot"></div><div class="firby-typing-dot"></div>';
    streamEl.appendChild(typing);
    streamEl.scrollTop = streamEl.scrollHeight;
  }

  function hideTyping() {
    const typing = shadow.getElementById('firby-typing-indicator');
    if (typing) typing.remove();
  }

  function renderChips(chips) {
    if (!chips || chips.length === 0) {
      chipsEl.style.display = 'none';
      chipsEl.innerHTML = '';
      return;
    }
    chipsEl.innerHTML = '';
    chips.forEach(chipText => {
      const chip = document.createElement('button');
      chip.className = 'firby-chip';
      chip.textContent = chipText;
      chip.addEventListener('click', () => {
        handleUserSend(chipText);
      });
      chipsEl.appendChild(chip);
    });
    chipsEl.style.display = 'flex';
  }

  async function handleUserSend(overrideText) {
    const text = (overrideText || inputEl.value).trim();
    if (!text || isSending) return;

    if (!overrideText) {
      inputEl.value = '';
    }

    appendMessage(text, true);
    isSending = true;
    sendEl.disabled = true;
    renderChips([]);
    showTyping();

    try {
      const res = await fetch(`${hostUrl}/api/widget/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          org_id: ORG_ID
        })
      });

      hideTyping();

      if (res.ok) {
        const data = await res.json();
        if (data.bubbles && Array.isArray(data.bubbles)) {
          data.bubbles.forEach((bubbleText, idx) => {
            setTimeout(() => appendMessage(bubbleText, false), idx * 250);
          });
        } else if (data.response) {
          appendMessage(data.response, false);
        }

        if (data.chips) {
          renderChips(data.chips);
        }

        // Navegación cinemática lenta y enmarcado en el sitio anfitrión si aplica
        if (data.ui_action) {
          const act = data.ui_action;
          const route = act.route || act.target || act.section;
          if (route) {
            try {
              if (window.FirbyScrollDirector && typeof window.FirbyScrollDirector.scrollTo === 'function') {
                window.FirbyScrollDirector.scrollTo(route, {
                  duration: act.duration || 1500,
                  label: act.label || null,
                  strikeKeyword: act.strike_keyword || null,
                  highlightKeyword: act.highlight_keyword || null
                });
              } else if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.navigateToElement === 'function') {
                window.FirbyMotionEngine.navigateToElement(route, {
                  slow: true,
                  duration: 1.6,
                  label: act.label || null,
                  strikeKeyword: act.strike_keyword || null,
                  highlightKeyword: act.highlight_keyword || null
                });
              } else {
                const target = document.querySelector(route);
                if (target) target.scrollIntoView({ behavior: 'smooth' });
              }

              // Reportar observación confirmada al backend tras completar el scroll
              if (data.requires_observation && data.run_id) {
                const durationMs = (act.duration ? (act.duration > 50 ? act.duration : act.duration * 1000) : 1500) + 150;
                setTimeout(async () => {
                  try {
                    await fetch(`${hostUrl}/api/widget/observe`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        run_id: data.run_id,
                        observation: {
                          success: true,
                          action_type: act.type || 'navigate_to_section',
                          target: route,
                          completed_at: Date.now() / 1000
                        },
                        user_id: USER_ID
                      })
                    });
                  } catch (errObs) {
                    console.warn('[Firby] Error reportando observación:', errObs);
                  }
                }, durationMs);
              }
            } catch (e) {
              console.warn('[Firby] Error en navegación guiada:', e);
            }
          }
        }
      } else {
        appendMessage('No se pudo procesar la solicitud en este momento.', false);
      }
    } catch (e) {
      hideTyping();
      appendMessage('Problema de conexión con el operador.', false);
    } finally {
      isSending = false;
      sendEl.disabled = false;
    }
  }

  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleUserSend();
    }
  });

  sendEl.addEventListener('click', () => handleUserSend());

  // 7. Cargar Configuración Dinámica del Inquilino (Hydration)
  async function hydrateConfig() {
    try {
      const res = await fetch(`${hostUrl}/api/v1/widget/config?org_id=${encodeURIComponent(ORG_ID)}`);
      if (res.ok) {
        const config = await res.json();
        if (config.business_name) {
          titleEl.textContent = config.business_name;
        }
        if (config.title) {
          subtitleEl.textContent = config.title;
        }
        if (config.welcome_messages && Array.isArray(config.welcome_messages)) {
          config.welcome_messages.forEach(msg => appendMessage(msg, false));
        }
        if (config.quick_chips) {
          renderChips(config.quick_chips);
        }
      } else {
        // Saludo por defecto
        appendMessage('Hola, en qué puedo colaborarte hoy?', false);
        renderChips(['Agendar cita', 'Horarios de atención', 'Consultar servicios']);
      }
    } catch (e) {
      appendMessage('Hola, en qué puedo colaborarte hoy?', false);
    }
  }

  // Ejecutar hidratación inicial
  hydrateConfig();

})();
