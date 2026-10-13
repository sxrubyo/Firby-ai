import re

def update(filename):
    with open(filename, "r") as f:
        text = f.read()

    text = text.replace('border-black/10 dark:border-white/10', 'border-black/15 dark:border-white/15')
    text = text.replace('bg-black/10 dark:bg-white/10', 'bg-black/15 dark:bg-white/15')

    with open(filename, "w") as f:
        f.write(text)

update("src/components/blocks/chat-template.tsx")
update("src/components/blocks/sidebar.tsx")
update("src/components/ui/resizable.tsx")
