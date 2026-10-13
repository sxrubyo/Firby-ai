import { SessionGate } from "@/components/SessionGate";

export default function DemoLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SessionGate
      allowedKeys={["firby_master_key", "dev_master_key"]}
      redirectTo="/sign-in/"
      loadingLabel="Preparando la consola de Firby..."
    >
      {children}
    </SessionGate>
  );
}
