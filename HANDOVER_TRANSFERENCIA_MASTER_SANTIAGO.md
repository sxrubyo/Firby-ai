# MAPA MAESTRO DE TRANSFERENCIA Y CONTINUIDAD: FIRBY AI

> **DOCUMENTO DE ENTREGA TÉCNICA Y OPERATIVA**  
> **Destinatario:** Antigravity CLI / Nuevo Agente  
> **Usuario / Fundador:** Santiago Rubio Parra (**Santi** / **Santiago**)  
> **Fecha:** 21 de Septiembre de 2026  
> **Ubicación en Servidor:** `/home/ubuntu/firby`  

---

## 0. REGLA INQUEBRANTABLE DE CONTEXTO Y TRATO (CANARY RULE)

> [!IMPORTANT]
> **CANARIO DE IDENTIDAD ACTIVO:**
> En **CADA MENSAJE** que envíes, **DEBES llamar al usuario por su nombre: Santi o Santiago**.  
> Esto permite a Santiago verificar de un vistazo que mantienes el contexto completo del proyecto, conoces su identidad y que el modelo no está alucinando. Si no lo llamas por su nombre, Santiago sabrá de inmediato que perdiste el hilo.

---

## 1. LA REGLA SAGRADA DE PRODUCTO Y CANALES

1. **EN LA WEB (Público / Visitantes / Leads de los clientes de Firby):**
   - Firby vive en el sitio web del cliente mediante un widget/botón flotante 2D de atención.
   - Atiende en tiempo real: consulta el backend, revisa disponibilidad en Google Calendar, agenda citas confirmadas y resuelve dudas.
   - **FIRBY NUNCA ATIENDE VISITANTES/LEADS POR WHATSAPP.**

2. **EN WHATSAPP (+57 324 369 9856) (Línea Privada con el Dueño del Negocio):**
   - Firby habla por WhatsApp **ÚNICA Y EXCLUSIVAMENTE CON EL DUEÑO DEL NEGOCIO**.
   - Funciones en WhatsApp:
     - Envía alertas instantáneas de citas confirmadas en la web.
     - Pide visto bueno para excepciones comerciales o solicitudes fuera de política.
     - Asistente de comando continuo ("¿cuántas citas hay hoy?", "bloquea el viernes por la tarde").

3. **Restricciones de Marketing:**
   - **Cero emojis** en toda la interfaz, botones, badges o textos.
   - **Cero mención de $1.000 COP**. La oferta oficial es: *"Prueba 7 días gratis. Cancela cuando quieras en 1 clic"*.

---

## 2. INFRAESTRUCTURA, RUTAS Y PROCESOS PM2

- **Ruta del repositorio principal:** `/home/ubuntu/firby`
- **Rama git activa:** `firby-rebrand`
- **Ruta del Frontend (Next.js 16.3.1):** `/home/ubuntu/firby/dev/react`
- **Ruta de salida estática generada:** `/home/ubuntu/firby/dev/react/out`
- **Comando de compilación:**
  ```bash
  cd /home/ubuntu/firby/dev/react && npm run build
  ```
- **Procesos PM2 en ejecución:**
  - **PM2 0 (`firby`):** Entorno DEV en puerto `8001` (`dev.firbyai.com`). Directorio `/home/ubuntu/bublee/run.sh`.
  - **PM2 6 (`firby-production`):** Entorno PROD en puerto `8003` (`firbyai.com`). Directorio `/home/ubuntu/firby/instances/production/run.sh`.
  - **PM2 3 (`n8n`):** Instancia local nativa de n8n corriendo en puerto `5678`.
- **Comando de reinicio tras compilación:**
  ```bash
  pm2 restart 0 && pm2 restart 6
  ```

---

## 3. ESTADO ACTUAL DE LO REALIZADO EN ESTA SESIÓN

1. **Header Persistente en Todas las Subpáginas (`app-shell.tsx`):**
   - Logo e Isotipo Firby AI a la izquierda.
   - Botón toggle colapsar/expandir barra lateral.
   - Campana de notificaciones con popover.
   - Anillo estilo Google One en degradado verde lima (`#b9fa01`) y amarillo (`#facc15`) cargando nombre y email dinámicos desde perfil/base de datos.
   - Altura estrictamente fija en `h-16` (**no alterar altura**, acordado con Santi: *"límite hasta ahí"*).
2. **Ensanchamiento Horizontal del Contenedor Central:**
   - Se removió la restricción `max-w-6xl` (1152px) en `app-shell.tsx`, `efferd-dashboard-2.tsx` y `dashboard.tsx`.
   - Ahora fluye hasta `max-w-[1800px]`, expandiéndose fluidamente al redimensionar o colapsar el slide bar.
3. **Eliminación del Bloque "Próximas citas agendadas":**
   - Removido 100% de `dashboard.tsx`.
4. **Limpieza del Slide Bar (`modern-side-bar.tsx`):**
   - Removido perfil antiguo de desarrollador (`dev@tesla`).
   - Ajustes y Ayuda fijados al pie de la barra lateral.
   - Marcado activo en verde lima `#b9fa01` estricto por ruta exacta.

---

## 4. LA TAREA CRÍTICA EN CURSO: EL MÓDULO DE FLUJOS ESTILO N8N

