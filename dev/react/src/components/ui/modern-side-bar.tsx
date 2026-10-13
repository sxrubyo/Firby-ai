"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname, useRouter } from "next/navigation";
import {
  Home,
  GitBranch,
  Calendar,
  Folder,
  Users2,
  ChevronDown,
  Settings2,
  HelpCircle,
  PanelLeft,
  ChevronRight,
  X,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";

interface SubItem {
  id: string;
  name: string;
  href: string;
}

interface NavItem {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number | string }>;
  href: string;
  subItems: SubItem[];
}

interface SidebarProps {
  className?: string;
  children?: React.ReactNode;
  initialCollapsed?: boolean;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

// 5 SECCIONES PRINCIPALES CON ICONOS PREMIUM Y ESTRUCTURA LIMPIA
const NAV_ITEMS: NavItem[] = [
  {
    id: "home",
    name: "Inicio",
    icon: Home,
    href: "/workspace/",
    subItems: [
      { id: "home-summary", name: "Panel general", href: "/workspace/" },
      { id: "home-metrics", name: "Métricas del negocio", href: "/panel/analytics/" },
    ],
  },
  {
    id: "lifecycle",
    name: "Flujos",
    icon: GitBranch,
    href: "/workspace/inbox/",
    subItems: [
      { id: "flows-knowledge", name: "Base de conocimiento", href: "/workspace/knowledge/" },
    ],
  },
  {
    id: "projects",
    name: "Citas",
    icon: Calendar,
    href: "/workspace/kanban/",
    subItems: [
      { id: "citas-kanban", name: "Tablero de citas", href: "/workspace/kanban/" },
    ],
  },
  {
    id: "library",
    name: "Biblioteca",
    icon: Folder,
    href: "/workspace/library/",
    subItems: [
      { id: "lib-data", name: "Recursos multimedia", href: "/workspace/library/" },
      { id: "lib-docs", name: "Documentos", href: "/panel/documents/" },
    ],
  },
  {
    id: "team",
    name: "Equipo",
    icon: Users2,
    href: "/panel/instances/",
    subItems: [
      { id: "team-staff", name: "Instancias y sedes", href: "/panel/instances/" },
      { id: "team-logs", name: "Registro de actividad", href: "/panel/logs/" },
      { id: "team-lab", name: "Laboratorio de pruebas", href: "/workspace/laboratory/" },
    ],
  },
];

export function Sidebar({
  className = "",
  children,
  initialCollapsed = false,
  isCollapsed: controlledCollapsed,
  onToggleCollapse,
  isMobileOpen = false,
  onCloseMobile,
}: SidebarProps) {
  const [internalCollapsed, setInternalCollapsed] = useState(initialCollapsed);
  const isCollapsed = controlledCollapsed !== undefined ? controlledCollapsed : internalCollapsed;
  const setIsCollapsed = (val: boolean | ((prev: boolean) => boolean)) => {
    if (onToggleCollapse) {
      onToggleCollapse();
    } else {
      setInternalCollapsed(val);
    }
  };
  const [sidebarWidth, setSidebarWidth] = useState(250);
  const [isDragging, setIsDragging] = useState(false);
  const [activeItem, setActiveItem] = useState("home");
  const collapsedNavRef = useRef<HTMLDivElement | null>(null);
  const [collapsedHover, setCollapsedHover] = useState<number | null>(null);

  const getCollapsedIndexAt = (clientY: number) => {
    const items = collapsedNavRef.current?.querySelectorAll(".collapsed-dock-item");
    if (!items?.length) return null;
    let best = 0;
    let gap = Infinity;
    items.forEach((el, i) => {
      const b = el.getBoundingClientRect();
      const d = Math.abs(clientY - (b.top + b.height / 2));
      if (d < gap) {
        gap = d;
        best = i;
      }
    });
    return best;
  };

  // Estado de secciones desplegadas
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    home: false,
    lifecycle: false,
    projects: false,
    library: false,
    team: false,
  });

  const pathname = usePathname();
  const router = useRouter();

  const toggleSection = (sectionKey: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setExpandedSections((prev) => ({
      ...prev,
      [sectionKey]: !prev[sectionKey],
    }));
  };

  useEffect(() => {
    if (pathname?.includes("/workspace/library") || pathname?.includes("/panel/documents")) {
      setActiveItem("library");
      setExpandedSections((prev) => ({ ...prev, library: true }));
    } else if (pathname?.includes("/workspace/kanban")) {
      setActiveItem("projects");
      setExpandedSections((prev) => ({ ...prev, projects: true }));
    } else if (
      pathname?.includes("/panel/instances") ||
      pathname?.includes("/panel/logs") ||
      pathname?.includes("/workspace/laboratory")
    ) {
      setActiveItem("team");
      setExpandedSections((prev) => ({ ...prev, team: true }));
    } else if (
      pathname?.includes("/workspace/inbox") ||
      pathname?.includes("/workspace/knowledge")
    ) {
      setActiveItem("lifecycle");
      setExpandedSections((prev) => ({ ...prev, lifecycle: true }));
    } else if (pathname === "/workspace" || pathname === "/workspace/" || pathname?.includes("/panel/analytics")) {
      setActiveItem("home");
    } else if (pathname?.includes("/settings")) {
      setActiveItem("settings");
    } else if (pathname?.includes("/help")) {
      setActiveItem("help");
    } else {
      setActiveItem("home");
    }
  }, [pathname]);

  // Bloquear scroll de la página de fondo cuando el menú móvil esté abierto
  useEffect(() => {
    if (isMobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileOpen]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = startWidth + (moveEvent.clientX - startX);
      setSidebarWidth(Math.min(360, Math.max(200, newWidth)));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  const handleItemClick = (itemId: string, href: string) => {
    if (onCloseMobile) onCloseMobile();

    if (itemId === "logout") {
      localStorage.removeItem("firby_master_key");
      localStorage.removeItem("dev_master_key");
      localStorage.removeItem("firby_user_email");
      window.location.href = "/sign-in";
      return;
    }

    if (href && href !== "#") {
      router.push(href);
      setActiveItem(itemId);
    }
  };

  // Renderiza las 5 opciones principales
  const renderNavItems = (isMobile: boolean = false) => {
    // MODO COLAPSADO (DESKTOP): Efecto Magnifying Dock por distancia
    if (!isMobile && isCollapsed) {
      return (
        <div
          ref={collapsedNavRef}
          className="space-y-1 py-0.5"
          onPointerMoveCapture={(e) => {
            setCollapsedHover(getCollapsedIndexAt(e.clientY));
          }}
          onPointerLeave={() => {
            setCollapsedHover(null);
          }}
        >
          {NAV_ITEMS.map((item, i) => {
            const Icon = item.icon;
            const isSectionActive =
              activeItem === item.id ||
              item.subItems.some(
                (sub) => pathname === sub.href || (pathname?.replace(/\/$/, "") === sub.href.replace(/\/$/, ""))
              );
            const d = collapsedHover === null ? 99 : Math.abs(i - collapsedHover);
            const spread = 1.4;
            const f = d > spread ? 0 : (1 + Math.cos((Math.PI * d) / (spread + 1))) / 2;
            const scale = 1 + 0.32 * f;

            return (
              <div key={item.id} className="w-full collapsed-dock-item">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button
                      onClick={() => handleItemClick(item.id, item.href)}
                      className="w-full flex flex-col items-center justify-center py-1 px-0.5 group cursor-pointer select-none"
                      title={item.name}
                    >
                      {/* PARTE DONDE SE PRESIONA EL ICONO: CIRCULAR COMPACTO CON RELLENO */}
                      <div
                        className={`
                          w-8 h-8 rounded-full flex items-center justify-center
                          ${
                            isSectionActive
                              ? "bg-[#b9fa01] text-black shadow-xs font-semibold"
                              : "text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-white group-hover:bg-neutral-100 dark:group-hover:bg-neutral-900/60"
                          }
                        `}
                      >
                        <div
                          style={{
                            transform: scale !== 1 ? `scale(${scale})` : "scale(1)",
                            transformOrigin: "center center",
                            transition: "transform 240ms cubic-bezier(0.24, 1.2, 0.32, 1)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Icon className="h-3.5 w-3.5 shrink-0" strokeWidth={isSectionActive ? 1.75 : 1.5} />
                        </div>
                      </div>
                      {/* NOMBRE ABAJITO DE CADA ICONO */}
                      <span
                        className={`
                          mt-1 text-[9px] leading-none tracking-tight text-center truncate max-w-full
                          ${
                            isSectionActive
                              ? "text-neutral-900 dark:text-white font-semibold"
                              : "text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-white font-medium"
                          }
                        `}
                      >
                        {item.name}
                      </span>
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    side="right"
                    align="start"
                    className="w-52 p-1.5 rounded-xl shadow-xl z-50 bg-white dark:bg-[#18181b] border border-neutral-200 dark:border-[#27272a] text-neutral-900 dark:text-neutral-100"
                  >
                    <DropdownMenuItem
                      onClick={() => handleItemClick(item.id, item.href)}
                      className="text-xs cursor-pointer gap-2 font-medium px-2 py-1.5 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800"
                    >
                      <Icon className="h-3.5 w-3.5 text-neutral-500 dark:text-neutral-400" strokeWidth={1.5} />
                      <span>Ir a {item.name}</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="my-1 border-neutral-200 dark:border-[#27272a]" />
                    <div className="px-2 py-1 text-[10px] text-neutral-400 uppercase tracking-wider font-semibold">
                      Opciones
                    </div>
                    {item.subItems.map((sub) => (
                      <DropdownMenuItem
                        key={sub.id}
                        onClick={() => handleItemClick(sub.id, sub.href)}
                        className="text-xs cursor-pointer px-2 py-1.5 rounded-md hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300"
                      >
                        <span>{sub.name}</span>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            );
          })}
        </div>
      );
    }

    // MODO NATURAL / EXPANDIDO: 100% INTACTO
    return (
      <div className="space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isSectionActive =
            activeItem === item.id ||
            item.subItems.some(
              (sub) => pathname === sub.href || (pathname?.replace(/\/$/, "") === sub.href.replace(/\/$/, ""))
            );
          const isExpanded = !!expandedSections[item.id];

        // MODO EXPANDIDO (DESKTOP & MÓVIL)
        return (
          <div key={item.id} className="space-y-0.5">
            <div
              className={`
                flex items-center justify-between w-full rounded-full transition-all group/row
                ${
                  isSectionActive
                    ? "bg-[#b9fa01] text-black shadow-xs font-semibold"
                    : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-900/60 font-medium"
                }
              `}
            >
              <button
                type="button"
                onClick={() => {
                  handleItemClick(item.id, item.href);
                  if (!expandedSections[item.id]) {
                    setExpandedSections((prev) => ({ ...prev, [item.id]: true }));
                  }
                }}
                className="flex-1 flex items-center py-1.5 px-3 space-x-2 text-left cursor-pointer min-w-0"
              >
                <div
                  className={`flex items-center justify-center min-w-[18px] shrink-0 ${
                    isSectionActive ? "text-black" : "text-neutral-500 dark:text-neutral-400 group-hover/row:text-neutral-900 dark:group-hover/row:text-white"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5 shrink-0" strokeWidth={isSectionActive ? 1.75 : 1.5} />
                </div>
                <span className="text-[12px] tracking-tight truncate">{item.name}</span>
              </button>

              {/* CONTROLES A LA DERECHA */}
              <div className="flex items-center shrink-0 pr-1.5">
                <button
                  type="button"
                  onClick={(e) => toggleSection(item.id, e)}
                  className={`
                    p-1 rounded-full transition-colors cursor-pointer shrink-0
                    ${
                      isSectionActive 
                        ? "text-black/80 hover:bg-black/10" 
                        : "text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-200/50 dark:hover:bg-neutral-800"
                    }
                  `}
                  title={isExpanded ? "Ocultar opciones" : "Ver opciones"}
                  aria-label="Ver opciones"
                >
                  <ChevronDown
                    className={`h-3 w-3 transition-transform duration-200 ${
                      isExpanded ? "rotate-180" : "rotate-0"
                    }`}
                    strokeWidth={1.5}
                  />
                </button>
              </div>
            </div>

            {/* Sub-opciones desplegables */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.12 }}
                  className="ml-5 pl-2.5 border-l border-neutral-200 dark:border-neutral-800 space-y-0.5 my-1"
                >
                  {item.subItems.map((sub) => {
                    const isSubActive =
                      isSectionActive &&
                      (pathname === sub.href || (pathname?.replace(/\/$/, "") === sub.href.replace(/\/$/, "")));
                    return (
                      <button
                        key={sub.id}
                        onClick={() => handleItemClick(sub.id, sub.href)}
                        className={`
                          w-full flex items-center py-1.5 px-3 rounded-full text-left text-xs transition-all cursor-pointer
                          ${
                            isSubActive
                              ? "bg-[#b9fa01] text-black font-semibold shadow-xs"
                              : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-900/60"
                          }
                        `}
                      >
                        <span className="truncate">{sub.name}</span>
                      </button>
                    );
                  })}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
};

  // Renderiza Ajustes y Ayuda
  const renderUtilities = (isMobile: boolean = false) => (
    <div className={!isMobile && isCollapsed ? "space-y-2" : "space-y-0.5"}>
      {/* AJUSTES */}
      {!isMobile && isCollapsed ? (
        <button
          onClick={() => handleItemClick("settings", "/settings/")}
          className="w-full flex items-center justify-center py-1 group cursor-pointer transition-all select-none"
          title="Ajustes"
        >
          <div
            className={`
              w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 group-hover:scale-115
              ${
                activeItem === "settings"
                  ? "bg-[#b9fa01] text-black shadow-xs font-semibold"
                  : "text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-white group-hover:bg-neutral-100 dark:group-hover:bg-neutral-900/60"
              }
            `}
          >
            <Settings2 className="h-3.5 w-3.5 shrink-0" strokeWidth={activeItem === "settings" ? 1.75 : 1.5} />
          </div>
        </button>
      ) : (
        <button
          onClick={() => handleItemClick("settings", "/settings/")}
          className={`
            w-full flex items-center py-1.5 px-3 text-left rounded-full transition-all cursor-pointer
            ${
              activeItem === "settings"
                ? "bg-[#b9fa01] text-black font-semibold shadow-xs"
                : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-900/60 font-medium"
            }
          `}
          title="Ajustes"
        >
          <div
            className={`flex items-center justify-center min-w-[18px] mr-2 ${
              activeItem === "settings" ? "text-black" : "text-neutral-500 dark:text-neutral-400"
            }`}
          >
            <Settings2 className="h-3.5 w-3.5 shrink-0" strokeWidth={1.5} />
          </div>
          <span className="text-[12px] tracking-tight">Ajustes</span>
        </button>
      )}

      {/* AYUDA */}
      {!isMobile && isCollapsed ? (
        <button
          onClick={() => handleItemClick("help", "/help/")}
          className="w-full flex items-center justify-center py-1 group cursor-pointer transition-all select-none"
          title="Ayuda"
        >
          <div
            className={`
              w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 group-hover:scale-115
              ${
                activeItem === "help"
                  ? "bg-[#b9fa01] text-black shadow-xs font-semibold"
                  : "text-neutral-500 dark:text-neutral-400 group-hover:text-neutral-900 dark:group-hover:text-white group-hover:bg-neutral-100 dark:group-hover:bg-neutral-900/60"
              }
            `}
          >
            <HelpCircle className="h-3.5 w-3.5 shrink-0" strokeWidth={activeItem === "help" ? 1.75 : 1.5} />
          </div>
        </button>
      ) : (
        <button
          onClick={() => handleItemClick("help", "/help/")}
          className={`
            w-full flex items-center py-1.5 px-3 text-left rounded-full transition-all cursor-pointer
            ${
              activeItem === "help"
                ? "bg-[#b9fa01] text-black font-semibold shadow-xs"
                : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-900/60 font-medium"
            }
          `}
          title="Ayuda"
        >
          <div
            className={`flex items-center justify-center min-w-[18px] mr-2 ${
              activeItem === "help" ? "text-black" : "text-neutral-500 dark:text-neutral-400"
            }`}
          >
            <HelpCircle className="h-3.5 w-3.5 shrink-0" strokeWidth={1.5} />
          </div>
          <span className="text-[12px] tracking-tight">Ayuda</span>
        </button>
      )}
    </div>
  );

  return (
    <>
      {/* 1. MÓVIL: TELÓN DE FONDO (BACKDROP BAJO EL HEADER) */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 top-16 z-30 bg-black/40 backdrop-blur-xs md:hidden"
            onClick={onCloseMobile}
          />
        )}
      </AnimatePresence>

      {/* 2. MÓVIL: CAJÓN DESLIZANTE LATERAL A ANCHO COMPLETO */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.aside
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 280 }}
            className="fixed top-16 bottom-0 inset-x-0 z-30 w-full bg-white dark:bg-[#000000] shadow-2xl flex flex-col font-sans text-neutral-900 dark:text-neutral-100 md:hidden overflow-hidden"
          >
            {/* Navegación móvil con Ajustes y Ayuda fijados al pie */}
            <div className="flex-1 overflow-y-auto px-4 pt-4 pb-2 space-y-1 custom-scrollbar">
              {renderNavItems(true)}
            </div>

            {/* Ajustes y Ayuda al pie en móvil */}
            <div className="mt-auto border-t border-neutral-200 dark:border-[#1a1a1f] pt-2 pb-6 px-4 bg-white dark:bg-[#000000] shrink-0">
              {renderUtilities(true)}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* 3. DESKTOP: SIDEBAR INTEGRADO EN LAYOUT (HIDDEN EN MÓVIL) */}
      <motion.aside
        animate={{ width: isCollapsed ? 72 : sidebarWidth }}
        transition={isDragging ? { duration: 0 } : { type: "spring", damping: 26, stiffness: 220 }}
        className={`
          hidden md:flex relative h-full bg-white dark:bg-[#000000] border-r border-neutral-200 dark:border-[#1a1a1f] z-20 flex-col font-sans text-neutral-900 dark:text-neutral-100 select-none shrink-0
          ${className}
        `}
      >
        {/* NAVEGACIÓN DESKTOP: NAV ARRIBA Y AJUSTES/AYUDA ABAJITO */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <nav className={`flex-1 ${isCollapsed ? "px-1.5 space-y-2.5" : "px-3 space-y-0.5"} pt-3.5 pb-2 overflow-y-auto custom-scrollbar`}>
            {renderNavItems(false)}
          </nav>

          {/* AJUSTES Y AYUDA AL PIE */}
          <div className={`mt-auto border-t border-neutral-200 dark:border-[#1a1a1f] pt-2 pb-3.5 ${isCollapsed ? "px-1.5" : "px-3"} bg-white dark:bg-[#000000] shrink-0`}>
            {renderUtilities(false)}
          </div>
        </div>

        {children}

        {/* MANIPULADOR DE REDIMENSIONAMIENTO (SOLO EN DESKTOP EXPANDIDO) */}
        {!isCollapsed && (
          <div
            onMouseDown={handleMouseDown}
            onDoubleClick={() => setSidebarWidth(250)}
            className="absolute right-0 top-0 w-1 h-full cursor-col-resize z-50 hover:bg-white/20 transition-colors"
          />
        )}
      </motion.aside>
    </>
  );
}
