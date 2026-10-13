import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";

export const metadata: Metadata = {
  metadataBase: new URL("https://firbyai.com"),
  alternates: {
    canonical: "/",
    languages: {
      "es": "https://firbyai.com/",
      "x-default": "https://firbyai.com/"
    }
  },
  title: {
    default: "Firby — Operador Digital Autónomo de Inteligencia Artificial para Sitios Web",
    template: "%s | Firby AI"
  },
  description: "Transforme su sitio web en un canal operativo activo. Firby es el operador digital que atiende visitantes en tiempo real, resuelve consultas complejas y ejecuta acciones clave bajo las reglas comerciales de su empresa. Prueba 7 días gratis.",
  keywords: [
    "Firby",
    "Firby AI",
    "operador digital autónomo",
    "agente de inteligencia artificial",
    "agentes para web",
    "agente IA para sitio web",
    "agentes de inteligencia artificial para sitios web",
    "operador digital web",
    "agente autónomo web",
    "inteligencia artificial para páginas web",
    "automatización web empresarial",
    "asistente virtual para empresas"
  ],
  authors: [{ name: "Santiago Rubio Parra", url: "https://firbyai.com" }],
  creator: "Santiago Rubio Parra",
  publisher: "Firby AI",
  openGraph: {
    title: "Firby — Operador Digital Autónomo de Inteligencia Artificial para Sitios Web",
    description: "Transforme su sitio web en un canal operativo activo. Firby es el operador digital que atiende visitantes en tiempo real, resuelve consultas complejas y ejecuta acciones clave bajo las reglas comerciales de su empresa. Prueba 7 días gratis.",
    url: "https://firbyai.com/",
    siteName: "Firby AI",
    locale: "es_CO",
    type: "website",
    images: [
      {
        url: "https://firbyai.com/assets/figma/firby_brand_logo.png",
        width: 1200,
        height: 630,
        alt: "Firby — Operador Digital Autónomo de Inteligencia Artificial para Sitios Web",
      }
    ]
  },
  twitter: {
    card: "summary_large_image",
    title: "Firby — Operador Digital Autónomo de Inteligencia Artificial para Sitios Web",
    description: "Transforme su sitio web en un canal operativo activo. Firby es el operador digital que atiende visitantes en tiempo real, resuelve consultas complejas y ejecuta acciones clave bajo las reglas comerciales de su empresa. Prueba 7 días gratis.",
    images: ["https://firbyai.com/assets/figma/firby_brand_logo.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: [
      { url: "/assets/branding/Isotipo-pestana.png?v=20261009_isotipo_negro", sizes: "512x512", type: "image/png" },
      { url: "/favicon.svg?v=20261009_isotipo_negro", type: "image/svg+xml" },
      { url: "/favicon-32x32.png?v=20261009_isotipo_negro", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16x16.png?v=20261009_isotipo_negro", sizes: "16x16", type: "image/png" },
      { url: "/favicon.ico?v=20261009_isotipo_negro" }
    ],
    apple: [
      { url: "/apple-icon.png?v=20261009_isotipo_negro", sizes: "180x180", type: "image/png" }
    ]
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        {/* Google Tag Manager */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-BLB26J2X');`,
          }}
        />
        {/* End Google Tag Manager */}
        {/* Microsoft Clarity */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(c,l,a,r,i,t,y){
              c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
              t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
              y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            })(window, document, "clarity", "script", "yk3dt2xwep");`,
          }}
        />
        {/* End Microsoft Clarity */}
        {/* Schema.org / JSON-LD Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@graph": [
                {
                  "@type": "Organization",
                  "@id": "https://firbyai.com/#organization",
                  "name": "Firby",
                  "alternateName": ["Firby AI", "Firby Operador Digital"],
                  "url": "https://firbyai.com",
                  "logo": "https://firbyai.com/assets/branding/Isotipo-pestana.png",
                  "founder": {
                    "@type": "Person",
                    "name": "Santiago Rubio Parra"
                  },
                  "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": "+57-324-369-9856",
                    "contactType": "sales",
                    "availableLanguage": ["es"]
                  },
                  "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Medellín",
                    "addressRegion": "Antioquia",
                    "addressCountry": "CO"
                  }
                },
                {
                  "@type": "WebSite",
                  "@id": "https://firbyai.com/#website",
                  "url": "https://firbyai.com",
                  "name": "Firby AI",
                  "description": "Agentes de inteligencia artificial y operadores digitales para sitios web",
                  "publisher": { "@id": "https://firbyai.com/#organization" }
                },
                {
                  "@type": "SoftwareApplication",
                  "@id": "https://firbyai.com/#software",
                  "name": "Firby",
                  "applicationCategory": "BusinessApplication",
                  "operatingSystem": "All, Web",
                  "description": "Operador digital autónomo y agente de inteligencia artificial para sitios web. Atiende visitantes en tiempo real, resuelve consultas complejas y ejecuta acciones clave bajo las reglas comerciales de su empresa.",
                  "offers": [
                    {
                      "@type": "Offer",
                      "name": "Plan Starter",
                      "price": "290000",
                      "priceCurrency": "COP"
                    },
                    {
                      "@type": "Offer",
                      "name": "Plan Pro",
                      "price": "490000",
                      "priceCurrency": "COP"
                    },
                    {
                      "@type": "Offer",
                      "name": "Plan Equipos",
                      "price": "890000",
                      "priceCurrency": "COP"
                    }
                  ]
                }
              ]
            })
          }}
        />
        <link rel="preload" href="/fonts/NeueMontreal-Regular.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/NeueMontreal-Medium.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/NeueMontreal-Bold.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <script dangerouslySetInnerHTML={{
        __html: `
          try {
            const explicit = localStorage.getItem('firby_theme_v3');
            if (explicit === 'dark') {
              document.documentElement.classList.add('dark');
            } else {
              document.documentElement.classList.remove('dark');
              localStorage.setItem('theme_v2', 'light');
              localStorage.setItem('theme', 'light');
              localStorage.setItem('firby_theme_v3', 'light');
            }
          } catch (_) {
            document.documentElement.classList.remove('dark');
          }
        `,
      }} />
        <script src="/firby-scroll-director.js" defer />
        <script src="/firby-motion-engine.js" defer />
      </head>
      <body className="font-sans bg-[#fafafa] dark:bg-[#0f0f11] text-neutral-900 dark:text-neutral-100 antialiased selection:bg-[#b9fa01] selection:text-black">
        {/* Google Tag Manager (noscript) */}
        <noscript>
          <iframe
            src="https://www.googletagmanager.com/ns.html?id=GTM-BLB26J2X"
            height="0"
            width="0"
            style={{ display: "none", visibility: "hidden" }}
          />
        </noscript>
        {/* End Google Tag Manager (noscript) */}
        <ThemeProvider>
            {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
