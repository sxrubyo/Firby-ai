"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Signup1 } from "@/components/ui/signup-1";

export default function SignUpPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [step, setStep] = useState<"email" | "password" | "verify">("email");
  const [isGoogleVerified, setIsGoogleVerified] = useState(false);
  const [googleName, setGoogleName] = useState("");
  const [existingAccount, setExistingAccount] = useState<{
    exists: boolean;
    provider: string;
    email: string;
    name?: string;
  } | null>(null);

  useEffect(() => {
    document.documentElement.classList.remove("dark");

    // Check query params for initial email or step
    try {
      const params = new URLSearchParams(window.location.search);
      const qEmail = params.get("email");
      const qStep = params.get("step");
      const qPlan = params.get("plan");

      if (qPlan) localStorage.setItem("firby_selected_plan", qPlan.toLowerCase());
      if (qEmail) {
        const cleanEmail = qEmail.trim().toLowerCase();
        setEmail(cleanEmail);
        // Interceptar si la cuenta ya existe antes de mostrar verify o password
        fetch("/api/auth/check-email", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: cleanEmail }),
        })
          .then((r) => r.json())
          .then((data) => {
            if (data && data.exists) {
              setExistingAccount({
                exists: true,
                provider: data.provider || "google",
                email: cleanEmail,
                name: data.name || "",
              });
            } else {
              if (qStep === "verify") setStep("verify");
              if (qStep === "password") setStep("password");
            }
          })
          .catch(() => {
            if (qStep === "verify") setStep("verify");
            if (qStep === "password") setStep("password");
          });
      }
    } catch (e) {}

    // Check server-signed Google OAuth session
    async function checkOAuthSession() {
      try {
        const res = await fetch("/api/auth/oauth-session", {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          if (data && data.valid && data.email) {
            setEmail(data.email);
            setIsGoogleVerified(true);
            if (data.name) setGoogleName(data.name);
            localStorage.setItem("firby_user_email", data.email);
            localStorage.setItem("firby_auth_provider", "google");
            return;
          }
        }
      } catch (err) {
        console.warn("OAuth session check error:", err);
      }

      // Fallback to localStorage if provider is google
      try {
        const localEmail = localStorage.getItem("firby_user_email");
        const localProvider = localStorage.getItem("firby_auth_provider");
        if (localEmail && localProvider === "google") {
          setEmail(localEmail);
          setIsGoogleVerified(true);
          const localName = localStorage.getItem("firby_user_name");
          if (localName) setGoogleName(localName);
        }
      } catch (e) {}
    }

    checkOAuthSession();
  }, []);

  const getActivePlan = (): string => {
    if (typeof window === "undefined") return "pro";
    try {
      const p = new URLSearchParams(window.location.search).get("plan") || localStorage.getItem("firby_selected_plan") || "pro";
      return p.toLowerCase();
    } catch {
      return "pro";
    }
  };

  const handleStepChange = (nextStep: "email" | "password" | "verify") => {
    setStep(nextStep);
    setError("");
    if (nextStep === "email") {
      setExistingAccount(null);
    }
    try {
      const activePlan = getActivePlan();
      if (nextStep === "email") {
        window.history.pushState(
          {},
          "",
          `/sign-up${activePlan ? `?plan=${encodeURIComponent(activePlan)}` : ""}`
        );
      } else {
        window.history.pushState(
          {},
          "",
          `/sign-up?step=${encodeURIComponent(nextStep)}&email=${encodeURIComponent(email)}${activePlan ? `&plan=${encodeURIComponent(activePlan)}` : ""}`
        );
      }
    } catch (e) {}
  };

  // 1. Paso 1 -> Paso 2 (Crear Contraseña) o Interceptar cuenta existente
  const handleEmailNext = async (targetEmail: string): Promise<boolean> => {
    const cleanEmail = targetEmail.trim().toLowerCase();
    setEmail(cleanEmail);
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/check-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: cleanEmail }),
      });
      const data = await res.json().catch(() => ({}));
      setLoading(false);

      if (data && data.exists) {
        setExistingAccount({
          exists: true,
          provider: data.provider || "google",
          email: cleanEmail,
          name: data.name || "",
        });
        return false;
      }

      setExistingAccount(null);
      handleStepChange("password");
      return true;
    } catch (err: any) {
      setLoading(false);
      handleStepChange("password");
      return true;
    }
  };

  // 2. Paso 2 -> Envía código OTP y pasa a Paso 3 (Revisa tu bandeja de entrada)
  const handlePasswordSubmit = async ({
    email: targetEmail,
    password: pwd,
  }: {
    email: string;
    password: string;
  }): Promise<boolean> => {
    setError("");
    setLoading(true);
    setPassword(pwd);

    try {
      const res = await fetch("/api/auth/send-verification-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: targetEmail,
          purpose: "register",
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (res.status === 409 || data.exists) {
        setExistingAccount({
          exists: true,
          provider: data.provider || "google",
          email: targetEmail,
          name: data.name || "",
        });
        setLoading(false);
        return false;
      }

      if (!res.ok) {
        setError(data.detail || data.error || "No se pudo enviar el código de verificación. Intenta nuevamente.");
        setLoading(false);
        return false;
      }

      setLoading(false);
      handleStepChange("verify");
      return true;
    } catch (err: any) {
      setError("Error de conexión con el servidor. Verifica tu conexión a internet.");
      setLoading(false);
      return false;
    }
  };

  // 3. Envío directo de código para "Regístrate con un código de un solo uso"
  const handleSendCode = async (targetEmail: string): Promise<boolean> => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/send-verification-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: targetEmail,
          purpose: "register",
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (res.status === 409 || data.exists) {
        setExistingAccount({
          exists: true,
          provider: data.provider || "google",
          email: targetEmail,
          name: data.name || "",
        });
        setLoading(false);
        return false;
      }

      if (!res.ok) {
        setError(data.detail || data.error || "No se pudo enviar el código de verificación.");
        setLoading(false);
        return false;
      }

      setLoading(false);
      handleStepChange("verify");
      return true;
    } catch (err: any) {
      setError("Error de conexión con el servidor.");
      setLoading(false);
      return false;
    }
  };

  // 4. Paso 3: Validar código OTP y completar registro
  const handleVerifyCode = async ({
    email: targetEmail,
    code,
    password: overridePassword,
  }: {
    email: string;
    code: string;
    password?: string;
  }) => {
    setError("");
    setLoading(true);
    const activePlan = getActivePlan();
    const effectivePassword = overridePassword || password;

    try {
      const vRes = await fetch("/api/auth/verify-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: targetEmail,
          code,
          purpose: "register",
        }),
      });

      const vData = await vRes.json().catch(() => ({}));
      if (vRes.status === 409 || vData.exists) {
        setExistingAccount({
          exists: true,
          provider: vData.provider || "google",
          email: targetEmail,
          name: vData.name || "",
        });
        setLoading(false);
        return;
      }

      if (!vRes.ok || !vData.ok) {
        setError(vData.detail || vData.error || "Código incorrecto o expirado. Por favor intenta de nuevo.");
        setLoading(false);
        return;
      }

      const verificationToken = vData.verification_token;

      const regRes = await fetch("/api/auth/register-trial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: targetEmail,
          verification_token: verificationToken,
          password: effectivePassword || undefined,
          provider: effectivePassword ? "email_password" : "email_otp",
          plan: activePlan,
        }),
      });

      const regData = await regRes.json().catch(() => ({}));
      if (regRes.status === 409 || regData.exists) {
        setExistingAccount({
          exists: true,
          provider: regData.provider || "google",
          email: targetEmail,
          name: regData.name || "",
        });
        setLoading(false);
        return;
      }

      if (!regRes.ok) {
        setError(regData.detail || regData.message || "Error al completar tu registro. Intenta nuevamente.");
        setLoading(false);
        return;
      }

      if (regData.master_key) {
        localStorage.setItem("firby_master_key", regData.master_key);
        localStorage.setItem("firby_user_email", targetEmail);
        localStorage.setItem("firby_auth_provider", effectivePassword ? "email_password" : "email_otp");
        localStorage.removeItem("dev_master_key");
        localStorage.removeItem("firby_dev_mode");
      }

      window.location.href = `/onboarding?plan=${encodeURIComponent(activePlan)}`;
    } catch (err: any) {
      setError("Error de conexión al procesar la verificación. Verifica tu conexión.");
      setLoading(false);
    }
  };

  // 5. Registro directo con Google
  const handleRegisterGoogle = async () => {
    setError("");
    setLoading(true);
    const activePlan = getActivePlan();

    try {
      const res = await fetch("/api/auth/register-trial", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          name: googleName || "",
          provider: "google",
          plan: activePlan,
        }),
      });

      const data = await res.json().catch(() => ({}));
      if (res.status === 409 || data.exists) {
        setExistingAccount({
          exists: true,
          provider: data.provider || "google",
          email,
          name: googleName || "",
        });
        setLoading(false);
        return;
      }

      if (!res.ok) {
        setError(data.detail || data.message || "Error al crear la cuenta con Google.");
        setLoading(false);
        return;
      }

      if (data.master_key) {
        localStorage.setItem("firby_master_key", data.master_key);
        localStorage.setItem("firby_user_email", email);
        localStorage.setItem("firby_auth_provider", "google");
        localStorage.removeItem("dev_master_key");
        localStorage.removeItem("firby_dev_mode");
      }

      window.location.href = `/onboarding?plan=${encodeURIComponent(activePlan)}`;
    } catch (err: any) {
      setError("Error de conexión con el servidor.");
      setLoading(false);
    }
  };

  // 6. Reenviar código OTP
  const handleResendCode = async (targetEmail: string): Promise<boolean> => {
    setError("");
    try {
      const res = await fetch("/api/auth/resend-code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: targetEmail, purpose: "register" }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(data.detail || data.error || "No se pudo reenviar el código. Espera un momento.");
        return false;
      }
      return true;
    } catch (e) {
      setError("Error de red al solicitar nuevo código.");
      return false;
    }
  };

  const handleGoogleAuth = () => {
    if (existingAccount && existingAccount.provider === "google") {
      window.location.href = "/calendar-auth?from=login";
    } else {
      window.location.href = "/calendar-auth?from=signup";
    }
  };

  const handleClearExistingAccount = () => {
    setExistingAccount(null);
    setEmail("");
    setPassword("");
    handleStepChange("email");
  };

  const handleSwitchAccount = async () => {
    try {
      await fetch("/api/auth/clear-oauth-session", {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {}

    try {
      localStorage.removeItem("firby_user_email");
      localStorage.removeItem("firby_auth_provider");
      localStorage.removeItem("firby_user_name");
      localStorage.removeItem("firby_user_avatar");
    } catch (e) {}

    setEmail("");
    setPassword("");
    setIsGoogleVerified(false);
    setGoogleName("");
    setExistingAccount(null);
    handleStepChange("email");
  };

  const currentPlan = getActivePlan();
  const isEquipos = currentPlan === "equipos" || currentPlan === "scale" || currentPlan === "enterprise";

  return (
    <Signup1
      heading="¡Vamos a Crear Tu Cuenta!"
      subheading={isEquipos ? "Crea tu cuenta de empresa para activar tu infraestructura multi-equipo en minutos." : "Prueba 7 días gratis sin tarjeta. Configura a tu operador en minutos."}
      logo={null}
      signupText={isEquipos ? "Crear Cuenta y Continuar" : "Comenzar Prueba Gratuita"}
      googleText="Registrarse con Google"
      loginText="¿Ya tienes una cuenta?"
      loginUrl="/sign-in"
      step={step}
      onStepChange={handleStepChange}
      onEmailNext={handleEmailNext}
      onPasswordSubmit={handlePasswordSubmit}
      onSendCode={handleSendCode}
      onVerifyCode={handleVerifyCode}
      onRegisterGoogle={handleRegisterGoogle}
      onResendCode={handleResendCode}
      onGoogleClick={handleGoogleAuth}
      onSwitchAccount={handleSwitchAccount}
      existingAccount={existingAccount}
      onClearExistingAccount={handleClearExistingAccount}
      isLoading={loading}
      error={error}
      initialEmail={email}
      isGoogleVerified={isGoogleVerified}
    />
  );
}
