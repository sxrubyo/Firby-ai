import re

def revert(filename):
    with open(filename, "r") as f:
        text = f.read()

    text = text.replace('border-neutral-200 dark:border-neutral-800', 'border-black/10 dark:border-white/10')
    text = text.replace('bg-neutral-200 dark:bg-neutral-800', 'bg-black/10 dark:bg-white/10')

    with open(filename, "w") as f:
        f.write(text)

revert("src/components/blocks/chat-template.tsx")
revert("src/components/blocks/sidebar.tsx")
revert("src/components/ui/resizable.tsx")
