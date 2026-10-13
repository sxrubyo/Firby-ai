"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  PiCopyLight,
  PiCheckLight,
  PiPaperPlaneTiltLight,
  PiArrowUpRightLight,
  PiXLight,
  PiGiftLight,
  PiRobotLight,
  PiSlidersLight,
  PiGitBranchLight,
  PiGlobeLight,
  PiArrowRightLight,
} from "react-icons/pi";
import StarBorder from "./StarBorder";
import { MagicBento, MagicBentoCard } from "./MagicBento";
import { useTheme } from "./theme-provider";

interface LeadItem {
  id: string | number;
  name: string;
  phone: string;
  inquiry: string;
  time_ago: string;
  status: string;
}

export function Dashboard() {
  const [userName, setUserName] = useState<string>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("firby_user_name") || localStorage.getItem("firby_user_email") || "";
      if (stored) {
        if (stored.toLowerCase().includes("sxrubyo") || stored.toLowerCase().includes("santiago")) {
          return "Santiago";
        }
        return stored.includes("@")
          ? stored.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
          : stored.split(" ")[0];
      }
    }
    return "Santiago";
  });
  const [copiedSnippet, setCopiedSnippet] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [showTrialBanner, setShowTrialBanner] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("firby_hide_trial_banner") !== "true";
    }
    return true;
  });
  const { isDark } = useTheme();
  const [trialEndDate, setTrialEndDate] = useState<string>("11 de octubre");

  const handleDismissTrialBanner = () => {
    setShowTrialBanner(false);
    try {
      localStorage.setItem("firby_hide_trial_banner", "true");
    } catch (e) {}
  };

  const [showHeroCard, setShowHeroCard] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      try {
        sessionStorage.removeItem("firby_hide_hero_card");
        localStorage.removeItem("firby_hide_hero_card");
      } catch (e) {}
      return sessionStorage.getItem("firby_hide_hero_card_v2") !== "true";
    }
    return true;
  });

  const handleDismissHeroCard = () => {
    setShowHeroCard(false);
    try {
      sessionStorage.setItem("firby_hide_hero_card_v2", "true");
    } catch (e) {}
  };

  // Metricas de negocio
  const [metrics, setMetrics] = useState({
    web_conversations: 25,
    web_today: 18,
    confirmed_appointments: 18,
    captured_leads: 42,
    saved_hours: "32.5 hrs"
  });

  // Contactos registrados en la web
  const [leads, setLeads] = useState<LeadItem[]>([
    {
      id: "lead-1",
      name: "Carlos Rodríguez",
      phone: "+57 310 987 6543",
      inquiry: "Cotización de procedimiento y disponibilidad",
      time_ago: "Hace 14 min",
      status: "Pendiente"
    },
    {
      id: "lead-2",
      name: "Diana Salazar",
      phone: "+57 315 456 7890",
      inquiry: "Consulta de horarios de atención y sedes",
      time_ago: "Hace 42 min",
      status: "Atendido"
    },
    {
      id: "lead-3",
      name: "Felipe Morales",
      phone: "+57 301 223 3445",
      inquiry: "Preguntó por medios de pago y convenios",
      time_ago: "Hace 2 hrs",
      status: "Atendido"
    },
    {
      id: "lead-4",
      name: "Camila Restrepo",
      phone: "+57 320 889 9001",
      inquiry: "Solicitud de cita para valoración general",
      time_ago: "Hace 3 hrs",
      status: "Cita agendada"
    }
  ]);

  const widgetSnippet = `<!-- Firby · Atención en Sitio Web -->\n<script\n  src="https://firbyai.com/widget.js"\n  data-firby-id="org_clinica_americas"\n  async>\n</script>`;

  useEffect(() => {
    try {
      const storedTrialDate = localStorage.getItem("firby_trial_end_date");
      if (storedTrialDate) {
        setTrialEndDate(storedTrialDate);
      } else {
        setTrialEndDate("11 de octubre");
      }
    } catch (e) {
      setTrialEndDate("11 de octubre");
    }

    try {
      const storedName = localStorage.getItem("firby_user_name") || "";
      const storedEmail = localStorage.getItem("firby_user_email") || "";
      if (storedName.toLowerCase().includes("sxrubyo") || storedEmail.toLowerCase().includes("sxrubyo") || storedName.toLowerCase().includes("santiago")) {
        setUserName("Santiago");
      } else if (storedName) {
        setUserName(storedName.split(" ")[0]);
      }
    } catch (e) {}

    const fetchUserProfile = async () => {
      try {
        const token = localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "";
        const email = localStorage.getItem("firby_user_email") || "";
        const res = await fetch("/api/user/profile", {
          headers: {
            "x-master-key": token,
            "x-user-email": email,
          },
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.name) {
            const isSanti = data.name.toLowerCase().includes("sxrubyo") || (data.email && data.email.toLowerCase().includes("sxrubyo")) || data.name.toLowerCase().includes("santiago");
            const finalName = isSanti ? "Santiago" : data.name.split(" ")[0];
            setUserName(finalName);
            localStorage.setItem("firby_user_name", finalName);
            if (data.email) localStorage.setItem("firby_user_email", data.email);
            if (data.avatar) localStorage.setItem("firby_user_avatar", data.avatar);
          }
        }
      } catch (e) {}
    };
    fetchUserProfile();

    fetchData();

    // Asegurar que ninguna instancia residual de Lenis intercepte el scroll de 2 dedos / rueda
    if (typeof window !== "undefined") {
      try {
        if ((window as any).__firbyLenis && typeof (window as any).__firbyLenis.destroy === "function") {
          (window as any).__firbyLenis.destroy();
          (window as any).__firbyLenis = null;
        }
        if ((window as any).lenis && typeof (window as any).lenis.destroy === "function") {
          (window as any).lenis.destroy();
          (window as any).lenis = null;
        }
        if ((window as any).FirbyMotionEngine && typeof (window as any).FirbyMotionEngine.destroy === "function") {
          (window as any).FirbyMotionEngine.destroy();
        }
      } catch (_) {}
    }

    // Cargar el widget oficial (Modo solo chat directo, compacto)
    const scriptId = "firby-landing-widget-script";
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = "/widget.js?v=20260922_noscroll_hijack";
      script.async = true;
      script.setAttribute("data-firby-id", "firby_workspace");
      script.setAttribute("data-title", "Firby");
      script.setAttribute("data-launcher", "chat");
      document.body.appendChild(script);
    }
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const getAuthHeaders = () => {
    const token = typeof window !== "undefined"
      ? localStorage.getItem("firby_master_key") || localStorage.getItem("dev_master_key") || "dev_master_key_preview"
      : "dev_master_key_preview";
    const email = typeof window !== "undefined" ? localStorage.getItem("firby_user_email") || "" : "";
    return {
      "x-master-key": token,
      "x-user-email": email,
      "Content-Type": "application/json"
    };
  };

  const fetchData = async () => {
    try {
      const res = await fetch("/api/workspace/stats", { headers: getAuthHeaders() });
      if (res.ok) {
        const json = await res.json();
        if (json.ok) {
          setMetrics((prev) => ({
            ...prev,
            web_conversations: json.conversations > 0 ? json.conversations : prev.web_conversations,
            confirmed_appointments: json.appointments > 0 ? json.appointments : prev.confirmed_appointments,
          }));
        }
      }
    } catch (e) {}
  };

  const copyWidgetCode = () => {
    navigator.clipboard.writeText(widgetSnippet);
    setCopiedSnippet(true);
    showToast("Código copiado al portapapeles.");
    setTimeout(() => setCopiedSnippet(false), 2500);
  };

  const openPreview = () => {
    const widgetBtn = document.getElementById("bws-hw-btn") || document.getElementById("firby-launcher-btn");
    if (widgetBtn) {
      widgetBtn.click();
    } else {
      showToast("Abre el botón de atención en la esquina inferior");
    }
  };

  const firstName = (userName || "").trim().split(" ")[0] || "Santiago";

  return (
    <div className="w-full max-w-5xl mx-auto flex flex-col gap-6 sm:gap-8 font-sans pb-16 px-4 sm:px-6">
      {/* MENSAJE TOAST DISCRETO */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 px-3.5 py-2 rounded shadow-md text-[11px] font-general font-medium border border-neutral-700 dark:border-neutral-200">
          {toastMessage}
        </div>
      )}

      {/* AVISO: PRUEBA GRATUITA CON STARBORDER (REACT BITS) */}
      {showTrialBanner && (
        <StarBorder
          as="div"
          className="w-full"
          color={isDark ? "#b9fa01" : "#84cc16"}
          speed="5s"
          thickness={1}
          backgroundColor={isDark ? "#111113" : "#ffffff"}
          textColor={isDark ? "#d4d4d8" : "#262626"}
          borderColor={isDark ? "#27272a" : "#e5e5e5"}
        >
          <div className="flex items-center justify-between text-[12px] sm:text-[12.5px] font-general w-full">
            <div className="flex items-center gap-2.5 min-w-0 pr-2">
              <PiGiftLight className={`h-4 w-4 shrink-0 ${isDark ? "text-neutral-200" : "text-neutral-700"}`} />
              <span>
                Tu prueba gratuita finalizará el <span className={`font-medium ${isDark ? "text-white" : "text-neutral-900"}`}>{trialEndDate}</span>.
              </span>
            </div>
            <button
              type="button"
              onClick={handleDismissTrialBanner}
              className={`transition-colors p-1 rounded-sm cursor-pointer shrink-0 ${isDark ? "text-neutral-400 hover:text-white" : "text-neutral-500 hover:text-neutral-900"}`}
              aria-label="Cerrar aviso"
            >
              <PiXLight className="h-3.5 w-3.5 stroke-[1.5]" />
            </button>
          </div>
        </StarBorder>
      )}

      {/* DISEÑO WORKSPACE: DISEÑO EXACTO FIGMA (FRAME 30:2566 "DISEÑO SIN TÍTULO 1") TAL CUAL */}
      {showHeroCard && (
        <div className="relative w-full rounded-2xl sm:rounded-3xl overflow-hidden shadow-sm dark:shadow-[0_14px_35px_rgba(0,0,0,0.55)] border border-neutral-200/80 dark:border-neutral-800 bg-white dark:bg-[#0c0c0e] transition-all">
          <picture>
            <source srcSet="/diseno-workspace.webp?v=figma_30_2566" type="image/webp" />
            <img
              src="/diseno-workspace.png?v=figma_30_2566"
              alt="Tu espacio, un lugar."
              width={6278}
              height={1956}
              className="w-full h-auto block select-none"
              loading="eager"
              fetchPriority="high"
              decoding="async"
            />
          </picture>

          {/* BOTÓN X TIPO ANUNCIO EN LA ESQUINA DERECHA (SOLO LA X SIN CÍRCULO) */}
          <button
            type="button"
            onClick={handleDismissHeroCard}
            className="absolute top-2.5 right-2.5 sm:top-3.5 sm:right-3.5 z-20 p-1 text-neutral-400 hover:text-neutral-900 dark:text-neutral-500 dark:hover:text-white transition-colors cursor-pointer focus:outline-none"
            aria-label="Cerrar anuncio"
            title="Cerrar"
          >
            <PiXLight className="h-4 w-4 sm:h-5 sm:w-5 stroke-[2]" />
          </button>

          {/* ISOTIPO FIRBY EN FOOTER */}
          <Link
            href="/workspace"
            className="absolute left-[6.8%] top-[82%] w-[3.5%] h-[11%] rounded-full cursor-pointer hover:opacity-85 focus:outline-none"
            aria-label="Ir a tu espacio"
            title="Firby"
          />

          {/* ENLACES LEGALES INTERACTIVOS */}
          <a
            href="https://firbyai.com/terms"
            target="_blank"
            rel="noopener noreferrer"
            className="absolute left-[10.5%] top-[84%] w-[2.8%] h-[8%] rounded-sm cursor-pointer hover:opacity-75 focus:outline-none"
            aria-label="Términos y Condiciones (T&T)"
            title="T&T"
          />
          <a
            href="https://firbyai.com/privacy"
            target="_blank"
            rel="noopener noreferrer"
            className="absolute left-[13.6%] top-[84%] w-[9.0%] h-[8%] rounded-sm cursor-pointer hover:opacity-75 focus:outline-none"
            aria-label="Política de Privacidad"
            title="Política de Privacidad"
          />
          <a
            href="https://firbyai.com/data-agreement"
            target="_blank"
            rel="noopener noreferrer"
            className="absolute left-[23.3%] top-[84%] w-[8.0%] h-[8%] rounded-sm cursor-pointer hover:opacity-75 focus:outline-none"
            aria-label="Acuerdo de Datos"
            title="Acuerdo de Datos"
          />
        </div>
      )}

      {/* 1. CABECERA PRINCIPAL (CENTRADA EN DESKTOP Y MÓVIL: ¡HOLA SANTIAGO! + SUBTÍTULO) */}
      <div className="flex pt-4 pb-7 border-b border-neutral-200/80 dark:border-neutral-800 text-center flex-col items-center justify-center">
        <h1 className="font-neue text-2xl sm:text-3xl md:text-4xl font-medium tracking-tight text-neutral-900 dark:text-neutral-100">
          ¡Hola {firstName}!
        </h1>
        <p className="font-general text-[12.5px] sm:text-[13.5px] text-neutral-500 dark:text-neutral-400 mt-2 leading-relaxed max-w-xl px-2">
          Aquí tienes el control de las citas, consultas y contactos recibidos en tu sitio web.
        </p>
      </div>

      {/* 2. BLOQUES DE ACCIÓN RÁPIDA (MAGIC BENTO: TILT, SPOTLIGHT, RESPLANDOR VERDE OSCURO SUTIL) */}
      <MagicBento
        className="grid grid-cols-2 gap-3.5 sm:gap-4 md:gap-5"
        enableSpotlight={true}
        enableBorderGlow={true}
        enableTilt={true}
        enableMagnetism={true}
        enableStars={false}
        clickEffect={true}
        spotlightRadius={260}
        glowColor="20, 83, 45"
      >
        {/* BLOQUE 1: CREA TU PRIMER AGENTE */}
        <MagicBentoCard
          as={Link}
          href="/panel/instances/"
          className="group p-4 sm:p-5 md:p-6 rounded-xl border border-neutral-200/90 dark:border-neutral-800/90 bg-white dark:bg-[#0c0c0e] hover:border-neutral-300/90 dark:hover:border-neutral-700/90 flex flex-col justify-between"
          glowColor="20, 83, 45"
          enableStars={false}
          enableTilt={true}
          enableMagnetism={true}
          enableBorderGlow={true}
        >
          <div>
            <div className="w-10 h-10 sm:w-12 sm:h-12 shrink-0 mb-3 sm:mb-4 transition-transform duration-200 ease-out group-hover:-translate-y-[1.5px]">
              <img
                src="/icons/quick-actions/clay_agent.webp?v=20260922_family"
                alt="Crea tu primer agente"
                width={48}
                height={48}
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="font-neue text-[13.5px] sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100 tracking-tight leading-snug">
              Crea tu primer agente
            </h3>
            <p className="font-general text-[11.5px] sm:text-[12.5px] text-neutral-500 dark:text-neutral-400 mt-1.5 sm:mt-2 leading-relaxed">
              Configura una instancia con objetivos comerciales, sede y reglas de atención para tu sitio web.
            </p>
          </div>
          <div className="mt-4 sm:mt-5 pt-0.5 flex items-center">
            <span className="font-general text-[11px] sm:text-[12px] font-medium text-neutral-900 dark:text-neutral-200 group-hover:underline inline-flex items-center gap-1.5">
              Crear agente
              <PiArrowRightLight className="h-3 w-3 stroke-[2] transition-transform duration-200 group-hover:translate-x-1" />
            </span>
          </div>
        </MagicBentoCard>

        {/* BLOQUE 2: PERSONALIZA A TU AGENTE */}
        <MagicBentoCard
          as={Link}
          href="/workspace/knowledge/"
          className="group p-4 sm:p-5 md:p-6 rounded-xl border border-neutral-200/90 dark:border-neutral-800/90 bg-white dark:bg-[#0c0c0e] hover:border-neutral-300/90 dark:hover:border-neutral-700/90 flex flex-col justify-between"
          glowColor="20, 83, 45"
          enableStars={false}
          enableTilt={true}
          enableMagnetism={true}
          enableBorderGlow={true}
        >
          <div>
            <div className="w-10 h-10 sm:w-12 sm:h-12 shrink-0 mb-3 sm:mb-4 transition-transform duration-200 ease-out group-hover:-translate-y-[1.5px]">
              <img
                src="/icons/quick-actions/clay_customize.webp?v=20260922_family"
                alt="Personaliza a tu agente"
                width={48}
                height={48}
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="font-neue text-[13.5px] sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100 tracking-tight leading-snug">
              Personaliza a tu agente
            </h3>
            <p className="font-general text-[11.5px] sm:text-[12.5px] text-neutral-500 dark:text-neutral-400 mt-1.5 sm:mt-2 leading-relaxed">
              Define el tono de voz, instrucciones estrictas y sube documentos para responder sin alucinaciones.
            </p>
          </div>
          <div className="mt-4 sm:mt-5 pt-0.5 flex items-center">
            <span className="font-general text-[11px] sm:text-[12px] font-medium text-neutral-900 dark:text-neutral-200 group-hover:underline inline-flex items-center gap-1.5">
              Personalizar directrices
              <PiArrowRightLight className="h-3 w-3 stroke-[2] transition-transform duration-200 group-hover:translate-x-1" />
            </span>
          </div>
        </MagicBentoCard>

        {/* BLOQUE 3: AUTOMATIZA CITAS Y FLUJOS */}
        <MagicBentoCard
          as={Link}
          href="/workspace/inbox/"
          className="group p-4 sm:p-5 md:p-6 rounded-xl border border-neutral-200/90 dark:border-neutral-800/90 bg-white dark:bg-[#0c0c0e] hover:border-neutral-300/90 dark:hover:border-neutral-700/90 flex flex-col justify-between"
          glowColor="20, 83, 45"
          enableStars={false}
          enableTilt={true}
          enableMagnetism={true}
          enableBorderGlow={true}
        >
          <div>
            <div className="w-10 h-10 sm:w-12 sm:h-12 shrink-0 mb-3 sm:mb-4 transition-transform duration-200 ease-out group-hover:-translate-y-[1.5px]">
              <img
                src="/icons/quick-actions/clay_workflows.webp?v=20260922_family"
                alt="Automatiza citas y flujos"
                width={48}
                height={48}
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="font-neue text-[13.5px] sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100 tracking-tight leading-snug">
              Automatiza citas y flujos
            </h3>
            <p className="font-general text-[11.5px] sm:text-[12.5px] text-neutral-500 dark:text-neutral-400 mt-1.5 sm:mt-2 leading-relaxed">
              Conecta Google Calendar para citas en tiempo real y diseña flujos de automatización en el lienzo visual.
            </p>
          </div>
          <div className="mt-4 sm:mt-5 pt-0.5 flex items-center">
            <span className="font-general text-[11px] sm:text-[12px] font-medium text-neutral-900 dark:text-neutral-200 group-hover:underline inline-flex items-center gap-1.5">
              Abrir flujos de trabajo
              <PiArrowRightLight className="h-3 w-3 stroke-[2] transition-transform duration-200 group-hover:translate-x-1" />
            </span>
          </div>
        </MagicBentoCard>

        {/* BLOQUE 4: DESPLIEGA EN TU SITIO WEB */}
        <MagicBentoCard
          as="button"
          type="button"
          onClick={() => {
            const el = document.getElementById("widget-install-section");
            if (el) {
              el.scrollIntoView({ behavior: "smooth" });
            }
          }}
          className="group p-4 sm:p-5 md:p-6 rounded-xl border border-neutral-200/90 dark:border-neutral-800/90 bg-white dark:bg-[#0c0c0e] hover:border-neutral-300/90 dark:hover:border-neutral-700/90 text-left flex flex-col justify-between cursor-pointer"
          glowColor="20, 83, 45"
          enableStars={false}
          enableTilt={true}
          enableMagnetism={true}
          enableBorderGlow={true}
        >
          <div>
            <div className="w-10 h-10 sm:w-12 sm:h-12 shrink-0 mb-3 sm:mb-4 transition-transform duration-200 ease-out group-hover:-translate-y-[1.5px]">
              <img
                src="/icons/quick-actions/clay_deploy.webp?v=20260922_family"
                alt="Despliega en tu sitio web"
                width={48}
                height={48}
                className="w-full h-full object-contain"
              />
            </div>
            <h3 className="font-neue text-[13.5px] sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100 tracking-tight leading-snug">
              Despliega en tu sitio web
            </h3>
            <p className="font-general text-[11.5px] sm:text-[12.5px] text-neutral-500 dark:text-neutral-400 mt-1.5 sm:mt-2 leading-relaxed">
              Pega una sola línea de script en WordPress, Webflow o Shopify para activar la atención automática en vivo.
            </p>
          </div>
          <div className="mt-4 sm:mt-5 pt-0.5 flex items-center">
            <span className="font-general text-[11px] sm:text-[12px] font-medium text-neutral-900 dark:text-neutral-200 group-hover:underline inline-flex items-center gap-1.5">
              Ver instalación
              <PiArrowRightLight className="h-3 w-3 stroke-[2] transition-transform duration-200 group-hover:translate-x-1" />
            </span>
          </div>
        </MagicBentoCard>
      </MagicBento>

      {/* 3. MÉTRICAS (BLOQUE ÚNICO BLANCO SEMI TRANSPARENTE) */}
      <div className="rounded-xl border border-neutral-200/80 dark:border-neutral-800/80 bg-white/70 dark:bg-neutral-900/40 backdrop-blur-sm p-5 sm:p-6 shadow-[0_2px_8px_rgba(0,0,0,0.02)] dark:shadow-none">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
          {/* MÉTRICA 1 */}
          <div className="flex flex-col space-y-1">
            <span className="font-general text-[11px] font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
              Consultas en la web
            </span>
            <span className="font-mono text-2xl sm:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
              {metrics.web_conversations}
            </span>
            <span className="font-general text-[11.5px] text-neutral-500 dark:text-neutral-400">
              {metrics.web_today} recibidas hoy
            </span>
          </div>

          {/* MÉTRICA 2 */}
          <div className="flex flex-col space-y-1">
            <span className="font-general text-[11px] font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
              Citas confirmadas
            </span>
            <span className="font-mono text-2xl sm:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
              {metrics.confirmed_appointments}
            </span>
            <span className="font-general text-[11.5px] text-neutral-500 dark:text-neutral-400">
              En Google Calendar
            </span>
          </div>

          {/* MÉTRICA 3 */}
          <div className="flex flex-col space-y-1">
            <span className="font-general text-[11px] font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
              Contactos registrados
            </span>
            <span className="font-mono text-2xl sm:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
              {metrics.captured_leads}
            </span>
            <span className="font-general text-[11.5px] text-neutral-500 dark:text-neutral-400">
              Con teléfono verificado
            </span>
          </div>

          {/* MÉTRICA 4 */}
          <div className="flex flex-col space-y-1">
            <span className="font-general text-[11px] font-medium uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
              Tiempo de atención
            </span>
            <span className="font-mono text-2xl sm:text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
              {metrics.saved_hours}
            </span>
            <span className="font-general text-[11.5px] text-neutral-500 dark:text-neutral-400">
              Ahorradas en recepción
            </span>
          </div>
        </div>
      </div>

      {/* 3. TABLA DE CONTACTOS (ESTILO TRANSACCIONES WOMPI: PLANA, AIREADA, CERO SOMBRAS) */}
      <div className="space-y-3 pb-7 border-b border-neutral-200/80 dark:border-neutral-800">
        <div className="flex items-baseline justify-between">
          <div>
            <h2 className="font-neue text-sm sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100">
              Contactos recientes del sitio web
            </h2>
            <p className="font-general text-[12px] text-neutral-500 dark:text-neutral-400 mt-0.5">
              Visitantes que solicitaron información o seguimiento con su número de teléfono.
            </p>
          </div>
          <span className="font-mono text-[11px] text-neutral-400 font-medium">
            {leads.length} contactos
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="border-b border-neutral-200/80 dark:border-neutral-800 font-general uppercase tracking-wider text-[10.5px] text-neutral-400 font-medium">
              <tr>
                <th className="py-2.5 pr-4">Nombre</th>
                <th className="py-2.5 px-4">Teléfono</th>
                <th className="py-2.5 px-4">Consulta o interés</th>
                <th className="py-2.5 px-4">Momento</th>
                <th className="py-2.5 pl-4 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 dark:divide-neutral-850/60 font-general text-[12.5px] text-neutral-800 dark:text-neutral-200">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-neutral-50/70 dark:hover:bg-neutral-900/40 transition-colors">
                  <td className="py-3.5 pr-4 font-neue font-medium text-neutral-900 dark:text-white">
                    {lead.name}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11.5px] text-neutral-500 dark:text-neutral-400">
                    {lead.phone}
                  </td>
                  <td className="py-3.5 px-4 text-neutral-600 dark:text-neutral-300 max-w-md leading-relaxed">
                    {lead.inquiry}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-neutral-400 whitespace-nowrap">
                    {lead.time_ago}
                  </td>
                  <td className="py-3.5 pl-4 text-right whitespace-nowrap">
                    <a
                      href={`https://wa.me/${lead.phone.replace(/[^0-9]/g, "")}?text=Hola%20${encodeURIComponent(lead.name)},%20te%20escribimos%20para%20darle%20seguimiento%20a%20tu%20consulta`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-general text-[11.5px] font-medium text-neutral-900 dark:text-neutral-100 hover:text-black dark:hover:text-white underline underline-offset-4 decoration-neutral-300 dark:decoration-neutral-700 transition-colors"
                    >
                      <span>Escribir</span>
                      <PiArrowUpRightLight className="h-3.5 w-3.5 stroke-[1.5]" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. INSTALACIÓN EN EL SITIO WEB (LIMPIO, MINIMALISTA, CERO CAJAS DE PLANTILLA) */}
      <div className="space-y-3.5" id="widget-install-section">
        <div>
          <h2 className="font-neue text-sm sm:text-[15px] font-medium text-neutral-900 dark:text-neutral-100">
            Instalación en tu sitio web
          </h2>
          <p className="font-general text-[12px] text-neutral-500 dark:text-neutral-400 mt-0.5 leading-normal">
            Pega esta línea de código antes de la etiqueta <code className="px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200 font-mono text-[11px]">&lt;/body&gt;</code> en tu página web, WordPress, Webflow o Shopify para habilitar la atención automática.
          </p>
        </div>

        {/* CÓDIGO PLANO Y TÉCNICO */}
        <div className="rounded-md bg-[#0a0a0c] border border-neutral-800 p-3 sm:p-3.5 font-mono text-[11.5px] text-neutral-200 overflow-x-auto leading-relaxed selection:bg-[#b9fa01]/30 selection:text-[#b9fa01]">
          <pre className="leading-relaxed">
            <code>{widgetSnippet}</code>
          </pre>
        </div>

        {/* ACCIONES TIPO FINTECH */}
        <div className="flex flex-wrap items-center gap-2.5 pt-1">
          <button
            onClick={copyWidgetCode}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-md bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 hover:bg-neutral-800 dark:hover:bg-neutral-100 font-general text-[11.5px] font-medium transition-colors cursor-pointer"
          >
            {copiedSnippet ? <PiCheckLight className="h-3.5 w-3.5 stroke-[2]" /> : <PiCopyLight className="h-3.5 w-3.5 stroke-[1.5]" />}
            <span>{copiedSnippet ? "Copiado" : "Copiar código"}</span>
          </button>

          <a
            href={`mailto:?subject=Código%20de%20instalación%20para%20el%20sitio%20web&body=Hola,%20este%20es%20el%20código%20para%20activar%20el%20módulo%20de%20atención%20en%20nuestro%20sitio%20web:%0A%0A${encodeURIComponent(widgetSnippet)}%0A%0AGracias.`}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-md border border-neutral-300 dark:border-neutral-700 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-800 font-general text-[11.5px] font-medium transition-colors cursor-pointer"
          >
            <PiPaperPlaneTiltLight className="h-3.5 w-3.5 stroke-[1.5]" />
            <span>Enviar a mi desarrollador</span>
          </a>

          <button
            onClick={openPreview}
            className="font-general text-[11.5px] text-neutral-500 hover:text-neutral-900 dark:hover:text-white transition-colors cursor-pointer ml-auto"
          >
            Probar en este navegador
          </button>
        </div>
      </div>
    </div>
  );
}
