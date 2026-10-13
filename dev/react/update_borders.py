import re

with open("src/components/blocks/chat-template.tsx", "r") as f:
    text = f.read()

# Update borders to neutral-200 for light mode, neutral-800 for dark mode
text = text.replace('border-black/5 dark:border-white/5', 'border-neutral-200 dark:border-neutral-800')

# Update isotype to be exclusively white
isotype_responsive = """<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />
                  <img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" />"""
isotype_white_only = """<img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain" />"""

text = text.replace(isotype_responsive, isotype_white_only)

with open("src/components/blocks/chat-template.tsx", "w") as f:
    f.write(text)

with open("src/components/blocks/sidebar.tsx", "r") as f:
    sidebar_text = f.read()

sidebar_text = sidebar_text.replace('border-black/5 dark:border-white/5', 'border-neutral-200 dark:border-neutral-800')
sidebar_text = sidebar_text.replace('bg-black/5 dark:bg-white/5', 'bg-neutral-200 dark:bg-neutral-800')

with open("src/components/blocks/sidebar.tsx", "w") as f:
    f.write(sidebar_text)

with open("src/components/ui/resizable.tsx", "r") as f:
    resizable_text = f.read()

resizable_text = resizable_text.replace('bg-black/5 dark:bg-white/5', 'bg-neutral-200 dark:bg-neutral-800')
resizable_text = resizable_text.replace('border-black/5 dark:border-white/5', 'border-neutral-200 dark:border-neutral-800')

with open("src/components/ui/resizable.tsx", "w") as f:
    f.write(resizable_text)
