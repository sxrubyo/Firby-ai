with open("src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

text = text.replace('import { AuthForm } from "@/components/ui/sign-in";', 'import { AuthForm } from "@/components/ui/sign-in";\nimport Image from "next/image";')
text = text.replace('<div className="w-full min-h-screen flex items-center justify-center bg-[#0a0a0c] p-4 font-sans text-neutral-100">\n      <AuthForm', '<div className="w-full min-h-screen flex flex-col items-center justify-center bg-[#0a0a0c] p-4 font-sans text-neutral-100">\n      <div className="w-full max-w-md flex flex-col items-center mb-8">\n        <Image src="/Firby Isotipo + Wordmark.png" alt="Firby Logo" width={200} height={50} className="w-auto h-10 object-contain brightness-0 invert" />\n      </div>\n      <AuthForm')

with open("src/app/sign-in/page.tsx", "w") as f:
    f.write(text)

