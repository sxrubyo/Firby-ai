/**
 * Firby AI — Universal One-Line Agent Embed SDK
 * ============================================
 * Permite instalar el agente autónomo de Firby en cualquier sitio web con 1 sola línea:
 * 
 * <script src="https://cdn.firbyai.lat/firby.js"></script>
 * <script>
 *   Firby.init({ agent: "agt_firby_demo" });
 * </script>
 * 
 * O directamente:
 * <script src="https://cdn.firbyai.lat/firby.js" data-agent="agt_firby_demo"></script>
 * 
 * Arquitectura Segura:
 * - El cliente NUNCA recibe claves de API ni secretos de integración.
 * - Resuelve la configuración pública mínima mediante GET /public/agents/{public_id}/bootstrap.
 * - Vincula la sesión criptográficamente en el backend (Tenant Pinning).
 */
(function (window, document) {
  'use strict';

  if (window.Firby && window.Firby.__INITIALIZED__) return;

  const Firby = {
    __INITIALIZED__: false,
    version: "2.0.0",
    config: null,
    sessionToken: null,
    conversationId: null,
    publicId: null,
    isOpen: false,

    init: function (options) {
      if (this.__INITIALIZED__) return;
      options = options || {};

      const currentScript = document.currentScript || (function () {
        const scripts = document.getElementsByTagName('script');
        for (let i = scripts.length - 1; i >= 0; i--) {
          if (scripts[i].src && scripts[i].src.indexOf('firby.js') !== -1) {
            return scripts[i];
          }
        }
        return scripts[scripts.length - 1];
      })();

      const publicId = options.agent ||
        (currentScript && currentScript.getAttribute('data-agent')) ||
        (currentScript && currentScript.getAttribute('data-firby-id')) ||
        'agt_firby_demo';

      const apiHost = options.host ||
        (currentScript && currentScript.getAttribute('data-host')) ||
        window.location.origin;

      this.publicId = publicId;
      this.apiHost = apiHost;
      this.__INITIALIZED__ = true;

      // Recuperar session token guardado
      const storageKey = 'firby_session_' + publicId;
      this.sessionToken = localStorage.getItem(storageKey) || null;

      // Ejecutar Bootstrap público seguro
      this._bootstrap(publicId, apiHost, storageKey);
    },

    _bootstrap: function (publicId, apiHost, storageKey) {
      const self = this;
      const url = `${apiHost}/public/agents/${encodeURIComponent(publicId)}/bootstrap` +
        (self.sessionToken ? `?session_token=${encodeURIComponent(self.sessionToken)}` : '');

      fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } })
        .then(function (res) {
          if (!res.ok) throw new Error('Error en bootstrap de agente (' + res.status + ')');
          return res.json();
        })
        .then(function (data) {
          if (!data.ok) {
            console.warn('[Firby] No se pudo inicializar agente:', data.error);
            return;
          }

          self.config = data;
          if (data.session && data.session.session_token) {
            self.sessionToken = data.session.session_token;
            self.conversationId = data.session.conversation_id;
            localStorage.setItem(storageKey, self.sessionToken);
          }

          self._renderWidget(data);
        })
        .catch(function (err) {
          console.warn('[Firby] Error de conexión durante bootstrap:', err.message);
        });
    },

    _renderWidget: function (data) {
      const self = this;
      const branding = data.branding || {};
      const accentColor = branding.accent_color || '#b9fa01';
      const borderColor = branding.border_color || '#00825a';
      const avatarUrl = branding.avatar_url || '/assets/branding/Isotipo-pestana.png?v=20260914_live';
      const title = branding.title || (data.business && data.business.name) || 'Firby';
      const position = branding.position || 'right';

      // 1. Inyectar estilos CSS
      const styleId = 'firby-embed-styles';
      if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
          .firby-sdk-container {
            position: fixed;
            bottom: 24px;
            ${position === 'left' ? 'left: 24px;' : 'right: 24px;'}
            z-index: 9999999;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", Roboto, sans-serif;
            -webkit-font-smoothing: antialiased;
          }
          .firby-sdk-launcher {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #09090b;
            border: 2px solid ${borderColor};
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
          }
          .firby-sdk-launcher:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
          }
          .firby-sdk-launcher img {
            width: 38px;
            height: 38px;
            object-fit: contain;
            pointer-events: none;
          }
          .firby-sdk-panel {
            position: absolute;
            bottom: 74px;
            ${position === 'left' ? 'left: 0;' : 'right: 0;'}
            width: 380px;
            max-width: calc(100vw - 32px);
            height: 560px;
            max-height: calc(100vh - 100px);
            background: #09090b;
            color: #f4f4f5;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            box-shadow: 0 20px 48px rgba(0, 0, 0, 0.4);
            display: none;
            flex-direction: column;
            overflow: hidden;
          }
          .firby-sdk-panel.open {
            display: flex;
            animation: firbyPanelIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          }
          @keyframes firbyPanelIn {
            from { opacity: 0; transform: translateY(16px) scale(0.96); }
            to { opacity: 1; transform: translateY(0) scale(1); }
          }
          .firby-sdk-header {
            padding: 16px 20px;
            background: #121215;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
          }
          .firby-sdk-header-info {
            display: flex;
            align-items: center;
            gap: 12px;
          }
          .firby-sdk-header-avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            border: 1px solid rgba(255, 255, 255, 0.15);
            background: #09090b;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .firby-sdk-header-avatar img {
            width: 24px;
            height: 24px;
            object-fit: contain;
          }
          .firby-sdk-header-title {
            font-size: 14.5px;
            font-weight: 600;
            color: #f4f4f5;
            letter-spacing: -0.01em;
          }
          .firby-sdk-header-status {
            font-size: 11.5px;
            color: #10b981;
            display: flex;
            align-items: center;
            gap: 5px;
          }
          .firby-sdk-header-status::before {
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #10b981;
          }
          .firby-sdk-close {
            background: transparent;
            border: none;
            color: #a1a1aa;
            cursor: pointer;
            padding: 4px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .firby-sdk-close:hover {
            color: #f4f4f5;
            background: rgba(255, 255, 255, 0.08);
          }
          .firby-sdk-messages {
            flex: 1;
            padding: 16px 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #09090b;
          }
          .firby-sdk-msg {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 13.5px;
            line-height: 1.5;
            word-break: break-word;
          }
          .firby-sdk-msg.assistant {
            align-self: flex-start;
            background: #18181b;
            color: #f4f4f5;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-bottom-left-radius: 4px;
          }
          .firby-sdk-msg.user {
            align-self: flex-end;
            background: ${accentColor};
            color: #09090b;
            font-weight: 500;
            border-bottom-right-radius: 4px;
          }
          .firby-sdk-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 4px;
          }
          .firby-sdk-chip {
            background: #1c1c22;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #e4e4e7;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
          }
          .firby-sdk-chip:hover {
            background: #27272a;
            border-color: rgba(255, 255, 255, 0.2);
            color: #ffffff;
          }
          .firby-sdk-input-area {
            padding: 14px 16px;
            background: #121215;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            gap: 10px;
          }
          .firby-sdk-input {
            flex: 1;
            background: #1c1c22;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #f4f4f5;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 13px;
            outline: none;
          }
          .firby-sdk-input:focus {
            border-color: ${accentColor};
          }
          .firby-sdk-send {
            background: ${accentColor};
            color: #09090b;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.15s ease;
          }
          .firby-sdk-send:hover {
            opacity: 0.9;
          }
        `;
        document.head.appendChild(style);
      }

      // 2. Inyectar contenedor HTML
      const container = document.createElement('div');
      container.className = 'firby-sdk-container';
      container.innerHTML = `
        <div class="firby-sdk-panel" id="firby-sdk-panel">
          <div class="firby-sdk-header">
            <div class="firby-sdk-header-info">
              <div class="firby-sdk-header-avatar">
                <img src="${avatarUrl}" alt="${title}" />
              </div>
              <div>
                <div class="firby-sdk-header-title">${title}</div>
                <div class="firby-sdk-header-status">En línea 24/7</div>
              </div>
            </div>
            <button class="firby-sdk-close" id="firby-sdk-close">✕</button>
          </div>
          <div class="firby-sdk-messages" id="firby-sdk-messages"></div>
          <div class="firby-sdk-input-area">
            <input type="text" class="firby-sdk-input" id="firby-sdk-input" placeholder="Escribe tu consulta..." />
            <button class="firby-sdk-send" id="firby-sdk-send">➔</button>
          </div>
        </div>
        <div class="firby-sdk-launcher" id="firby-sdk-launcher">
          <img src="${avatarUrl}" alt="Firby Concierge" />
        </div>
      `;
      document.body.appendChild(container);

      const panel = document.getElementById('firby-sdk-panel');
      const launcher = document.getElementById('firby-sdk-launcher');
      const closeBtn = document.getElementById('firby-sdk-close');
      const input = document.getElementById('firby-sdk-input');
      const sendBtn = document.getElementById('firby-sdk-send');
      const messagesContainer = document.getElementById('firby-sdk-messages');

      launcher.onclick = function () {
        self.isOpen = !self.isOpen;
        panel.classList.toggle('open', self.isOpen);
        if (self.isOpen) input.focus();
      };

      closeBtn.onclick = function () {
        self.isOpen = false;
        panel.classList.remove('open');
      };

      // 3. Renderizar bienvenida inicial
      if (data.welcome && data.welcome.bubbles) {
        data.welcome.bubbles.forEach(function (b) {
          self._appendMessage(messagesContainer, b, 'assistant');
        });
        if (data.welcome.chips && data.welcome.chips.length) {
          self._renderChips(messagesContainer, data.welcome.chips, input);
        }
      }

      function handleSend() {
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        self._appendMessage(messagesContainer, text, 'user');
        self._sendMessage(text, messagesContainer, input);
      }

      sendBtn.onclick = handleSend;
      input.onkeydown = function (e) {
        if (e.key === 'Enter') handleSend();
      };
    },

    _appendMessage: function (container, text, sender) {
      const msg = document.createElement('div');
      msg.className = 'firby-sdk-msg ' + sender;
      msg.textContent = text;
      container.appendChild(msg);
      container.scrollTop = container.scrollHeight;
      return msg;
    },

    _renderChips: function (container, chips, inputElement) {
      const self = this;
      const chipsWrapper = document.createElement('div');
      chipsWrapper.className = 'firby-sdk-chips';
      chips.forEach(function (chipText) {
        const chip = document.createElement('button');
        chip.className = 'firby-sdk-chip';
        chip.textContent = chipText;
        chip.onclick = function () {
          self._appendMessage(container, chipText, 'user');
          self._sendMessage(chipText, container, inputElement);
          chipsWrapper.remove();
        };
        chipsWrapper.appendChild(chip);
      });
      container.appendChild(chipsWrapper);
      container.scrollTop = container.scrollHeight;
    },

    _sendMessage: function (text, container, inputElement) {
      const self = this;
      const typing = self._appendMessage(container, '...', 'assistant');

      const chatUrl = `${self.apiHost}/public/agents/${encodeURIComponent(self.publicId)}/chat`;
      const payload = {
        message: text,
        session_token: self.sessionToken,
        web_context: {
          current_url: window.location.pathname + window.location.hash,
          page_title: document.title
        }
      };

      fetch(chatUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Error en chat (' + res.status + ')');
          return res.json();
        })
        .then(function (data) {
          typing.remove();

          // Actualizar session token si fue renovado
          if (data.session_token) {
            self.sessionToken = data.session_token;
            localStorage.setItem('firby_session_' + self.publicId, self.sessionToken);
          }

          // Ejecutar UI Actions de navegación si corresponden con física inercial
          const actionToExec = data.action || data.ui_action;
          if (actionToExec && actionToExec.target) {
            const tgt = actionToExec.target;
            if (window.FirbyMotionEngine && typeof window.FirbyMotionEngine.navigateToElement === 'function') {
              window.FirbyMotionEngine.navigateToElement(tgt, { label: actionToExec.label });
            } else if (tgt.startsWith('#')) {
              const el = document.querySelector(tgt);
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            } else if (tgt.startsWith('/')) {
              window.location.href = tgt;
            }
          }

          const bubbles = data.bubbles || (data.response ? [data.response] : []);
          bubbles.forEach(function (b) {
            self._appendMessage(container, b, 'assistant');
          });

          if (data.chips && data.chips.length) {
            self._renderChips(container, data.chips, inputElement);
          }
        })
        .catch(function (err) {
          typing.textContent = 'Lo siento, hubo un problema al procesar tu consulta. Intenta nuevamente.';
        });
    }
  };

  window.Firby = Firby;

  // Auto-init si el script incluye data-agent
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      Firby.init();
    });
  } else {
    Firby.init();
  }

})(window, document);
