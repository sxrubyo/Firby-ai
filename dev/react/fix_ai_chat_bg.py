with open("src/components/ui/animated-ai-chat.tsx", "r") as f:
    text = f.read()

text = text.replace('bg-neutral-100/50 dark:bg-white/[0.02]', 'bg-white dark:bg-white/[0.02]')
text = text.replace('shadow-2xl"', 'shadow-[0_8px_30px_rgb(0,0,0,0.06)] dark:shadow-2xl"')
text = text.replace('backdrop-blur-2xl bg-white', 'backdrop-blur-2xl bg-white')

with open("src/components/ui/animated-ai-chat.tsx", "w") as f:
    f.write(text)
