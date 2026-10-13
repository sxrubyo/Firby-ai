with open("src/app/layout.tsx", "r") as f:
    text = f.read()

text = text.replace(',\n  icons: {\n    icon: "/favicon.ico"\n  }', '')

with open("src/app/layout.tsx", "w") as f:
    f.write(text)
