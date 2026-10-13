import re

with open("src/app/layout.tsx", "r") as f:
    text = f.read()

metadata_old = """export const metadata: Metadata = {
  title: "Firby AI",
  description: "Firby AI developer and client consoles",
  icons: {
    icon: '/favicon.png',
    apple: '/favicon.png',
  },
};"""

metadata_new = """export const metadata: Metadata = {
  title: "Firby AI",
  description: "Firby AI developer and client consoles",
};"""

text = text.replace(metadata_old, metadata_new)

with open("src/app/layout.tsx", "w") as f:
    f.write(text)
