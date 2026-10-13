"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AuthForm } from "@/components/ui/sign-in";

export default function DevLoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  const handleEmailSubmit = async (data: { email: string; password?: string }) => {
    setError("");
    if (!data.password) {
      setError("Please enter a password");
      return;
    }

    try {
      const res = await fetch('/api/auth/dev-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: data.email, password: data.password })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        setError(errData.detail || "Credenciales incorrectas");
        return;
      }

      const resData = await res.json();
      if (resData.master_key) {
        localStorage.setItem('firby_master_key', resData.master_key);
        localStorage.setItem('dev_master_key', resData.master_key);
        localStorage.setItem('firby_dev_mode', 'true');
        router.replace('/panel/');
      }
    } catch (err) {
      setError("Error de red");
    }
  };

  React.useEffect(() => {
    document.documentElement.classList.remove('dark');
  }, []);

  return (
    <div className="w-full min-h-screen flex items-center justify-center bg-[#fafafa] p-4 font-sans text-neutral-900">
      <div className="w-full max-w-md flex flex-col items-center">
        <AuthForm
          title="Developer Login"
          description="Accede a la consola de desarrollador para gestionar instancias y configuraciones."
          emailLabel="Correo Electrónico"
          passwordLabel="Contraseña"
          submitLabel="Iniciar Sesión"
          emailLinkLabel="Volver al inicio de sesión principal"
          onEmailSubmit={handleEmailSubmit}
          onApiToken={() => router.push('/dev-portal/token/')}
          onEmailLink={() => router.push('/sign-in/')}
          errorMsg={error}
        />
      </div>
    </div>
  );
}
