import re

with open("src/components/ui/animated-ai-chat.tsx", "r") as f:
    content = f.read()

replacements = {
    'text-white ': 'text-neutral-900 dark:text-white ',
    'text-white"': 'text-neutral-900 dark:text-white"',
    'text-white/90': 'text-neutral-800 dark:text-white/90',
    'text-white/70': 'text-neutral-600 dark:text-white/70',
    'text-white/60': 'text-neutral-500 dark:text-white/60',
    'text-white/40': 'text-neutral-400 dark:text-white/40',
    'text-white/20': 'text-neutral-300 dark:text-white/20',
    
    'bg-white/10': 'bg-neutral-200 dark:bg-white/10',
    'bg-white/5': 'bg-neutral-100 dark:bg-white/5',
    'bg-white/[0.02]': 'bg-neutral-100/50 dark:bg-white/[0.02]',
    'bg-white/[0.03]': 'bg-neutral-200/50 dark:bg-white/[0.03]',
    'bg-white/[0.05]': 'bg-neutral-200 dark:bg-white/[0.05]',
    
    'border-white/10': 'border-neutral-200 dark:border-white/10',
    'border-white/[0.05]': 'border-neutral-200 dark:border-white/[0.05]',
    
    'bg-white text-[#0A0A0B] shadow-lg shadow-white/10': 'bg-neutral-900 text-white dark:bg-white dark:text-[#0A0A0B] shadow-lg shadow-black/10 dark:shadow-white/10',
    
    'from-white/90 to-white/40': 'from-neutral-900 to-neutral-500 dark:from-white/90 dark:to-white/40',
    'via-white/20': 'via-neutral-300 dark:via-white/20',
    
    'bg-black/90': 'bg-white/90 dark:bg-black/90',
    'bg-black/95': 'bg-white/95 dark:bg-black/95',
    
    # Typing Dots
    'bg-white/90 rounded-full': 'bg-neutral-800 dark:bg-white/90 rounded-full',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# specific fix for <Textarea> placeholder color
content = content.replace('placeholder:text-white/20', 'placeholder:text-neutral-400 dark:placeholder:text-white/20')

# box shadow for dots
content = content.replace('boxShadow: "0 0 4px rgba(255, 255, 255, 0.3)"', 'boxShadow: "0 0 4px rgba(0, 0, 0, 0.1)" /* In light mode it might look fine, or we can remove it */')

with open("src/components/ui/animated-ai-chat.tsx", "w") as f:
    f.write(content)

# Also fix the page container background
with open("src/app/demo/page.tsx", "r") as f:
    page_content = f.read()

page_content = page_content.replace('bg-black', 'bg-white dark:bg-black')

with open("src/app/demo/page.tsx", "w") as f:
    f.write(page_content)
