import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

interface AuthFormProps extends React.HTMLAttributes<HTMLDivElement> {
  logoSrc: string;
  logoAlt?: string;
  title: string;
  description?: string;
  primaryAction: {
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
  };
  secondaryActions?: {
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
  }[];
  skipAction?: {
    label: string;
    onClick: () => void;
  };
  footerContent?: React.ReactNode;
}

const AuthForm = React.forwardRef<HTMLDivElement, AuthFormProps>(
  (
    {
      className,
      logoSrc,
      logoAlt = "Company Logo",
      title,
      description,
      primaryAction,
      secondaryActions,
      skipAction,
      footerContent,
      ...props
    },
    ref
  ) => {
    return (
      <div className={cn("flex flex-col items-center justify-center", className)}>
        <Card
          ref={ref}
          className={cn(
            "w-full max-w-sm",
            "animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-4 duration-500 shadow-xl dark:border-neutral-800 dark:bg-[#111]"
          )}
          {...props}
        >
          <CardHeader className="text-center">
            <div className="mb-4 flex justify-center">
              <img src={logoSrc} alt={logoAlt} className="h-12 w-12 object-contain rounded-[4px] dark:invert" />
            </div>
            <CardTitle className="text-2xl font-semibold tracking-tight text-foreground dark:text-white">{title}</CardTitle>
            {description && <CardDescription className="dark:text-neutral-400">{description}</CardDescription>}
          </CardHeader>
          <CardContent className="grid gap-4">
            <Button onClick={primaryAction.onClick} className="w-full transition-transform hover:scale-[1.03] dark:bg-white dark:text-black">
              {primaryAction.icon}
              {primaryAction.label}
            </Button>

            {secondaryActions && secondaryActions.length > 0 && (
              <div className="relative my-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t dark:border-neutral-800" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background dark:bg-[#111] px-2 text-muted-foreground dark:text-neutral-500">or</span>
                </div>
              </div>
            )}

            <div className="grid gap-2">
              {secondaryActions?.map((action, index) => (
                <Button key={index} variant="secondary" className="w-full transition-transform hover:scale-[1.03] dark:bg-[#222] dark:text-white dark:hover:bg-[#333]" onClick={action.onClick}>
                  {action.icon}
                  {action.label}
                </Button>
              ))}
            </div>
          </CardContent>

          {skipAction && (
            <CardFooter className="flex flex-col">
              <Button variant="outline" className="w-full transition-transform hover:scale-[1.03] dark:border-neutral-800 dark:text-white" onClick={skipAction.onClick}>
                {skipAction.label}
              </Button>
            </CardFooter>
          )}
        </Card>

        {footerContent && (
          <div className="mt-6 w-full max-w-sm px-8 text-center text-sm text-muted-foreground dark:text-neutral-500 animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-4 duration-500 [animation-delay:200ms]">
            {footerContent}
          </div>
        )}
      </div>
    );
  }
);
AuthForm.displayName = "AuthForm";

export { AuthForm };
