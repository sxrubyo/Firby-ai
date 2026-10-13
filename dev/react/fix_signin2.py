with open("src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

text = text.replace('<Image src="/Firby Isotipo + Wordmark.png" alt="Firby Logo" width={200} height={50} className="w-auto h-10 object-contain brightness-0 invert" />', '<img src="/firby_logo_12jun.svg" alt="Firby Logo" className="w-auto h-11 object-contain brightness-0 invert select-none" />')
text = text.replace('import Image from "next/image";\n', '')

with open("src/app/sign-in/page.tsx", "w") as f:
    f.write(text)

