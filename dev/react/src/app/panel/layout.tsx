import { SessionGate } from "@/components/SessionGate";

export default function PanelLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SessionGate
      allowedKeys={["dev_master_key"]}
      redirectTo="/dev-portal/login/"
      loadingLabel="Validando acceso al panel..."
    >
      {children}
    </SessionGate>
  );
}
