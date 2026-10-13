import re

with open("src/components/blocks/chat-template.tsx", "r") as f:
    text = f.read()

# Remove white borders, make them subtle. The user says "Jamas blancos" which usually refers to dark mode borders being too light.
text = text.replace('className="flex flex-col h-screen border ml-1"', 'className="flex flex-col h-screen border-r border-black/5 dark:border-white/5 ml-1"')
text = text.replace('className="h-16 border-b flex items-center px-3"', 'className="h-14 border-b border-black/5 dark:border-white/5 flex items-center px-3"')
text = text.replace('className="flex h-10 pt-2 border-t"', 'className="flex h-14 items-center gap-1 px-2 border-t border-black/5 dark:border-white/5"')

# Add the Firby isotype above "Chats"
header_html = """              <div className="px-3 pt-4 pb-2">
                <div className="w-10 h-10 mb-2">
                  <img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />
                  <img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" />
                </div>
              </div>
              <div className="h-12 px-3 py-2 flex items-center justify-between">
                <p className="font-semibold text-lg">Chats</p>
                <div className="flex justify-end">"""

# Replace the old Chats header
text = re.sub(
    r'<div className="h-10 px-2 py-4 flex items-center">\s*<p className="ml-1">Chats</p>\s*<div className="flex justify-end w-full">',
    header_html,
    text
)

# Make things smaller
text = text.replace('<Avatar className="size-12">', '<Avatar className="size-10">')
text = text.replace('<CardTitle>', '<span className="font-medium text-sm">')
text = text.replace('</CardTitle>', '</span>')
text = text.replace('<CardDescription>', '<span className="text-xs text-muted-foreground truncate max-w-[180px] block">')
text = text.replace('</CardDescription>', '</span>')
text = text.replace('<div className="space-y-2">', '<div className="flex flex-col">')
text = text.replace('<div className="space-y-1 ml-2">', '<div className="flex flex-col ml-3">')

with open("src/components/blocks/chat-template.tsx", "w") as f:
    f.write(text)
