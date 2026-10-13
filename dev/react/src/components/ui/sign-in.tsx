"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Apple, AtSign, Eye, EyeOff, LockKeyhole, Loader2 } from "lucide-react";
import { FcGoogle } from "react-icons/fc";

const MicrosoftIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 21 21" width="16" height="16" {...props}>
    <rect x="1" y="1" width="9" height="9" fill="#f25022" />
    <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
    <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
    <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
  </svg>
);

interface AuthFormProps extends React.HTMLAttributes<HTMLDivElement> {
  onEmailSubmit?: (data: { email: string; password?: string }) => void;
  onSocialSignIn?: (provider: 'google' | 'microsoft' | 'apple') => void;
  onApiToken?: () => void;
  onEmailLink?: () => void;
  errorMsg?: string;
  title?: string;
  description?: string;
  emailLabel?: string;
  passwordLabel?: string;
  submitLabel?: string;
  emailLinkLabel?: string;
  initialEmail?: string;
  isLoading?: boolean;
  logo?: {
    url: string;
    src: string;
    alt: string;
    title?: string;
  } | null;
}

const AuthForm = React.forwardRef<HTMLDivElement, AuthFormProps>(
  ({
    className,
    onEmailSubmit,
    onSocialSignIn,
    onApiToken,
    onEmailLink,
    errorMsg,
    title = 'Iniciar Sesión',
    description = 'Ingresa a tu espacio de trabajo para gestionar tu agente de IA y revisar tus conversaciones.',
    emailLabel = 'Correo Electrónico',
    passwordLabel = 'Contraseña',
    submitLabel = 'Iniciar Sesión',
    emailLinkLabel,
    initialEmail = '',
    isLoading = false,
    logo = null,
    ...props
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const [email, setEmail] = React.useState(initialEmail);

    React.useEffect(() => {
      if (initialEmail) setEmail(initialEmail);
    }, [initialEmail]);

    const handleFormSubmit = (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const formEmail = (formData.get('email') as string) || email;
      const password = formData.get('password') as string;
      onEmailSubmit?.({ email: formEmail, password });
    };

    const actionButtonClass =
      'h-11 border-neutral-200 bg-white text-neutral-700 shadow-sm hover:border-neutral-300 hover:bg-neutral-50 hover:text-neutral-900 rounded-xl transition cursor-pointer flex items-center justify-center';

    return (
      <div
        ref={ref}
        className={cn(
          'w-full max-w-sm mx-auto rounded-2xl border border-neutral-200/80 bg-white text-neutral-900 shadow-xl shadow-black/5 p-7 sm:p-8 flex flex-col gap-6',
          className
        )}
        {...props}
      >
        {/* Header con logo horizontal centrado */}
        <div className="flex flex-col items-center gap-y-2.5 text-center">
          {logo && (
            <div className="flex items-center justify-center">
              <a href={logo.url} className="transition-transform hover:scale-[1.02] active:scale-[0.98]">
                <img
                  src={logo.src}
                  alt={logo.alt || 'Firby AI'}
                  title={logo.title || 'Firby AI'}
                  className="h-9 sm:h-10 w-auto object-contain select-none"
                />
              </a>
            </div>
          )}
          {title && (
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-neutral-900 leading-tight">
              {title}
            </h1>
          )}
          {description && (
            <p className="text-xs text-neutral-500 max-w-xs leading-relaxed">
              {description}
            </p>
          )}
        </div>

        <div className="flex w-full flex-col gap-5">
          {errorMsg && (
            <div className="w-full rounded-xl bg-red-50 border border-red-200/80 p-3 text-xs text-red-600 font-medium text-center animate-in fade-in duration-200">
              {errorMsg}
            </div>
          )}

          {/* Social Sign In: 3 columnas (Google, Microsoft, Apple) - API eliminada */}
          <div className="flex flex-col gap-2">
            <span className="text-[11px] font-medium text-neutral-400 text-center uppercase tracking-wider">
              Acceder con
            </span>
            <div className="grid grid-cols-3 gap-2.5">
              <Button
                type="button"
                variant="outline"
                className={cn(actionButtonClass, 'p-0')}
                onClick={() => onSocialSignIn ? onSocialSignIn('google') : (window.location.href = '/calendar-auth?from=login')}
                aria-label="Sign in with Google"
              >
                <FcGoogle className="size-5" />
              </Button>
              <Button
                type="button"
                variant="outline"
                className={cn(actionButtonClass, 'p-0')}
                onClick={() => onSocialSignIn?.('microsoft')}
                aria-label="Sign in with Microsoft"
              >
                <MicrosoftIcon className="size-4 object-contain" />
              </Button>
              <Button
                type="button"
                variant="outline"
                className={cn(actionButtonClass, 'p-0')}
                onClick={() => onSocialSignIn?.('apple')}
                aria-label="Sign in with Apple"
              >
                <Apple className="size-4" />
              </Button>
            </div>
          </div>

          {/* Separador */}
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

          {/* Formulario */}
          <form onSubmit={handleFormSubmit} className="flex flex-col gap-3.5">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email" className="text-neutral-700 text-xs font-semibold">
                {emailLabel}
              </Label>
              <div className="relative">
                <AtSign className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" strokeWidth={1.75} />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="nombre@empresa.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  className="h-11 rounded-xl border-neutral-200 bg-white pl-10 text-neutral-900 placeholder:text-neutral-400 focus-visible:border-neutral-400 focus-visible:ring-neutral-400/20 text-sm shadow-none"
                  required
                />
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between gap-3">
                <Label htmlFor="password" className="text-neutral-700 text-xs font-semibold">
                  {passwordLabel}
                </Label>
                <a
                  href="/forgot-password"
                  className="text-xs font-medium text-neutral-500 hover:text-neutral-900 hover:underline transition"
                >
                  ¿Olvidaste tu contraseña?
                </a>
              </div>
              <div className="relative">
                <LockKeyhole className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" strokeWidth={1.75} />
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Tu contraseña"
                  disabled={isLoading}
                  className="h-11 rounded-xl border-neutral-200 bg-white pl-10 pr-10 text-neutral-900 placeholder:text-neutral-400 focus-visible:border-neutral-400 focus-visible:ring-neutral-400/20 text-sm shadow-none"
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-neutral-400 hover:bg-transparent hover:text-neutral-700 cursor-pointer"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" strokeWidth={1.75} /> : <Eye className="h-4 w-4" strokeWidth={1.75} />}
                </Button>
              </div>
            </div>

            <div className="pt-1 flex flex-col gap-2.5">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-11 bg-[#b8f901] border border-[#b8f901] text-[#09090b] hover:bg-[#a6e000] hover:border-[#a6e000] font-bold text-sm rounded-xl shadow-sm transition active:scale-[0.99] cursor-pointer disabled:opacity-50"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2 justify-center">
                    <Loader2 className="h-4 w-4 animate-spin text-black" />
                    <span>Iniciando sesión...</span>
                  </span>
                ) : (
                  submitLabel
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                disabled={isLoading}
                className="w-full h-11 justify-center border-neutral-200 bg-neutral-50 hover:bg-neutral-100 text-neutral-800 hover:border-neutral-300 hover:text-neutral-900 font-semibold text-sm rounded-xl shadow-sm transition cursor-pointer"
                onClick={() => window.location.href = '/sign-up'}
              >
                Crear Cuenta
              </Button>
            </div>
          </form>

          {/* Enlace secundario opcional solo para desarrolladores */}
          {emailLinkLabel && onEmailLink && (
            <div className="flex justify-center pt-0.5">
              <button
                type="button"
                onClick={onEmailLink}
                className="text-xs text-neutral-500 hover:text-neutral-900 hover:underline transition cursor-pointer"
              >
                {emailLinkLabel}
              </button>
            </div>
          )}

          <p className="w-full text-center text-[11px] text-neutral-400 leading-relaxed pt-1">
            Al iniciar sesión, aceptas nuestros{' '}
            <a href="/terms" target="_blank" rel="noopener noreferrer" className="underline hover:text-neutral-700">Términos de Servicio</a>{' '}
            y{' '}
            <a href="/privacy" target="_blank" rel="noopener noreferrer" className="underline hover:text-neutral-700">Política de Privacidad</a>.
          </p>
        </div>
      </div>
    );
  }
);

AuthForm.displayName = 'AuthForm';

export { AuthForm };
