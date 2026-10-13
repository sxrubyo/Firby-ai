"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff } from "lucide-react";
import React, { useState } from "react";

export function Login03({
  onSubmit,
  errorMsg,
  onOtherWays,
  title = "Welcome Back",
  description = "Enter your credentials to access your account.",
}: { onSubmit: (email: string, pass: string) => void, errorMsg?: string, onOtherWays?: () => void, title?: string, description?: string }) {
  const [showPassword, setShowPassword] = useState(false);
  return (
    <div className="flex flex-1 flex-col justify-center px-4 py-10 lg:px-6 w-full max-w-sm animate-in fade-in-0 slide-in-from-bottom-4 duration-500 bg-background dark:bg-[#111] rounded-xl shadow-xl border dark:border-neutral-800">
      <div className="sm:mx-auto sm:w-full">
        <h3 className="text-center text-lg font-semibold text-foreground dark:text-white">
          {title}
        </h3>
        <p className="text-center text-sm text-muted-foreground dark:text-neutral-400 mt-1">
          {description}
        </p>
        <form onSubmit={(e) => {
            e.preventDefault();
            const fd = new FormData(e.currentTarget);
            onSubmit(fd.get("email") as string, fd.get("password") as string);
        }} className="mt-6 space-y-4">
          {errorMsg && <div className="p-3 bg-red-950/50 border border-red-900 rounded-md text-red-200 text-sm text-center">{errorMsg}</div>}
          <div>
            <Label
              htmlFor="email-login-03"
              className="text-sm font-medium text-foreground dark:text-neutral-200"
            >
              Email
            </Label>
            <Input
              type="email"
              id="email-login-03"
              name="email"
              autoComplete="email"
              placeholder="name@company.com"
              className="mt-2 dark:bg-[#222] dark:border-neutral-800 dark:text-white"
              required
            />
          </div>
          <div>
            <Label
              htmlFor="password-login-03"
              className="text-sm font-medium text-foreground dark:text-neutral-200"
            >
              Password
            </Label>
            
            <div className="relative mt-2">
              <Input
                id="password-login-03"
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="••••••••"
                required
                className="pr-10 dark:bg-[#222] dark:border-neutral-800 dark:text-white"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-200"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>

          </div>
          <Button type="submit" className="mt-4 w-full py-2 font-medium dark:bg-white dark:text-black">
            Sign in
          </Button>
        </form>
        <p className="mt-6 text-sm text-center text-muted-foreground dark:text-neutral-500">
          Forgot your password?{" "}
          <a
            href="#"
            className="font-medium text-primary hover:text-primary/90 dark:text-white dark:hover:text-neutral-300 transition-colors"
          >
            Reset password
          </a>
        </p>
        {onOtherWays && <div className="mt-4 text-center"><Button variant="link" className="text-xs text-neutral-500" onClick={onOtherWays}>O ingresa con Api Token</Button></div>}
      </div>
    </div>
  );
}
