"use client";

import { ThemeContext } from "@/components/theme-provider";
import { useContext, useState, useEffect, useRef } from "react";
import { AppShell } from "@/components/app-shell";
import { CheckCircle2, RefreshCw, LogOut, Moon, Sun } from "lucide-react";
import { LiquidToggle } from "@/components/LiquidToggle";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [isClientUser, setIsClientUser] = useState(false);
  const [profile, setProfile] = useState<any>({ name: "", email: "", role: "", avatar: "" });
  const [pendingProfile, setPendingProfile] = useState<any>({ name: "", avatar: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const { isDark, toggleDark } = useContext(ThemeContext);
  const [showAvatars, setShowAvatars] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const presetAvatars = Array.from(
    { length: 30 },
    (_, i) => `/static/avatars/avatar_${String(i + 1).padStart(2, "0")}.svg`
  );

  useEffect(() => {
    setIsClientUser(!!localStorage.getItem("firby_master_key"));
    const params = new URLSearchParams(window.location.search);
    if (params.get("tab")) {
      const tab = params.get("tab") as string;
      if (tab === "profile" || tab === "appearance") {
        setActiveTab(tab);
      }
    }

    const fetchData = async () => {
      try {
        const token =
          localStorage.getItem("firby_master_key") ||
          localStorage.getItem("dev_master_key") ||
          "";
        const resProfile = await fetch("/api/user/profile", {
          headers: { "x-master-key": token },
        });
        if (resProfile.ok) {
          const data = await resProfile.json();
          setProfile(data);
          setPendingProfile({ name: data.name || "", avatar: data.avatar || "" });
        }
      } catch (e) {}
      setLoading(false);
    };
    fetchData();
  }, []);

  const toggleTheme = toggleDark;

  const handleApplyChanges = async () => {
    setSaving(true);
    setSuccessMsg("");
    try {
      const token =
        localStorage.getItem("firby_master_key") ||
        localStorage.getItem("dev_master_key") ||
        localStorage.getItem("conny_master_key") ||
        "ACTV-FIRBY2026-CLIENT-SESSION-TOKEN-KEY";

      let avatarToSave = pendingProfile.avatar;

      if (pendingProfile.avatar.startsWith("data:image")) {
        const resUpload = await fetch("/upload-avatar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: "upload.png",
            content_type: "image/png",
            data: pendingProfile.avatar,
          }),
        });
        if (resUpload.ok) {
          const data = await resUpload.json();
          avatarToSave = data.url;
        }
      }

      const res = await fetch("/api/user/profile", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "x-master-key": token,
        },
        body: JSON.stringify({ name: pendingProfile.name, avatar: avatarToSave }),
      });

      const updatedProfile = { ...profile, name: pendingProfile.name, avatar: avatarToSave };
      setProfile(updatedProfile);
      setPendingProfile({ name: pendingProfile.name, avatar: avatarToSave });

      localStorage.setItem("firby_user_name", pendingProfile.name);
      localStorage.setItem("firby_user_avatar", avatarToSave);

      setSuccessMsg("Cambios guardados correctamente");
      setTimeout(() => setSuccessMsg(""), 3000);

      window.dispatchEvent(new CustomEvent("avatarUpdated", { detail: avatarToSave }));
      window.dispatchEvent(new CustomEvent("profileUpdated", { detail: { name: pendingProfile.name } }));
    } catch (e) {
      console.error(e);
    }
    setSaving(false);
  };

  const handleLogout = () => {
    const isClient = !!localStorage.getItem("firby_master_key");
    localStorage.removeItem("dev_master_key");
    localStorage.removeItem("firby_master_key");
    if (isClient) {
      window.location.href = "/sign-in/";
    } else {
      window.location.href = "/dev-portal/login/";
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64String = reader.result as string;
      setPendingProfile((prev: any) => ({ ...prev, avatar: base64String }));
      setShowAvatars(false);
    };
    reader.readAsDataURL(file);
  };

  const selectPresetAvatar = (url: string) => {
    setPendingProfile((prev: any) => ({ ...prev, avatar: url }));
    setShowAvatars(false);
  };

  const inputStyle =
    "w-full bg-neutral-50 dark:bg-[#121216] border border-neutral-200 dark:border-white/10 rounded-[8px] text-neutral-900 dark:text-white px-[14px] py-[10px] text-[13px] focus:outline-hidden focus:border-[#b9fa01] focus:ring-1 focus:ring-[#b9fa01] transition-colors";
  const labelStyle =
    "block uppercase text-neutral-500 dark:text-white/50 text-[11px] tracking-[0.06em] mb-2 font-medium";

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8 select-none">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight mb-1 text-neutral-900 dark:text-white">
              Configuración de la cuenta
            </h1>
            <p className="text-neutral-500 dark:text-white/50 text-sm">
              Gestiona tu información de perfil y preferencias del sistema.
            </p>
          </div>
          {activeTab === "profile" && (
            <button
              onClick={handleApplyChanges}
              disabled={saving}
              className="px-4 py-2 bg-[#b9fa01] hover:bg-[#a5e000] text-black text-[13px] font-semibold rounded-[6px] transition-colors disabled:opacity-50 whitespace-nowrap shadow-xs cursor-pointer"
            >
              {saving ? "Guardando..." : "Guardar cambios"}
            </button>
          )}
        </div>

        {successMsg && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-sm rounded-md flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> {successMsg}
          </div>
        )}

        <div className="flex flex-col md:flex-row items-start mt-8">
          {/* Menú lateral de pestañas */}
          <div className="w-full md:w-[160px] shrink-0 flex flex-col space-y-1 pr-8 mb-8 md:mb-0">
            {[
              { id: "profile", label: "Perfil" },
              { id: "appearance", label: "Apariencia" },
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`text-left py-2 px-3 text-sm rounded-r-md transition-colors cursor-pointer ${
                    isActive
                      ? "text-neutral-900 dark:text-white border-l-2 border-[#b9fa01] bg-neutral-100 dark:bg-white/[0.05] font-semibold"
                      : "text-neutral-600 dark:text-white/50 border-l-2 border-transparent hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-50 dark:hover:bg-white/[0.02]"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Contenido de la pestaña activa */}
          <div className="flex-1 w-full max-w-2xl">
            {loading ? (
              <div className="p-8 flex justify-center">
                <RefreshCw className="w-5 h-5 animate-spin text-neutral-400 dark:text-white/40" />
              </div>
            ) : (
              <>
                {activeTab === "profile" && (
                  <div className="bg-white dark:bg-[#0c0c10] border border-neutral-200 dark:border-white/[0.08] rounded-[12px] p-6 space-y-8 shadow-xs">
                    {/* Sección 1: Foto de perfil */}
                    <div>
                      <label className={labelStyle}>Foto de perfil</label>
                      <div className="flex flex-col items-start gap-4 mt-2">
                        <div className="flex items-center gap-6">
                          <div className="w-[80px] h-[80px] rounded-full overflow-hidden bg-neutral-100 dark:bg-[#15151a] border border-neutral-200 dark:border-white/10 flex items-center justify-center text-2xl font-semibold text-neutral-900 dark:text-white ring-2 ring-[#b9fa01]/30">
                            {pendingProfile.avatar ? (
                              <img
                                src={pendingProfile.avatar}
                                alt="Avatar"
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              pendingProfile.name?.charAt(0) || "U"
                            )}
                          </div>

                          <div className="flex flex-col gap-2">
                            <button
                              type="button"
                              onClick={() => fileInputRef.current?.click()}
                              className="px-3 py-1.5 border border-neutral-200 dark:border-white/10 rounded-[6px] text-[13px] font-medium hover:bg-neutral-50 dark:hover:bg-white/[0.06] transition-colors cursor-pointer text-neutral-800 dark:text-white"
                            >
                              Subir foto
                            </button>
                            <button
                              type="button"
                              onClick={() => setShowAvatars(!showAvatars)}
                              className="px-3 py-1.5 border border-neutral-200 dark:border-white/10 rounded-[6px] text-[13px] font-medium hover:bg-neutral-50 dark:hover:bg-white/[0.06] transition-colors text-neutral-600 dark:text-white/70 cursor-pointer"
                            >
                              Elegir avatar
                            </button>
                          </div>
                        </div>

                        <input
                          type="file"
                          ref={fileInputRef}
                          className="hidden"
                          accept="image/*"
                          onChange={handleFileSelect}
                        />

                        {showAvatars && (
                          <div className="mt-4 p-4 bg-neutral-50 dark:bg-[#121216] border border-neutral-200 dark:border-white/10 rounded-[8px] w-full">
                            <div className="flex justify-between items-center mb-3">
                              <p className="text-[12px] font-medium text-neutral-500 dark:text-white/50">
                                Selecciona un avatar
                              </p>
                              <button
                                type="button"
                                onClick={() => setShowAvatars(false)}
                                className="text-[12px] text-[#b9fa01] hover:underline cursor-pointer"
                              >
                                Cancelar
                              </button>
                            </div>
                            <div className="grid grid-cols-6 gap-3 max-h-48 overflow-y-auto pr-2">
                              {presetAvatars.map((url, i) => (
                                <img
                                  key={i}
                                  src={url}
                                  alt={`Avatar ${i}`}
                                  className="w-12 h-12 rounded-full cursor-pointer hover:ring-2 ring-[#b9fa01] transition-all"
                                  onClick={() => selectPresetAvatar(url)}
                                />
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="h-[0.5px] w-full bg-neutral-200 dark:bg-white/[0.06]" />

                    {/* Sección 2: Nombre para mostrar */}
                    <div>
                      <label className={labelStyle}>Nombre para mostrar</label>
                      <input
                        type="text"
                        value={pendingProfile.name}
                        onChange={(e) =>
                          setPendingProfile({ ...pendingProfile, name: e.target.value })
                        }
                        className={inputStyle}
                      />
                    </div>

                    <div className="h-[0.5px] w-full bg-neutral-200 dark:bg-white/[0.06]" />

                    {/* Sección 3: Correo electrónico */}
                    <div>
                      <label className={labelStyle}>Correo electrónico</label>
                      <input
                        type="email"
                        value={profile.email}
                        disabled
                        className={`${inputStyle} opacity-60 cursor-not-allowed`}
                      />
                      <p className="text-neutral-500 dark:text-white/40 text-[11px] mt-2">
                        Contacta con soporte si necesitas actualizar tu correo electrónico.
                      </p>
                    </div>

                    <div className="h-[0.5px] w-full bg-neutral-200 dark:bg-white/[0.06]" />

                    {/* Sección 4: Zona de riesgo */}
                    <div>
                      <label className="block uppercase text-red-500 dark:text-red-400 text-[11px] tracking-[0.06em] mb-3 font-medium">
                        Zona de riesgo
                      </label>
                      <button
                        type="button"
                        onClick={handleLogout}
                        className="w-full px-4 py-[10px] border border-red-500/30 text-red-600 dark:text-red-400 bg-transparent text-[13px] font-medium rounded-[8px] hover:bg-red-500/10 transition-colors flex items-center justify-center gap-2 cursor-pointer"
                      >
                        <LogOut className="w-4 h-4" /> Cerrar sesión
                      </button>
                    </div>
                  </div>
                )}

                {activeTab === "appearance" && (
                  <div className="bg-white dark:bg-[#0c0c10] border border-neutral-200 dark:border-white/[0.08] rounded-[12px] p-6 shadow-xs">
                    <div className="flex items-center justify-between">
                      <div>
                        <label className={labelStyle} style={{ marginBottom: 0 }}>
                          Tema visual
                        </label>
                        <p className="text-[12px] text-neutral-500 dark:text-white/40 mt-0.5">
                          Alterna entre modo claro y modo oscuro para la interfaz.
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[13px] font-medium text-neutral-700 dark:text-white/80">
                          {isDark ? "Modo oscuro" : "Modo claro"}
                        </span>
                        <LiquidToggle
                          checked={isDark}
                          onChange={(nextDark) => {
                            if (nextDark !== isDark) {
                              toggleTheme();
                            }
                          }}
                        />
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