### El Diagnóstico de Santi:
- Santi abrió `/workspace/inbox/` y vio una tabla con métricas y tarjetas de texto que se veía como un dashboard común.
- Su indicación textual y enfática fue:
  > *"ESTO SE VE TERRIBLE. habra un repo de github que te guie con el diseño casi ecacto de n8n para que te guies con los lienzos etc"*
- **Qué debe ser la página de Flujos:**
  - **LA PANTALLA PRINCIPAL DEBE SER DIRECTAMENTE EL LIENZO (CANVAS) DE AUTOMATIZACIÓN DE N8N.**
  - No una lista de métricas ni una tabla aburrida.
  - Debe lucir idéntico al editor de n8n:
    1. **Fondo dot-grid infinito** (puntos grises sobre fondo blanco en light mode / puntos oscuros en dark mode).
    2. **Nodos visuales estilo n8n:**
       - Tarjetas con bordes redondeados y sombra sutil.
       - Barra superior con color distintivo según el tipo:
         - Disparador Webhook / Widget Web 2D: Coral / Naranja / Azul pizarra.
         - Inteligencia Artificial (Operador Firby LLM): Violeta / Púrpura.
         - Herramientas / Google Calendar: Azul / Esmeralda.
         - WhatsApp Ejecutivo Dueño: Verde lima (`#b9fa01`).
       - Puertos circulares de conexión a los lados con botón `(+)` para encadenar el siguiente paso.
       - Conexiones con curvas Bézier fluidas entre nodos.
    3. **Toolbar superior del Editor de Flujo:**
       - Selector / dropdown del flujo activo (ej. *"Agendamiento en Sitio Web"* / *"Alerta WhatsApp Dueño"* / *"Leads Nocturnos"*).
       - Switch Toggle: `Inactivo / Activo` (verde lima brillante).
       - Botón `+ Añadir nodo` (abre panel derecho de catálogo de nodos).
       - Botón `Probar flujo` (Test step con ejecución nodo a nodo y ticks verdes).
       - Botón `Guardar`.
    4. **Panel Lateral Derecho (Drawer de Catálogo y Configuración):**
       - Al hacer clic en un nodo: parámetros del nodo (Calendario, teléfono autorizado `+57 324 369 9856`, prompt del operador) e inspección de JSON de entrada y salida.
       - Al hacer clic en `+ Añadir nodo`: buscador de integraciones (*Disparadores*, *Agentes IA*, *Google Calendar*, *WhatsApp Dueño*, *Lógica If/Else*).
    5. **Controles flotantes:** Botones inferiores de Zoom (`+`, `-`, fit to view `[ ]`, reset 100%).

### Lo que ya se adelantó para esto:
- Se instaló la librería oficial de nodos: **`@xyflow/react`** (React Flow v12) en `/home/ubuntu/firby/dev/react`.
- `package.json` ya tiene `@xyflow/react` listo para importar:
  ```tsx
  import { ReactFlow, Background, Controls, Handle, Position, applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
  import "@xyflow/react/dist/style.css";
  ```

### Repositorios de GitHub de referencia exacta para guiarse:
1. **`n8n-io/n8n`** (`packages/editor-ui/src`): El código frontend original del canvas de n8n.
2. **`nobruf/shadcn-next-workflows`**: Implementación de Next.js + React Flow + shadcn/ui con nodos personalizados para flujos de trabajo idénticos a n8n.
3. **`koolii/react-workflow-editor`**: Editor de flujos en React Flow diseñado para ser 100% compatible con el formato de n8n.
4. **`kotiyalashwin/n8n-project`**: Clon de n8n construido en Next.js con React Flow y canvas interactivo drag-and-drop.

---

## 5. ARCHIVOS CLAVE A LEER Y EDITAR

1. `/home/ubuntu/.gemini/GEMINI.md`: Reglas globales del sistema (ya actualizado con el canario de Santi y la arquitectura n8n).
2. `/home/ubuntu/firby/dev/react/src/app/workspace/inbox/page.tsx`: Aquí vive el Lienzo de Flujos estilo n8n.
3. `/home/ubuntu/firby/dev/react/src/components/app-shell.tsx`: Layout con el Header persistente y el Sidebar.
4. `/home/ubuntu/firby/dev/react/src/components/ui/modern-side-bar.tsx`: Barra lateral con rutas y colapso.
5. `/home/ubuntu/firby/dev/react/src/components/dashboard.tsx`: Panel general de bienvenida del workspace.
6. `/home/ubuntu/firby/USER.md`: Ficha de usuario de Santiago Rubio.

---

## 6. CHECKLIST DE INICIO PARA EL NUEVO CHAT

- [ ] Saludar a **Santi** por su nombre en el primer mensaje (*"Hola Santi..."*).
- [ ] Confirmar que leíste este mapa de transferencia en `/home/ubuntu/.gemini/GEMINI.md` y este artefacto.
- [ ] Proceder de inmediato a construir el **Lienzo (Canvas) de Automatización idéntico a n8n** en `dev/react/src/app/workspace/inbox/page.tsx` usando `@xyflow/react` con dot-grid, nodos custom de Firby, toolbar y drawer de parámetros.
- [ ] Compilar con `npm run build` y reiniciar PM2 0 y PM2 6.
