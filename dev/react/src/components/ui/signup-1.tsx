"use client";

import React, { useState, useEffect } from "react";
import { FcGoogle } from "react-icons/fc";
import { Loader2, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { OneTimeCode } from "@/components/OneTimeCode";

export interface Signup1Props {
  heading?: string;
  subheading?: string;
  logo?: {
    url: string;
    src: string;
    alt: string;
    title?: string;
  } | null;
  signupText?: string;
  googleText?: string;
  loginText?: string;
  loginUrl?: string;
  step?: "email" | "password" | "verify";
  onStepChange?: (step: "email" | "password" | "verify") => void;
  onEmailNext?: (email: string) => Promise<boolean | void> | void;
  onPasswordSubmit?: (data: { email: string; password: string }) => Promise<boolean | void>;
  onSendCode?: (email: string) => Promise<boolean | void>;
  onVerifyCode?: (data: { email: string; code: string; password?: string }) => Promise<void>;
  onRegisterGoogle?: () => Promise<void>;
  onResendCode?: (email: string) => Promise<boolean | void>;
  onGoogleClick?: () => void;
  onSwitchAccount?: () => Promise<void> | void;
  existingAccount?: {
    exists: boolean;
    provider: string;
    email: string;
    name?: string;
  } | null;
  onClearExistingAccount?: () => void;
  isLoading?: boolean;
  error?: string;
  initialEmail?: string;
  isGoogleVerified?: boolean;
}

const Signup1 = ({
  heading = "¡Vamos a Crear Tu Cuenta!",
  subheading = "Prueba 7 días gratis sin tarjeta. Configura a tu operador en minutos.",
  logo = null,
  googleText = "Registrarse con Google",
  signupText = "Comenzar Prueba Gratuita",
  loginText = "¿Ya tienes una cuenta?",
  loginUrl = "/sign-in",
  step: externalStep,
  onStepChange,
  onEmailNext,
  onPasswordSubmit,
  onSendCode,
  onVerifyCode,
  onRegisterGoogle,
  onResendCode,
  onGoogleClick,
  onSwitchAccount,
  existingAccount,
  onClearExistingAccount,
  isLoading = false,
  error = "",
  initialEmail = "",
  isGoogleVerified = false,
}: Signup1Props) => {
  const [internalStep, setInternalStep] = useState<"email" | "password" | "verify">("email");
  const currentStep = externalStep || internalStep;

  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [localLoading, setLocalLoading] = useState(false);
  const [localError, setLocalError] = useState("");
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resendSuccess, setResendSuccess] = useState(false);

  useEffect(() => {
    if (initialEmail) {
      setEmail(initialEmail);
    }
  }, [initialEmail]);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const interval = setInterval(() => {
      setResendCooldown((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [resendCooldown]);

  const changeStep = (nextStep: "email" | "password" | "verify") => {
    setInternalStep(nextStep);
    setLocalError("");
    setResendSuccess(false);
    if (onStepChange) onStepChange(nextStep);
  };

  const effectiveLoading = isLoading || localLoading;
  const effectiveError = error || localError;

  // ─── PASO 1: Enviar correo y pasar a Crear Contraseña (o registro Google) ────
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail) {
      setLocalError("Por favor ingresa un correo electrónico.");
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setLocalError("Por favor ingresa una dirección de correo válida.");
      return;
    }

    if (isGoogleVerified) {
      if (onRegisterGoogle) {
        setLocalLoading(true);
        try {
          await onRegisterGoogle();
        } catch (err: any) {
          setLocalError(err?.message || "Error al procesar el registro con Google.");
        } finally {
          setLocalLoading(false);
        }
      }
      return;
    }

    setLocalLoading(true);
    try {
      if (onEmailNext) {
        const ok = await onEmailNext(cleanEmail);
        if (ok !== false) {
          changeStep("password");
        }
      } else {
        changeStep("password");
      }
    } catch (err: any) {
      setLocalError(err?.message || "Error al verificar el correo.");
    } finally {
      setLocalLoading(false);
    }
  };

  // ─── PASO 2: Usuario define contraseña -> despacha OTP -> pasa a Verificación ───
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");

    if (!password || password.length < 6) {
      setLocalError("La contraseña debe tener al menos 6 caracteres.");
      return;
    }

    setLocalLoading(true);
    try {
      if (onPasswordSubmit) {
        const ok = await onPasswordSubmit({
          email: email.trim().toLowerCase(),
          password,
        });
        if (ok !== false) {
          setResendCooldown(60);
          changeStep("verify");
        }
      } else {
        // Enviar código OTP por correo
        const res = await fetch("/api/auth/send-verification-code", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim().toLowerCase(), purpose: "register" }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setLocalError(data.detail || data.error || "No se pudo enviar el código. Intenta de nuevo.");
          return;
        }
        setResendCooldown(60);
        changeStep("verify");
      }
    } catch (err: any) {
      setLocalError(err?.message || "Error de conexión al procesar la contraseña.");
    } finally {
      setLocalLoading(false);
    }
  };

  // ─── Salto directo a código OTP sin contraseña ───
  const handleSkipPasswordToOtp = async () => {
    setLocalError("");
    setLocalLoading(true);
    try {
      if (onSendCode) {
        const res = await onSendCode(email.trim().toLowerCase());
        if (res !== false) {
          setResendCooldown(60);
          changeStep("verify");
        }
      } else {
        const res = await fetch("/api/auth/send-verification-code", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim().toLowerCase(), purpose: "register" }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setLocalError(data.detail || data.error || "No se pudo enviar el código. Intenta de nuevo.");
          return;
        }
        setResendCooldown(60);
        changeStep("verify");
      }
    } catch (err: any) {
      setLocalError("Error de conexión al enviar el código de verificación.");
    } finally {
      setLocalLoading(false);
    }
  };

  // ─── PASO 3: Validar código OTP y completar registro ───
  const processVerification = async (targetCode?: string) => {
    setLocalError("");
    const cleanCode = (targetCode ?? code).trim().replace(/\D/g, "");

    if (cleanCode.length !== 6) {
      setLocalError("Por favor ingresa el código completo de 6 dígitos.");
      return;
    }

    setLocalLoading(true);
    try {
      if (onVerifyCode) {
        await onVerifyCode({
          email: email.trim().toLowerCase(),
          code: cleanCode,
          password: password || undefined,
        });
      } else {
        const vRes = await fetch("/api/auth/verify-code", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email.trim().toLowerCase(),
            code: cleanCode,
            purpose: "register",
          }),
        });
        const vData = await vRes.json().catch(() => ({}));
        if (!vRes.ok || !vData.ok) {
          setLocalError(vData.detail || vData.error || "Código incorrecto o expirado.");
          return;
        }

        const token = vData.verification_token;
        const regRes = await fetch("/api/auth/register-trial", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: email.trim().toLowerCase(),
            verification_token: token,
            provider: password ? "email_password" : "email_otp",
            password: password || undefined,
          }),
        });
        const regData = await regRes.json().catch(() => ({}));
        if (!regRes.ok) {
          setLocalError(regData.detail || regData.message || "Error al completar tu registro.");
          return;
        }

        if (regData.master_key) {
          localStorage.setItem("firby_master_key", regData.master_key);
          localStorage.setItem("firby_user_email", email.trim().toLowerCase());
          localStorage.setItem("firby_auth_provider", password ? "email_password" : "email_otp");
        }
        window.location.href = "/onboarding";
      }
    } catch (err: any) {
      setLocalError(err?.message || "Error de conexión al verificar el código.");
    } finally {
      setLocalLoading(false);
    }
  };

  const handleVerifySubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    await processVerification();
  };

  // Reenviar código OTP
  const handleResend = async () => {
    if (resendCooldown > 0 || effectiveLoading) return;
    setLocalError("");
    setResendSuccess(false);
    setLocalLoading(true);

    try {
      if (onResendCode) {
        await onResendCode(email.trim().toLowerCase());
      } else {
        const res = await fetch("/api/auth/resend-code", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim().toLowerCase(), purpose: "register" }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setLocalError(data.detail || data.error || "No se pudo reenviar el código. Espera un momento.");
          return;
        }
      }
      setResendCooldown(60);
      setResendSuccess(true);
      setTimeout(() => setResendSuccess(false), 4000);
    } catch (err: any) {
      setLocalError("Error de conexión al reenviar el correo.");
    } finally {
      setLocalLoading(false);
    }
  };

  const handleGoogleClick = () => {
    if (onGoogleClick) {
      onGoogleClick();
    } else {
      window.location.href = "/calendar-auth?from=signup";
    }
  };

  const handleDifferentAccountClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    setLocalLoading(true);
    try {
      if (onSwitchAccount) {
        await onSwitchAccount();
      }
    } finally {
      setLocalLoading(false);
    }
  };

  // =========================================================================
  // VISTA: CUENTA YA REGISTRADA (INTERCEPTOR DE SEGURIDAD / SIN DUPLICADOS)
  // =========================================================================
  if (existingAccount && existingAccount.exists) {
    const isGoogle = existingAccount.provider === "google";
    return (
      <section className="min-h-screen bg-[#fafafa] flex items-center justify-center p-4 selection:bg-[#b8f901] selection:text-black">
        <div className="flex h-full w-full items-center justify-center">
          <div className="border border-neutral-200/80 bg-white flex w-full max-w-sm flex-col items-center gap-y-6 rounded-2xl p-7 sm:p-8 shadow-xl shadow-black/5 animate-in fade-in duration-200">
            {/* Logo horizontal centrado */}
            {logo && (
              <div className="flex items-center justify-center">
                <a href={logo.url} className="transition-transform hover:scale-[1.02] active:scale-[0.98]">
                  <img
                    src={logo.src}
                    alt={logo.alt || "Firby AI"}
                    title={logo.title || "Firby AI"}
                    className="h-10 sm:h-11 w-auto object-contain select-none"
                  />
                </a>
              </div>
            )}

            <div className="flex flex-col items-center gap-y-2 text-center">
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-neutral-900 leading-tight">
                {isGoogle ? "Cuenta registrada con Google" : "Esta cuenta ya existe"}
              </h1>
              <p className="text-xs sm:text-sm text-neutral-600 leading-relaxed max-w-xs">
                {isGoogle ? (
                  <>
                    El correo <span className="font-semibold text-neutral-900 break-all">{existingAccount.email}</span> ya está registrado con Google. Inicia sesión directamente para acceder a tu cuenta.
                  </>
                ) : (
                  <>
                    El correo <span className="font-semibold text-neutral-900 break-all">{existingAccount.email}</span> ya está registrado en Firby. Inicia sesión con tu contraseña para continuar.
                  </>
                )}
              </p>
            </div>

            <div className="flex w-full flex-col gap-3">
              {isGoogle ? (
                <Button
                  type="button"
                  onClick={onGoogleClick || (() => { window.location.href = "/calendar-auth?from=login"; })}
                  disabled={effectiveLoading}
                  className="w-full h-11 bg-neutral-900 hover:bg-neutral-800 text-white font-semibold text-sm rounded-xl transition active:scale-[0.99] flex items-center justify-center gap-2.5 cursor-pointer shadow-sm"
                >
                  <FcGoogle className="size-5 shrink-0" />
                  <span>Continuar con Google</span>
                </Button>
              ) : (
                <Button
                  type="button"
                  onClick={() => {
                    window.location.href = `/sign-in?email=${encodeURIComponent(existingAccount.email)}`;
                  }}
                  disabled={effectiveLoading}
                  className="w-full h-11 bg-[#b8f901] hover:bg-[#a6e000] text-[#09090b] font-bold text-sm rounded-xl border border-[#b8f901] hover:border-[#a6e000] shadow-sm transition active:scale-[0.99] cursor-pointer"
                >
                  Iniciar Sesión
                </Button>
              )}

              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  if (onClearExistingAccount) {
                    onClearExistingAccount();
                  } else {
                    setEmail("");
                    changeStep("email");
                  }
                }}
                disabled={effectiveLoading}
                className="w-full h-11 border-neutral-200 hover:bg-neutral-50 hover:border-neutral-300 font-medium text-xs sm:text-sm transition-all rounded-xl text-neutral-700 cursor-pointer"
              >
                Usar otro correo
              </Button>
            </div>

            <div className="text-neutral-500 flex justify-center gap-1.5 text-xs pt-1">
              <p>{loginText}</p>
              <a
                href={loginUrl}
                className="text-neutral-900 font-semibold hover:underline"
              >
                Iniciar Sesión
              </a>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // =========================================================================
  // PASO 1: SIGN UP INICIAL (TARJETA BLANCA ORIGINAL CON LOGO HORIZONTAL)
  // =========================================================================
  if (currentStep === "email") {
    return (
      <section className="min-h-screen bg-[#fafafa] flex items-center justify-center p-4 selection:bg-[#b8f901] selection:text-black">
        <div className="flex h-full w-full items-center justify-center">
          <div className="border border-neutral-200/80 bg-white flex w-full max-w-sm flex-col items-center gap-y-7 rounded-2xl p-7 sm:p-8 shadow-xl shadow-black/5">
            <div className="flex flex-col items-center gap-y-3 text-center">
              {/* Logo horizontal centrado */}
              {logo && (
                <div className="flex items-center justify-center">
                  <a href={logo.url} className="transition-transform hover:scale-[1.02] active:scale-[0.98]">
                    <img
                      src={logo.src}
                      alt={logo.alt || "Firby AI"}
                      title={logo.title || "Firby AI"}
                      className="h-10 sm:h-11 w-auto object-contain select-none"
                    />
                  </a>
                </div>
              )}
              {heading && (
                <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-neutral-900">
                  {heading}
                </h1>
              )}
              {subheading && (
                <p className="text-xs text-neutral-500 max-w-xs leading-relaxed">
                  {subheading}
                </p>
              )}
            </div>

            <div className="flex w-full flex-col gap-5">
              {effectiveError && (
                <div className="w-full rounded-xl bg-red-50 border border-red-200/80 p-3 text-xs text-red-600 font-medium text-center animate-in fade-in duration-200">
                  {effectiveError}
                </div>
              )}

              {isGoogleVerified ? (
                <div className="w-full flex items-center justify-between text-xs py-1 text-neutral-600">
                  <div className="flex items-center gap-2">
                    <FcGoogle className="size-4 shrink-0" />
                    <span className="font-semibold text-neutral-900 truncate max-w-[210px]">{email}</span>
                  </div>
                  <span className="text-[11px] font-medium text-neutral-400">
                    Verificado con Google
                  </span>
                </div>
              ) : (
                <>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleGoogleClick}
                    disabled={effectiveLoading}
                    className="w-full h-11 border-neutral-200 hover:bg-neutral-50 hover:border-neutral-300 font-medium text-xs sm:text-sm transition-all rounded-xl flex items-center justify-center gap-2.5 text-neutral-700 shadow-sm cursor-pointer"
                  >
                    <FcGoogle className="size-5 shrink-0" />
                    <span>{googleText}</span>
                  </Button>

                  <div className="relative my-0">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-neutral-200" />
                    </div>
                    <div className="relative flex justify-center text-[11px] uppercase">
                      <span className="bg-white px-3 text-neutral-400 font-medium tracking-wider">
                        o con correo
                      </span>
                    </div>
                  </div>
                </>
              )}

              <form onSubmit={handleEmailSubmit} className="flex flex-col gap-3.5">
                <div className="flex flex-col gap-1.5">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-semibold text-neutral-700 flex items-center gap-1.5">
                      <span>Correo electrónico</span>
                    </label>
                  </div>

                  <Input
                    type="email"
                    placeholder="contacto@tuempresa.com"
                    required
                    value={email}
                    readOnly={isGoogleVerified}
                    disabled={isGoogleVerified || effectiveLoading}
                    onChange={(e) => setEmail(e.target.value)}
                    className={`h-11 rounded-xl text-sm transition-all ${
                      isGoogleVerified
                        ? "border-neutral-200 bg-neutral-100 text-neutral-600 cursor-not-allowed font-medium shadow-none select-none"
                        : "border-neutral-200 bg-white text-neutral-900 placeholder:text-neutral-400 focus-visible:ring-neutral-400/20"
                    }`}
                  />

                  {isGoogleVerified && (
                    <div className="mt-1 flex items-center justify-between text-[11px] text-neutral-500">
                      <span className="text-neutral-400">Correo verificado por Google</span>
                      <button
                        type="button"
                        onClick={handleDifferentAccountClick}
                        disabled={effectiveLoading}
                        className="text-neutral-900 font-semibold underline hover:text-black transition cursor-pointer"
                      >
                        o usa otra cuenta
                      </button>
                    </div>
                  )}
                </div>

                {/* BOTÓN PRINCIPAL: LLEVA A CREAR CONTRASEÑA */}
                <Button
                  type="submit"
                  disabled={effectiveLoading}
                  className="mt-1 w-full h-11 bg-[#b8f901] hover:bg-[#a6e000] text-[#09090b] font-bold text-sm rounded-xl border border-[#b8f901] hover:border-[#a6e000] shadow-sm transition active:scale-[0.99] cursor-pointer"
                >
                  {effectiveLoading ? (
                    <span className="flex items-center gap-2 justify-center">
                      <Loader2 className="h-4 w-4 animate-spin text-black" />
                      <span>Cargando...</span>
                    </span>
                  ) : isGoogleVerified ? (
                    "Completar Registro con Google"
                  ) : (
                    signupText
                  )}
                </Button>
              </form>
            </div>

            <div className="text-neutral-500 flex justify-center gap-1.5 text-xs">
              <p>{loginText}</p>
              <a
                href={loginUrl}
                className="text-neutral-900 font-semibold hover:underline"
              >
                Iniciar Sesión
              </a>
            </div>
          </div>
        </div>
      </section>
    );
  }

  // =========================================================================
  // PASO 2: CREAR UNA CONTRASEÑA (FLOTANDO, ISOTIPO ARRIBA A LA IZQUIERDA)
  // =========================================================================
  if (currentStep === "password") {
    return (
      <div className="min-h-screen w-full bg-white relative flex flex-col justify-between selection:bg-[#b8f901] selection:text-black">
        
        {/* Logo de Firby arriba en la esquina izquierda (mismo del banner de la landing) */}
        <header className="absolute top-0 left-0 w-full p-6 sm:p-8 flex items-center justify-between z-10">
          <a
            href="/"
            title="Firby"
            className="transition-transform hover:scale-105 active:scale-95 inline-block"
          >
            <img
              src="/assets/figma/firby_brand_logo.png"
              alt="Firby"
              className="h-8 sm:h-9 w-auto object-contain select-none"
            />
          </a>
        </header>

        {/* Contenido en texto flotando estilo OpenAI */}
        <main className="flex-1 w-full flex items-center justify-center px-6 py-20">
          <div className="w-full max-w-[360px] sm:max-w-[380px] flex flex-col gap-6">
            <div className="flex flex-col gap-2">
              <h1 className="text-2xl sm:text-[28px] font-bold tracking-tight text-neutral-900 leading-tight">
                Crear una contraseña
              </h1>
              <p className="text-sm text-neutral-600 leading-relaxed">
                Utilizarás esta contraseña para iniciar sesión en Firby y acceder a tu espacio de trabajo.
              </p>
            </div>

            {effectiveError && (
              <div className="w-full rounded-xl bg-red-50 border border-red-200/80 p-3 text-xs text-red-600 font-medium animate-in fade-in duration-200">
                {effectiveError}
              </div>
            )}

            <form onSubmit={handlePasswordSubmit} className="flex flex-col gap-4">
              {/* Campo de correo en solo lectura con enlace a Editar */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-neutral-700">
                    Dirección de correo electrónico
                  </label>
                  <button
                    type="button"
                    onClick={() => changeStep("email")}
                    className="text-xs text-neutral-500 hover:text-neutral-900 underline transition cursor-pointer"
                  >
                    Editar
                  </button>
                </div>
                <Input
                  type="email"
                  value={email}
                  readOnly
                  disabled
                  className="h-11 rounded-xl text-sm border-neutral-200 bg-neutral-100 text-neutral-600 font-medium shadow-none cursor-not-allowed select-none"
                />
              </div>

              {/* Campo Contraseña */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-neutral-700">
                  Contraseña
                </label>
                <Input
                  type="password"
                  placeholder="Contraseña"
                  required
                  autoFocus
                  value={password}
                  disabled={effectiveLoading}
                  onChange={(e) => setPassword(e.target.value)}
                  className="h-11 rounded-xl border-neutral-300 bg-white text-neutral-900 placeholder:text-neutral-400 focus-visible:ring-neutral-400/20 text-sm shadow-sm"
                />
              </div>

              <Button
                type="submit"
                disabled={effectiveLoading || password.length < 6}
                className="w-full h-11 bg-[#b8f901] hover:bg-[#a6e000] text-[#09090b] font-bold text-sm rounded-xl border border-[#b8f901] hover:border-[#a6e000] shadow-sm transition active:scale-[0.99] cursor-pointer disabled:opacity-50"
              >
                {effectiveLoading ? (
                  <span className="flex items-center gap-2 justify-center">
                    <Loader2 className="h-4 w-4 animate-spin text-black" />
                    <span>Enviando código...</span>
                  </span>
                ) : (
                  "Continuar"
                )}
              </Button>
            </form>

            {/* Acciones secundarias */}
            <div className="flex flex-col items-center gap-3 pt-1 text-center w-full">
              <div className="relative w-full my-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-neutral-200" />
                </div>
                <div className="relative flex justify-center text-[11px] uppercase">
                  <span className="bg-white px-3 text-neutral-400 font-medium tracking-wider">
                    o
                  </span>
                </div>
              </div>

              <button
                type="button"
                onClick={handleSkipPasswordToOtp}
                disabled={effectiveLoading}
                className="text-xs font-medium text-neutral-700 hover:text-black transition cursor-pointer"
              >
                Regístrate con un código de un solo uso.
              </button>

              <div className="text-neutral-500 flex justify-center gap-1.5 text-xs pt-1">
                <p>{loginText}</p>
                <a
                  href={loginUrl}
                  className="text-neutral-900 font-semibold hover:underline"
                >
                  Inicia sesión
                </a>
              </div>
            </div>
          </div>
        </main>

        {/* Footer legal */}
        <footer className="w-full py-6 text-center text-xs text-neutral-400 flex items-center justify-center gap-2">
          <a href="/terms" target="_blank" className="hover:text-neutral-700 underline transition">
            Condiciones de uso
          </a>
          <span className="text-neutral-300">·</span>
          <a href="/privacy" target="_blank" className="hover:text-neutral-700 underline transition">
            Política de privacidad
          </a>
        </footer>

      </div>
    );
  }

  // =========================================================================
  // PASO 3: REVISA TU BANDEJA DE ENTRADA (CÓDIGO OTP + CONTINUAR CON GOOGLE)
  // =========================================================================
  return (
    <div className="min-h-screen w-full bg-white relative flex flex-col justify-between selection:bg-[#b8f901] selection:text-black">
      
      {/* Logo de Firby arriba en la esquina izquierda (mismo del banner de la landing) */}
      <header className="absolute top-0 left-0 w-full p-6 sm:p-8 flex items-center justify-between z-10">
        <a
          href="/"
          title="Firby"
          className="transition-transform hover:scale-105 active:scale-95 inline-block"
        >
          <img
            src="/assets/figma/firby_brand_logo.png"
            alt="Firby"
            className="h-8 sm:h-9 w-auto object-contain select-none"
          />
        </a>
      </header>

      {/* Contenido en texto flotando (estilo exacto auth.openai.com/email-verification) */}
      <main className="flex-1 w-full flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-[320px] sm:max-w-[340px] flex flex-col gap-6">
          <div className="flex flex-col gap-2.5 text-center">
            <h1 className="text-2xl sm:text-[28px] font-bold tracking-tight text-neutral-900 leading-tight text-center">
              Revisa tu bandeja
              <span className="block mt-1">de entrada</span>
            </h1>
            <p className="text-xs sm:text-sm text-neutral-600 leading-relaxed text-center max-w-[280px] mx-auto">
              Introduce el código de verificación que te acabamos de enviar a{" "}
              <span className="font-semibold text-neutral-900 break-all">{email}</span> para crear tu cuenta.
            </p>
          </div>

          {effectiveError && (
            <div className="w-full rounded-xl bg-red-50 border border-red-200/80 p-3 text-xs text-red-600 font-medium text-center animate-in fade-in duration-200">
              {effectiveError}
            </div>
          )}

          {resendSuccess && (
            <div className="w-full rounded-xl bg-neutral-100 border border-neutral-200 p-2.5 text-xs text-neutral-700 font-medium text-center flex items-center justify-center gap-1.5 animate-in fade-in duration-200">
              <Check className="size-3.5 text-neutral-700" />
              <span>Nuevo código de verificación enviado</span>
            </div>
          )}

          <div className="flex flex-col items-center justify-center py-2 w-full">
            <OneTimeCode
              length={6}
              value={code}
              onChange={(val) => {
                setCode(val);
                if (val.length === 6 && !effectiveLoading) {
                  processVerification(val);
                }
              }}
              onComplete={(val) => {
                if (!effectiveLoading) {
                  processVerification(val);
                }
              }}
              disabled={effectiveLoading}
              hasError={Boolean(effectiveError)}
              autoFocus={true}
            />

            {effectiveLoading && (
              <div className="flex items-center gap-2 mt-4 text-xs font-medium text-neutral-600 animate-in fade-in duration-200">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-neutral-800" />
                <span>Verificando código...</span>
              </div>
            )}
          </div>

          {/* Acciones secundarias */}
          <div className="flex flex-col items-center gap-3 pt-1 text-center w-full">
            {resendCooldown > 0 ? (
              <span className="text-xs text-neutral-400 select-none">
                Reenviar correo electrónico en {resendCooldown}s
              </span>
            ) : (
              <button
                type="button"
                onClick={handleResend}
                disabled={effectiveLoading}
                className="text-xs font-medium text-neutral-700 hover:text-black underline transition cursor-pointer"
              >
                Reenviar correo electrónico
              </button>
            )}

            <div className="relative w-full my-1">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-neutral-200" />
              </div>
              <div className="relative flex justify-center text-[11px] uppercase">
                <span className="bg-white px-3 text-neutral-400 font-medium tracking-wider">
                  o
                </span>
              </div>
            </div>

            {/* Continuar con Google */}
            <Button
              type="button"
              variant="outline"
              onClick={handleGoogleClick}
              disabled={effectiveLoading}
              className="w-full h-11 border-neutral-200 hover:bg-neutral-50 hover:border-neutral-300 font-medium text-xs sm:text-sm transition-all rounded-xl flex items-center justify-center gap-2.5 text-neutral-700 shadow-sm cursor-pointer"
            >
              <FcGoogle className="size-5 shrink-0" />
              <span>Continuar con Google</span>
            </Button>
          </div>
        </div>
      </main>

      {/* Footer legal */}
      <footer className="w-full py-6 text-center text-xs text-neutral-400 flex items-center justify-center gap-2">
        <a href="/terms" target="_blank" className="hover:text-neutral-700 underline transition">
          Condiciones de uso
        </a>
        <span className="text-neutral-300">·</span>
        <a href="/privacy" target="_blank" className="hover:text-neutral-700 underline transition">
          Política de privacidad
        </a>
      </footer>

    </div>
  );
};

export { Signup1 };
