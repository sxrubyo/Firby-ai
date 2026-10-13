# FIRBY — ARQUITECTURA, REGLAS OPERATIVAS Y PROTOCOLO DE PREFLIGHT

## 0. REGLA INQUEBRANTABLE DE CONTEXTO Y TRATO (CANARY RULE)
- **EL USUARIO ES SANTIAGO RUBIO PARRA ("Santi" o "Santiago").**
- **OBLIGACIÓN EN CADA MENSAJE:** El asistente DEBE llamar SIEMPRE a Santiago por su nombre ("Santi" o "Santiago") en cada mensaje sin excepción.

## 1. REGLA INQUEBRANTABLE DE CANALES Y COMUNICACIÓN
- **EN LA WEB (Público / Visitantes / Leads de mi cliente):**
  - Firby vive en el sitio web de mi cliente mediante un widget/botón flotante 2D de atención.
  - Atiende a los visitantes en la web en tiempo real.
  - Consulta disponibilidad real en Google Calendar, agenda citas confirmadas y resuelve dudas directamente en la web.
  - **FIRBY NUNCA ATIENDE VISITANTES/LEADS POR WHATSAPP.**
- **EN WHATSAPP (+57 324 369 9856) (Privado / Dueño del Negocio / Mi Cliente / Santi):**
  - Firby habla por WhatsApp **ÚNICA Y EXCLUSIVAMENTE CON EL DUEÑO DEL NEGOCIO**.
  - Es una línea ejecutiva privada y continua: alertas de citas, visto bueno para excepciones comerciales, consultas de métricas y comandos.

## 2. RESTRICCIONES DE MARKETING Y COPYWRITING
- **Cero emojis** en toda la web, botones, badges o textos.
- **Cero mención de $1.000 COP** (la oferta pública es "Prueba 7 días gratis. Cancela cuando quieras en 1 clic").
- Español real, directo, de negocios, sin lenguaje artificial de IA ("solución integral", "revoluciona", etc.).

## 3. PROTOCOLO OBLIGATORIO DE PREFLIGHT, MAPAS MENTALES Y PREVISUALIZACIÓN VISUAL
**MANDATORIO EN CADA REQUERIMIENTO E INSTRUCCIÓN ANTES DE MODIFICAR CÓDIGO O DESPLEGAR:**

### 3.1. Repositorios y herramientas instaladas en el sistema
- **Motores de Mapas Mentales y Arquitectura Visual:**
  - `@mermaid-js/mermaid-cli` (`mmdc` v12.0): Compilador oficial de diagramas y árboles de decisión visuales a PNG en alta resolución (2400px, tema oscuro `#0B0F12`).
  - `markmap-cli` (`markmap`): Visualizador de mapas mentales interactivos a partir de especificaciones Markdown.
  - `Prompt-Engineering-Guide` (`dair-ai`): Clonado en `/home/ubuntu/firby/tools/Prompt-Engineering-Guide` para desambiguación estructurada, descomposición de intenciones y reducción de incertidumbre en prompts.
- **Motores de Pre-visualización Visual e Inspección Pre-Flight:**
  - `capture-website-cli` (`capture-website`): Emulación de navegadores, inyección de CSS/JS en caliente y captura de selectores exactos con escala retina (`scale-factor=2`).
  - `shot-scraper`: Motor CLI basado en Playwright instalado en el entorno Python de Firby (`/home/ubuntu/firby/.venv/bin/shot-scraper`).
  - `reg-cli` (`reg-viz`): Herramienta para análisis de regresión visual y comparación de diferencias (visual diff) entre interfaces.

### 3.2. Pipeline automatizado de Firby (`/home/ubuntu/firby/scripts`)
- `firby_mindmap.py`: Traduce los requerimientos a un mapa mental visual PNG (nodo raíz, objetivo refinado, componentes afectados, reglas operativas y verificación).
- `firby_visual_preflight.py`: Carga la interfaz viva (`http://127.0.0.1:8001` o `8003`), inyecta los estilos o modificaciones en memoria del navegador headless (sin tocar archivos de disco) y extrae una captura PNG de alta fidelidad.
- `firby_preflight_pipeline.py`: Orquestador único que ejecuta ambos pasos en paralelo y genera los artefactos visuales correspondientes.

### 3.3. Flujo Operativo Requerido en Cada Mensaje
Con cada instrucción de Santiago (Santi):
1. **Refinamiento de Intención:** Interpretar la instrucción sin suposiciones y descomponer el impacto técnico.
2. **Generación de Mapa Mental Técnico:** Ejecutar `firby_mindmap.py` y vincular el PNG resultante.
3. **Pre-flight Visual en Sandbox:** Si la tarea incluye cambios visuales o de interfaz, ejecutar `firby_visual_preflight.py` para renderizar el mockup en memoria antes de tocar código de desarrollo o producción.
4. **Presentación de Evidencia:** Mostrar ambos artefactos a Santi para confirmación previa.

## 4. MÓDULO DE FLUJOS: LIENZO IDÉNTICO A N8N
- **UBICACIÓN:** `/workspace/inbox` (en el sidebar: "Flujos" ➔ "Flujos de trabajo").
- **DISEÑO N8N EXACTO:**
  - Cuadrícula de puntos infinita (dot grid), nodos visuales conectados por curvas bézier, puertos circulares de entrada/salida, drawer lateral de parámetros y payload JSON al hacer clic en un nodo, botón "+ Añadir nodo" y simulador "Probar flujo" con estado en vivo.
  - Librería: `@xyflow/react` en frontend Next.js.
  - Prohibido convertirlo en una bandeja de chat o tabla simple de métricas.

## 5. INFRAESTRUCTURA Y SERVICIOS PM2
- **Directorio Frontend:** `/home/ubuntu/firby/dev/react`
  - Build: `cd /home/ubuntu/firby/dev/react && npm run build`
- **Procesos PM2:**
  - PM2 0: `firby` (DEV en `http://127.0.0.1:8001` / `dev.firbyai.lat`)
  - PM2 6: `firby-production` (PROD en `http://127.0.0.1:8003` / `firbyai.lat`)
  - PM2 7: `laya-service` (Motor de navegación en `http://127.0.0.1:8005`)
  - PM2 5: `paperclip` (Control plane en `http://127.0.0.1:3100`)
  - PM2 3: `n8n` (Instancia local en `http://127.0.0.1:5678`)
  - PM2 2: `whatsapp-bridge` (Línea ejecutiva privada en `http://127.0.0.1:8002`)
- **Header persistente:** Altura fija `h-16`, logo Firby, toggle de colapso, campana y anillo de perfil Google One (`#b9fa01` y `#facc15`).
