with open("src/app/layout.tsx", "r") as f:
    text = f.read()

text = text.replace('  icons: {\n    icon: "/favicon.png"\n  }', '  icons: {\n    icon: "/favicon.ico"\n  }')

with open("src/app/layout.tsx", "w") as f:
    f.write(text)
