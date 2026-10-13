import re
import sys

def update_html(content):
    # 1. Title & Meta tags
    content = re.sub(
        r'<title>.*?</title>',
        '<title>Firby — En Firby tienes el control de tu operación</title>',
        content
    )
    
    content = re.sub(
        r'<meta name="description" content=".*?">',
        '<meta name="description" content="En Firby tienes el control operativo de tu negocio. Tú decides qué acciones se resuelven de forma automática y cuáles requieren tu visto bueno. Agentes autónomos que atienden, verifican y resuelven 24/7.">',
        content
    )

    content = re.sub(
        r'<meta property="og:title" content=".*?">',
        '<meta property="og:title" content="Firby — En Firby tienes el control de tu operación">',
        content
    )
    content = re.sub(
        r'<meta property="og:description" content=".*?">',
        '<meta property="og:description" content="En Firby tienes el control operativo de tu negocio. Agentes autónomos que atienden a tus usuarios, verifican solicitudes y ejecutan procesos reales 24/7 sin salir de tus reglas.">',
        content
    )

    # 2. Hero Section
    content = re.sub(
        r'<h1 class="hero-title">[\s\S]*?</h1>',
        '''<h1 class="hero-title">
                    En Firby tienes el <span class="highlight-lime hero-cursive-accent">control</span><br>de tu operación.
                </h1>''',
        content
    )

    content = re.sub(
        r'<p class="hero-description">[\s\S]*?</p>',
        '''<p class="hero-description">
                    Tú decides qué acciones se resuelven de forma automática y cuáles requieren tu visto bueno. Agentes autónomos que atienden a tus clientes, verifican identidad y ejecutan procesos reales las 24 horas del día.
                </p>''',
        content,
        count=1
    )

    # Hero Benefits Row
    content = re.sub(
        r'<span class="hero-benefit-text">Cobertura total, sin turnos,<br>sin tiempo de inactividad\.</span>',
        '<span class="hero-benefit-text">Cobertura 24/7 sin turnos,<br>sin pausas ni demoras.</span>',
        content
    )
    content = re.sub(
        r'<span class="hero-benefit-text">Voz, SMS y WhatsApp:<br>un equipo unificado</span>',
        '<span class="hero-benefit-text">En tu web y canales:<br>un equipo unificado</span>',
        content
    )
    content = re.sub(
        r'<span class="hero-benefit-text">Citas confirmadas en tiempo real,<br>sin trabajo manual\.</span>',
        '<span class="hero-benefit-text">Procesos resueltos al instante,<br>sin trabajo manual.</span>',
        content
    )

    # 3. Problem Section
    content = re.sub(
        r'<h2 class="section-title">La crisis invisible de la administración clínica</h2>',
        '<h2 class="section-title">El cuello de botella de la atención operativa</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Hasta el 60% de los ingresos potenciales[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Hasta el 70% del tiempo de tu equipo se consume respondiendo las mismas preguntas, agendando citas a mano y actualizando datos en sistemas.
                    </p>''',
        content
    )
    content = re.sub(
        r'<h3 class="problem-sub-title">El Costo Oculto de la Recepción Tradicional</h3>',
        '<h3 class="problem-sub-title">El costo oculto de la atención manual</h3>',
        content
    )

    # 4 Cards in problem
    content = re.sub(
        r'<div class="spotlight-stat-value">51%</div>[\s\S]*?<p class="spotlight-stat-desc">[\s\S]*?</p>',
        '''<div class="spotlight-stat-value">58%</div>
                                    <p class="spotlight-stat-desc">
                                        Más del 50% de las solicitudes llegan fuera del horario laboral. Si un cliente no obtiene respuesta ni confirmación inmediata, busca otra alternativa en minutos.
                                    </p>''',
        content
    )

    content = re.sub(
        r'<div class="spotlight-stat-value">42%</div>[\s\S]*?<p class="spotlight-stat-desc">[\s\S]*?</p>',
        '''<div class="spotlight-stat-value">40%</div>
                                    <p class="spotlight-stat-desc">
                                        El 40% del tiempo de los operadores se pierde en tareas repetitivas como cambiar correos, verificar disponibilidad o enviar enlaces que una máquina puede resolver al instante.
                                    </p>''',
        content
    )

    content = re.sub(
        r'<div class="spotlight-stat-value">Presupuestos en el olvido</div>[\s\S]*?<p class="spotlight-stat-desc">[\s\S]*?</p>',
        '''<div class="spotlight-stat-value">Solicitudes sin resolver</div>
                                    <p class="spotlight-stat-desc">
                                        Clientes que inician un proceso y abandonan porque nadie les confirma o porque el operador tarda horas en revisar la agenda o el sistema.
                                    </p>''',
        content
    )

    content = re.sub(
        r'<div class="spotlight-stat-value">Hasta un 35%</div>[\s\S]*?<p class="spotlight-stat-desc">[\s\S]*?</p>',
        '''<div class="spotlight-stat-value">Hasta un 30%</div>
                                    <p class="spotlight-stat-desc">
                                        La falta de confirmaciones y recordatorios inmediatos genera inasistencias y citas canceladas de última hora, dejando espacios vacíos irrecuperables.
                                    </p>''',
        content
    )

    # Subseccion 2 bots
    content = re.sub(
        r'<h3 class="problem-card-title">La falacia de los chatbots convencionales</h3>',
        '<h3 class="problem-card-title">La limitación de los chatbots convencionales</h3>',
        content
    )
    content = re.sub(
        r'<h4 class="problem-item-title">Sistemas telefónicos robóticos frustrantes</h4>',
        '<h4 class="problem-item-title">Sistemas robóticos que solo emiten texto</h4>',
        content
    )
    content = re.sub(
        r'<span class="problem-item-tag">Árboles rígidos</span>',
        '<span class="problem-item-tag">Sin acción</span>',
        content
    )
    content = re.sub(
        r'<p class="problem-item-desc">Los letreros que dicen "Pulse 1 para citas"[\s\S]*?</p>',
        '<p class="problem-item-desc">Los chatbots tradicionales solo repiten párrafos de texto. Le dicen al usuario "ve a configuración", pero son incapaces de ejecutar el cambio por él.</p>',
        content
    )

    content = re.sub(
        r'<h4 class="problem-item-title">Capacidades de acción cero</h4>',
        '<h4 class="problem-item-title">Árboles rígidos y respuestas prefabricadas</h4>',
        content
    )
    content = re.sub(
        r'<span class="problem-item-tag">Sin ejecución</span>',
        '<span class="problem-item-tag">Flujos cerrados</span>',
        content
    )
    content = re.sub(
        r'<p class="problem-item-desc">Los bots básicos solo emiten texto estático[\s\S]*?</p>',
        '<p class="problem-item-desc">Obligan al usuario a presionar botones que no resuelven lo que realmente necesita, dañando la imagen de tu empresa.</p>',
        content
    )

    content = re.sub(
        r'<h4 class="problem-item-title">Integración de telefonía y voz cero</h4>',
        '<h4 class="problem-item-title">Cero integración con tus sistemas</h4>',
        content
    )
    content = re.sub(
        r'<span class="problem-item-tag">Sin línea telefónica</span>',
        '<span class="problem-item-tag">Aislados</span>',
        content
    )
    content = re.sub(
        r'<p class="problem-item-desc">Cuando se enfrentan a dudas médicas o a un dolor agudo[\s\S]*?</p>',
        '<p class="problem-item-desc">No consultan tu base de datos, no verifican disponibilidad real ni ejecutan acciones en tus herramientas de trabajo.</p>',
        content
    )

    content = re.sub(
        r'<h4 class="problem-item-title">Alucinaciones clínicas y responsabilidad</h4>',
        '<h4 class="problem-item-title">Falta de control y riesgo de alucinación</h4>',
        content
    )
    content = re.sub(
        r'<span class="problem-item-tag">Riesgo legal</span>',
        '<span class="problem-item-tag">Sin gobernanza</span>',
        content
    )
    content = re.sub(
        r'<p class="problem-item-desc">Los sistemas de IA no supervisados inventan precios[\s\S]*?</p>',
        '<p class="problem-item-desc">Los modelos sin supervisión técnica inventan información o condiciones comerciales no autorizadas por tu negocio.</p>',
        content
    )

    # 4. How it works
    content = re.sub(
        r'<h2 class="section-title">Arquitectura de Operación Autónoma</h2>',
        '<h2 class="section-title">Aumenta tu capacidad operativa con soluciones a tu medida</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Delega la fricción administrativa[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Elige las soluciones que mejor se ajustan a tu negocio. En tres pasos tienes a tu agente operando con tus reglas.
                    </p>''',
        content
    )

    # Steps
    content = re.sub(
        r'<span class="step-name">Conecta con Firby</span>',
        '<span class="step-name">Instala con una sola línea</span>',
        content
    )
    content = re.sub(
        r'<p class="step-desc">\s*Conectamos tus líneas telefónicas existentes[\s\S]*?</p>',
        '''<p class="step-desc">
                                Pega el script en tu sitio web en menos de 3 minutos. Sin configuraciones complejas, sin servidores y sin depender de aprobaciones externas.
                            </p>''',
        content
    )

    content = re.sub(
        r'<span class="step-name">Delega la atención</span>',
        '<span class="step-name">Define las acciones permitidas</span>',
        content
    )
    content = re.sub(
        r'<p class="step-desc">\s*Firby aprende tus especialidades[\s\S]*?</p>',
        '''<p class="step-desc">
                                Tú decides qué herramientas puede usar el agente: agendar citas, actualizar datos, consultar información o solicitar aprobación para casos especiales.
                            </p>''',
        content
    )

    content = re.sub(
        r'<span class="step-name">Crece sin límites</span>',
        '<span class="step-name">Opera con total tranquilidad</span>',
        content
    )
    content = re.sub(
        r'<p class="step-desc">\s*Tu clínica atiende, filtra, agenda[\s\S]*?</p>',
        '''<p class="step-desc">
                                Firby atiende a tus usuarios, resuelve solicitudes y te envía alertas por Telegram para autorizar cualquier excepción con un solo clic.
                            </p>''',
        content
    )

    # 5. Digital team / Capabilities
    content = re.sub(
        r'<h2 class="section-title">Tu equipo digital especializado</h2>',
        '<h2 class="section-title">Soluciones operativas diseñadas para tu negocio</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Empleados digitales autónomos, capacitados en protocolos clínicos[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Capacidades autónomas creadas para integrarse a tus procesos existentes y multiplicar el rendimiento de tu equipo humano.
                    </p>''',
        content
    )

    # Card 1: Valeria -> Front-desk
    content = re.sub(
        r'<h3 class="team-name">Valeria</h3>\s*<span class="team-role role-valeria">[\s\S]*?</span>',
        '''<h3 class="team-name">Atención y Agendamiento</h3>
                                <span class="team-role role-valeria">Operador Front-Desk 24/7</span>''',
        content
    )
    content = re.sub(
        r'<p class="team-desc">\s*Contesta las llamadas entrantes con voz humana[\s\S]*?</p>',
        '''<p class="team-desc">
                            Atiende a los visitantes en tu sitio web en tiempo real. Responde consultas frecuentes, verifica disponibilidad en Google Calendar y agenda citas confirmadas sin intervención humana.
                        </p>''',
        content
    )
    content = re.sub(
        r'<span class="capsule-label" id="voice-text">Escucha a Valeria \(demostración de voz\)</span>',
        '<span class="capsule-label" id="voice-text">Demostración de atención interactiva</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Programación autónoma</span>',
        '<span class="spec-label">Agendamiento en Google Calendar</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Latencia de voz &lt;400 ms</span>',
        '<span class="spec-label">Respuesta inmediata en &lt;400 ms</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Confirmaciones instantáneas por SMS</span>',
        '<span class="spec-label">Confirmaciones y recordatorios</span>',
        content
    )

    # Card 2: Kroma -> Payments & Confirmation
    content = re.sub(
        r'<h3 class="team-name">Kroma</h3>\s*<span class="team-role role-kroma">[\s\S]*?</span>',
        '''<h3 class="team-name">Gestión de Pagos</h3>
                                <span class="team-role role-kroma">Recaudo y Verificación de Anticipos</span>''',
        content
    )
    content = re.sub(
        r'<p class="team-desc">\s*Especialista en la aceptación de casos de alto costo[\s\S]*?</p>',
        '''<p class="team-desc">
                            Genera enlaces seguros de pago para reservas y pedidos. Valida el estado de la transacción y confirma el servicio sin que el operador tenga que revisar el extracto bancario.
                        </p>''',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Enlaces de pago Wompi, PSE y Nequi</span>',
        '<span class="spec-label">Enlaces de pago Wompi, PSE y tarjetas</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Manejo de objeciones</span>',
        '<span class="spec-label">Confirmación automática de abonos</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Reactivación de pacientes inactivos</span>',
        '<span class="spec-label">Seguimiento de cotizaciones pendientes</span>',
        content
    )

    # Card 3: Cyro -> Gobernanza y Validación
    content = re.sub(
        r'<h3 class="team-name">Cyro</h3>\s*<span class="team-role role-cyro">[\s\S]*?</span>',
        '''<h3 class="team-name">Gobernanza y Validación</h3>
                                <span class="team-role role-cyro">Gestión Segura de Solicitudes</span>''',
        content
    )
    content = re.sub(
        r'<p class="team-desc">\s*Evalúa los síntomas del paciente[\s\S]*?</p>',
        '''<p class="team-desc">
                            Verifica la identidad del usuario antes de ejecutar cambios sensibles como correo o teléfono. Si una solicitud no está en la lista permitida, la remite al operador humano.
                        </p>''',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Triaje clínico</span>',
        '<span class="spec-label">Validación previa de identidad</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Seguridad de grado médico</span>',
        '<span class="spec-label">Guardrails y listas blancas de acción</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Alertas médicas urgentes</span>',
        '<span class="spec-label">Alertas de visto bueno al operador</span>',
        content
    )

    # Card 4: Cenit -> Automatizaciones
    content = re.sub(
        r'<h3 class="team-name">Cenit</h3>\s*<span class="team-role role-cenit">[\s\S]*?</span>',
        '''<h3 class="team-name">Integración de Flujos</h3>
                                <span class="team-role role-cenit">Conexión con tus Sistemas (n8n y APIs)</span>''',
        content
    )
    content = re.sub(
        r'<p class="team-desc">\s*Asegura las reservas con garantías de tarjeta[\s\S]*?</p>',
        '''<p class="team-desc">
                            Sincroniza la información de cada usuario con tus hojas de Google Sheets, CRM, ERP o base de datos interna de forma instantánea y confiable.
                        </p>''',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Retenciones de tarjeta en Stripe</span>',
        '<span class="spec-label">Conexión nativa con Google Sheets y CRM</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Enlaces de prepago y anticipos</span>',
        '<span class="spec-label">Webhooks automáticos en tiempo real</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Recordatorios inteligentes</span>',
        '<span class="spec-label">Bucle interactivo con Telegram</span>',
        content
    )
    content = re.sub(
        r'<span class="spec-label">Optimización de agenda médica</span>',
        '<span class="spec-label">Registro de auditoría de cada acción</span>',
        content
    )

    # 6. Channels Section
    content = re.sub(
        r'<h2 class="section-title">Dos canales, un mismo equipo digital</h2>',
        '<h2 class="section-title">Tus canales de atención en un solo lugar</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Tus pacientes eligen cómo hablarte[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Tus usuarios eligen por dónde contactarte. Firby responde con la misma precisión y capacidad de acción en cada canal.
                    </p>''',
        content
    )

    content = re.sub(
        r'<h3 class="channel-editorial-title">Recepción de voz</h3>',
        '<h3 class="channel-editorial-title">Widget interactivo en tu sitio web</h3>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Responde llamadas en menos de 400 ms, como una persona real\.</span>',
        '<span class="channel-bullet-text">Se instala con una sola línea de código en cualquier plataforma web.</span>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Realiza el triaje clínico y reserva citas directamente en tu calendario\.</span>',
        '<span class="channel-bullet-text">Resuelve solicitudes y agenda citas directamente en la pantalla del usuario.</span>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Disponible las 24 horas, los 7 días de la semana, sin turnos ni traspasos\.</span>',
        '<span class="channel-bullet-text">Disponible las 24 horas del día, los 7 días de la semana.</span>',
        content
    )
    content = re.sub(
        r'<span>Escucha a Valeria en acción</span>',
        '<span>Probar el widget interactivo</span>',
        content
    )
    content = re.sub(
        r'<span class="voice-live-dot"></span>\s*Línea directa con el paciente',
        '<span class="voice-live-dot"></span> Asistente Web en Vivo',
        content
    )
    content = re.sub(
        r'<strong>Valeria:</strong> "Hola, Metro Dental[\s\S]*?"',
        '<strong>Firby:</strong> "¡Hola! Tengo disponibilidad para tu cita este jueves a las 3:00 PM. ¿Deseas que la reserve a tu nombre?"',
        content
    )

    # Channel row 2
    content = re.sub(
        r'<h3 class="channel-editorial-title">Recepción de WhatsApp y SMS</h3>',
        '<h3 class="channel-editorial-title">Conexión a tus redes y mensajería</h3>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Confirma las citas y envía recordatorios automáticos\.</span>',
        '<span class="channel-bullet-text">Atiende consultas entrantes por WhatsApp e Instagram con la misma inteligencia.</span>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Recibe depósitos mediante un único enlace de pago \(Stripe / Apple Pay\)\.</span>',
        '<span class="channel-bullet-text">Envía enlaces de pago seguros y confirmaciones de servicio al instante.</span>',
        content
    )
    content = re.sub(
        r'<span class="channel-bullet-text">Reactiva a los pacientes inactivos sin que nadie tenga que descolgar el teléfono\.</span>',
        '<span class="channel-bullet-text">Escala casos complejos a tu equipo humano por Telegram o correo electrónico.</span>',
        content
    )
    content = re.sub(
        r'<span>Vea la recuperación del paciente en acción</span>',
        '<span>Conoce cómo se integra a tus canales</span>',
        content
    )

    # 7. Security Section
    content = re.sub(
        r'<h2 class="security-title">\s*La seguridad que exigen los datos de sus pacientes\s*</h2>',
        '''<h2 class="security-title">
                            Encuentra la seguridad y el control que buscas
                        </h2>''',
        content
    )
    content = re.sub(
        r'<p class="security-body">\s*Firby cifra todas las llamadas[\s\S]*?</p>',
        '''<p class="security-body">
                            Nuestra plataforma cuenta con arquitectura de gobernanza estricta. El agente solo ejecuta las acciones que tú autorizas previamente mediante listas blancas y verificación de identidad, protegiendo tus sistemas y los datos de tus usuarios.
                        </p>''',
        content
    )
    content = re.sub(
        r'<span>Cumple con la normativa HIPAA\.</span>\s*<span class="badge-separator">·</span>\s*<span>BAA disponible bajo petición</span>',
        '<span>Gobernanza de Acciones</span><span class="badge-separator">·</span><span>Control y Auditoría en Tiempo Real</span>',
        content
    )
    content = re.sub(
        r'<span>Vea cómo protegemos sus datos clínicos\.</span>',
        '<span>Conoce más sobre nuestra política de seguridad y datos</span>',
        content
    )

    # 8. Pricing Section
    content = re.sub(
        r'<h2 class="section-title">Elige el plan para tu negocio</h2>',
        '<h2 class="section-title">Elige el plan que mejor se ajusta a tu negocio</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Sin contratos de permanencia\. Prueba 7 días gratis[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Sin contratos de permanencia. Prueba 7 días gratis con todas las funciones y cancela cuando quieras.
                    </p>''',
        content
    )

    # Plan Starter
    content = re.sub(
        r'<p class="pricing-tagline">Recepción inteligente en WhatsApp y control de agenda\.</p>',
        '<p class="pricing-tagline">Operador autónomo en tu sitio web con agendamiento y resolución de consultas.</p>',
        content
    )
    content = re.sub(
        r'<div class="pricing-price">\$299\.000</div>\s*<div class="pricing-period">COP / mes <span class="pricing-usd">\(\~\$75 USD\)</span></div>',
        '<div class="pricing-price">$790.000</div><div class="pricing-period">COP / mes <span class="pricing-usd">(~$199 USD)</span></div>',
        content
    )
    content = re.sub(
        r'<span>Atención WhatsApp 24/7</span>',
        '<span>Widget web interactivo (1 línea de código)</span>',
        content
    )
    content = re.sub(
        r'<span>Recordatorios automáticos \(24h y 2h\)</span>',
        '<span>Hasta 500 acciones resueltas al mes</span>',
        content
    )
    content = re.sub(
        r'<span>Seguimiento post-visita \(24h\)</span>',
        '<span>Guardrails de seguridad (Nivel 1 y 2)</span>',
        content
    )
    content = re.sub(
        r'<span>1 Número de WhatsApp</span>',
        '<span>Reporte diario de actividad a tu correo</span>',
        content
    )

    # Plan Pro
    content = re.sub(
        r'<p class="pricing-tagline">Recepción clínica completa, llamadas de voz, triaje clínico y recaudo de depósitos\.</p>',
        '<p class="pricing-tagline">Ecosistema operativo completo con aprobaciones en tiempo real por Telegram y mensajería.</p>',
        content
    )
    content = re.sub(
        r'<div class="pricing-price">\$690\.000</div>\s*<div class="pricing-period">COP / mes <span class="pricing-usd">\(\~\$175 USD\)</span></div>',
        '<div class="pricing-price">$1.990.000</div><div class="pricing-period">COP / mes <span class="pricing-usd">(~$499 USD)</span></div>',
        content
    )
    content = re.sub(
        r'<span><strong>Human-Grade Voice AI \(&lt;400ms Latency\)</strong></span>',
        '<span>Hasta 2.500 acciones resueltas al mes</span>',
        content
    )
    content = re.sub(
        r'<span>1\.200 minutos de voz incluidos al mes</span>',
        '<span>Alertas y aprobación interactiva por Telegram</span>',
        content
    )
    content = re.sub(
        r'<span>Closer de Ventas &amp; Objection Handling</span>',
        '<span>Conexión a WhatsApp e Instagram</span>',
        content
    )
    content = re.sub(
        r'<span>Stripe &amp; Apple Pay Links, PSE, Nequi y Stripe</span>',
        '<span>Integración con Google Sheets y CRM vía n8n</span>',
        content
    )
    content = re.sub(
        r'<span>Urgent Medical Triage &amp; On-Call Doctor Alerts</span>',
        '<span>Guardrails Nivel 3 (Human-in-the-Loop)</span>',
        content
    )

    # Plan Enterprise
    content = re.sub(
        r'<p class="pricing-tagline">Sistema operativo completo con los 5 empleados y automatizaciones\.</p>',
        '<p class="pricing-tagline">Operación a gran escala con agente de voz telefónica y soporte dedicado.</p>',
        content
    )
    content = re.sub(
        r'<div class="pricing-price">\$1\.490\.000</div>\s*<div class="pricing-period">COP / mes <span class="pricing-usd">\(\~\$375 USD\)</span></div>',
        '<div class="pricing-price">$4.800.000</div><div class="pricing-period">COP / mes <span class="pricing-usd">(~$1.200 USD)</span></div>',
        content
    )
    content = re.sub(
        r'<span><strong>Los 5 Empleados Digitales Activos</strong></span>',
        '<span>Acciones operativas de alto volumen</span>',
        content
    )
    content = re.sub(
        r'<span>Creador de Automatizaciones n8n por Chat</span>',
        '<span>Agente de voz telefónica en vivo para conmutador</span>',
        content
    )
    content = re.sub(
        r'<span>Campañas Proactivas de Reactivación</span>',
        '<span>Instancia de servidor dedicada y aislada</span>',
        content
    )
    content = re.sub(
        r'<span>Soporte con Documentos PDF Ilimitados</span>',
        '<span>Conectores personalizados a tus APIs y ERP</span>',
        content
    )
    content = re.sub(
        r'<span>Soporte VIP Dedicado 24/7</span>',
        '<span>Acuerdo de nivel de servicio (SLA) 99.9%</span>',
        content
    )

    content = re.sub(
        r'<span class="callout-pill">ROI</span> <strong>Retorno de Inversión:</strong> El Plan Pro cuesta menos del 25%[\s\S]*?demoras\.',
        '<span class="callout-pill">ROI</span> <strong>Retorno de Inversión:</strong> El Plan Starter cuesta menos de la mitad del salario de un operador en Colombia, operando 24/7 sin ausencias, demoras ni cargas prestacionales.',
        content
    )

    # 9. Mockup section
    content = re.sub(
        r'<h2 class="section-title">Interacción clínica real: desde la primera consulta hasta el depósito\.</h2>',
        '<h2 class="section-title">Resolución de solicitudes en tiempo real: de la consulta a la acción.</h2>',
        content
    )
    content = re.sub(
        r'<p class="section-subtitle">\s*Observa cómo Firby evalúa las necesidades del paciente[\s\S]*?</p>',
        '''<p class="section-subtitle">
                        Observa cómo Firby verifica los datos del usuario, consulta disponibilidad y completa la acción en menos de un minuto.
                    </p>''',
        content
    )
    content = re.sub(
        r'<span class="phone-user-name">Valeria \(Recepción Odontología & Estética\)</span>',
        '<span class="phone-user-name">Firby (Operador de Atención)</span>',
        content
    )
    content = re.sub(
        r'<span class="phone-user-status">en línea • Práctica autónoma con IA</span>',
        '<span class="phone-user-status">en línea • Operador autónomo activo</span>',
        content
    )

    # Chat conversation mockup
    old_chat_body = r'<div class="phone-chat-body">[\s\S]*?</div>\s*</div>\s*</div>\s*</section>'
    new_chat_body = '''<div class="phone-chat-body">
                        <!-- Message 1 (User) -->
                        <div class="chat-bubble user">
                            ¡Hola! Quisiera agendar una cita para este jueves por la tarde y actualizar mi correo registrado.
                        </div>

                        <!-- Message 2 (Firby) -->
                        <div class="chat-bubble bot">
                            ¡Hola! Con gusto. Para el jueves tengo disponibilidad a las 3:15 PM o a las 4:45 PM. Y respecto a tu correo, por seguridad indícame cuál es tu correo actual y el nuevo que deseas registrar.
                        </div>

                        <!-- Message 3 (User) -->
                        <div class="chat-bubble user">
                            Las 3:15 PM está perfecto. Mi correo actual es carlos.m@gmail.com y el nuevo es carlos@empresa.com.
                        </div>

                        <!-- Message 4 (Firby + Action confirmation) -->
                        <div class="chat-bubble bot">
                            Listo, tu cita para el jueves a las 3:15 PM quedó confirmada en agenda. Tu correo fue actualizado a carlos@empresa.com y te enviamos la confirmación. ¡Te esperamos!
                            <div class="chat-payment-btn" onclick="window.location.href='/sign-up'">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                <span>Ver confirmación de cita en línea</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>'''
    content = re.sub(old_chat_body, new_chat_body, content)

    # 10. Final CTA
    content = re.sub(
        r'<h2 class="cta-final-title">El sistema operativo autónomo que llena tu agenda y multiplica la rentabilidad de tu clínica</h2>',
        '<h2 class="cta-final-title">El operador autónomo que resuelve solicitudes y libera a tu equipo de trabajo</h2>',
        content
    )
    content = re.sub(
        r'<p class="cta-final-sub">[\s\S]*?</p>',
        '''<p class="cta-final-sub">
                            Prueba piloto de 7 días con acompañamiento. Sin contratos de permanencia. Instalación en tu sitio web en 3 minutos.
                        </p>''',
        content
    )

    # 11. Footer
    content = re.sub(
        r'<p class="footer-desc">[\s\S]*?</p>',
        '''<p class="footer-desc">
                        Automatización operativa inteligente para empresas y servicios en América Latina. Reemplazamos fricción manual por eficiencia.
                    </p>''',
        content
    )

    return content

files_to_update = [
    "/home/ubuntu/firby/src/interfaces/web/static/firby-landing-es.html",
    "/home/ubuntu/firby/src/interfaces/web/static/firby-landing.html",
    "/home/ubuntu/firby/instances/clinica-de-las-americas/src/interfaces/web/static/firby-landing-es.html",
    "/home/ubuntu/firby/instances/clinica-de-las-americas/src/interfaces/web/static/firby-landing.html"
]

for fpath in files_to_update:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            c = f.read()
        updated = update_html(c)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"Successfully updated {fpath}")
    except Exception as e:
        print(f"Error on {fpath}: {e}")

