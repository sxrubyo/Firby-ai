import { SessionGate } from "@/components/SessionGate";

export default function SettingsLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SessionGate
      allowedKeys={["firby_master_key", "dev_master_key"]}
      redirectTo="/sign-in/"
      loadingLabel="Validando acceso a configuración..."
    >
      {children}
    </SessionGate>
  );
}
