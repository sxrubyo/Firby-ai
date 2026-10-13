with open("src/app/layout.tsx", "r") as f:
    text = f.read()

text = text.replace('  description: "Firby AI developer and client consoles",\n}', '  description: "Firby AI developer and client consoles",\n  icons: {\n    icon: "/favicon.png"\n  }\n}')

with open("src/app/layout.tsx", "w") as f:
    f.write(text)
