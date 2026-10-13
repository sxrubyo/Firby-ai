# FIRBY AI · PLAN MAESTRO DE EVOLUCIÓN ESTRATÉGICA & LANZAMIENTO
## De Chatbot Clínico a Plataforma de Operadores Autónomos de Negocio

> **Versión:** 2.0 (Consolidada con Modelo Financiero y Bucle Telegram)  
> **Fecha:** Septiembre 2026  
> **Autor:** Santiago Rubio & Firby AI Core Engineering  
> **Ubicación Principal:** `/home/ubuntu/FIRBY_AUTONOMOUS_OPERATOR_PLAN.md`  
> **Estado:** Documento Maestro para Revisión de Agente y Ejecución

---

## 1. La Tesis Estratégica: El Cambio de Era (2020 vs 2026)

### El Colapso de los Chatbots (2020 - 2023)
- ChatGPT popularizó los chatbots de texto.
- Grandes marcas (McDonald's, bancos, aerolíneas) los implementaron y los clientes los rechazaron porque **solo hablaban y no resolvían nada**.
- Si un usuario decía *"quiero cambiar mi correo"*, el bot repetía: *"Dirígete a configuración en la app..."*.
- Resultado: cancelaciones masivas y comoditización a $30 - $50 USD/mes.

### La Nueva Era: Agentes de Acción y Operación (2024 - 2026)
- Modelos como **Claude Code**, **Google Antigravity** y la **Consola de AWS** demostraron el verdadero poder: agentes que tienen herramientas, acceso a APIs, ejecutan comandos y aplican gobernanza.
- Las empresas no buscan otro bot de texto; buscan **un operador digital que reduzca el costo de nómina de soporte y front-desk**.

---

## 2. La Evolución de la Recepcionista Clínica

### ¿Dónde quedan nuestros agentes actuales? (Valeria, Santiago, Camila, Nova, Mateo)
- En el mundo físico, una recepcionista **no es un loro que solo saluda**: es la operadora del front-desk. Pide documentos, verifica citas, cambia datos en el sistema, cobra y pide autorización al doctor cuando hay excepciones.
- La clínica médica fue nuestro **stress-test de máxima complejidad** (empatía humana estricta, privacidad y agendamiento).
- Al evolucionar a **Operador Autónomo de Negocio**, el agente no solo opera clínicas: opera cualquier empresa (e-commerce, SaaS, inmobiliarias, despachos legales).
- Los 5 roles ya programados en `src/firby/brain/employee_roles.py` se convierten en los operadores especializados de la plataforma.

---

## 3. El Bucle de Acción: Telegram + Gmail + Web

```
1. Usuario en la web: "Quiero cambiar mi correo a santiago@..."
2. Firby valida identidad previa (Nivel 2).
3. Como es una acción sensible, Firby envía alerta instantánea a TELEGRAM:
   ┌─────────────────────────────────────────────────────────┐
   │ 🔔 FIRBY ALERT · Solicitud de Cambio de Correo          │
   │ Usuario: Santiago Gómez · ID: #4829                     │
   │ Nuevo correo: santiago@nuevo.com                        │
   │ [  ✓ APROBAR ACCIÓN  ]      [  ✕ RECHAZAR  ]            │
   └─────────────────────────────────────────────────────────┘
4. El dueño o recepcionista toca [✓ APROBAR] desde su celular en Telegram.
5. Firby ejecuta el cambio en la base de datos y le confirma al usuario en la web:
   "¡Listo! Tu correo ha sido actualizado con éxito."
6. A las 7:00 PM, Firby envía el Reporte Ejecutivo EOD a GMAIL:
   "Hoy Firby resolvió 64 acciones, 18 citas agendadas y 0 errores."
```

---

## 4. Software de Gobernanza: Los 3 Niveles de Acción
*La razón por la que las empresas pagan 10 veces más: Cero Riesgo.*

1. **Nivel 1 (Autónomo Seguro)**:
   - Consultas de catálogo, precios públicos, horarios, citas en huecos libres.
   - Resuelve directamente en milisegundos.
2. **Nivel 2 (Acción Verificada)**:
   - Cambios de datos personales (correo, teléfono), reagendamiento.
   - Pide validación de identidad previa antes de tocar la base de datos.
3. **Nivel 3 (Gobernanza / Human-in-the-Loop)**:
   - Reembolsos, excepciones de tarifas, cancelaciones especiales.
   - El agente **NO** ejecuta solo: envía tarjeta interactiva a Telegram o panel para aprobación con 1 clic.

---

## 5. Modelo de Precios y Retorno de Inversión (COP & USD)

### Estructura de Planes Mensuales

| Plan | Precio USD | **Precio COP / mes** | Propuesta de Valor para el Cliente |
| :--- | :--- | :--- | :--- |
| **Starter** *(Operador Web)* | $199 USD | **$790.000 COP** | Widget web de 1 línea. Hasta 500 acciones resueltas. Guardrails Nivel 1 y 2. Reporte diario a Gmail. |
| **Pro** *(Omnicanal + Telegram)* | $499 USD | **$1.990.000 COP** | Web + WhatsApp + Instagram. Hasta 2.500 acciones. Aprobaciones interactivas por Telegram. Integraciones n8n. |
| **Enterprise** *(Total + Voz)* | $1.200 USD | **$4.800.000 COP** | Todo lo anterior + Agente de Voz telefónica en vivo. Instancia dedicada aislada. |

### Retorno de Inversión (ROI) sobre $600.000 COP de Pauta / Lanzamiento:
- **Presupuesto**: $600.000 COP (~$150 USD).
- **Visitas B2B**: 500 - 700 clics de dueños de empresas en Colombia.
- **Pruebas de 7 días activadas (4%-6%)**: 20 a 35 empresas.
- **Cierres a pago al día 7 (10%-15%)**: 2 a 4 clientes de pago.
- **Facturación Mes 1 (Conservador: 2 Starter)**: **$1.580.000 COP** (**2.6x ROI inmediato**).
- **Facturación Mes 1 (Probable: 1 Pro + 1 Starter)**: **$2.780.000 COP** (**4.6x ROI inmediato**).
- **Valor Recurrente a 6 meses (LTV)**: **$9.480.000 COP** (**15.8x ROI acumulado**).

---

## 6. Hoja de Ruta de los 7 Días para el Lanzamiento

- [x] **Día 0 (Hoy)**:
  - Consolidación del plan estratégico y documento maestro.
  - Widget web flotante de Firby creado y compilado en el frontend (`firby-chat-widget.tsx`).
  - Endpoint de chat directo `/api/widget/chat` activo en FastAPI (puerto 8003).
  - Descarga de isotipos oficiales de WhatsApp, Instagram y Facebook.

- [x] **Día 1 (Gobernanza y Dashboard)**:
  - Implementar el software de Guardrails (Lista blanca de herramientas en backend `src/core/guardrails.py`).
  - Diseñar la **Consola de Operaciones** en `dashboard.tsx` con la Matriz de Permisos visual y endpoints `/api/governance/*`.
  - Sección de "Instalación en 1 Clic" con el snippet `<script src="https://firbyai.com/widget.js" ...>` y el script estático compilado y sirviendo en port 8003.

- [ ] **Día 2 (Bucle Telegram & Aprobaciones)**:
  - Conectar el bot de Telegram con botones inline de `[✓ Aprobar]` y `[✕ Rechazar]`.
  - Probar el flujo completo: Web -> Validación -> Alerta Telegram -> Aprobación -> Confirmación.

- [ ] **Día 3 (Reporte Diario a Gmail)**:
  - Script automatizado de reporte ejecutivo diario (resumen de acciones y horas ahorradas).

- [ ] **Día 4 y 5 (Landing Page de Conversión & Oferta de 7 Días)**:
  - Adaptar la página principal (`firbyai.com`) con el nuevo copy y el widget embebido para prueba inmediata.

- [ ] **Día 6 y 7 (Lanzamiento & Campaña de $600.000 COP)**:
  - Configurar campaña en Meta Ads segmentada a tomadores de decisión.
  - Outreach directo por mensaje mostrando el widget en acción.
