import os
import glob

def replace_in_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Chat Template
    content = content.replace('w-10 h-10 mb-2', 'h-8 mb-2')
    content = content.replace('src="/isotype_white.png"', 'src="/firby_logo_12jun.svg"')
    
    # Modern Sidebar
    content = content.replace('w-12 h-12 rounded-lg flex items-center justify-center', 'h-8 rounded-lg flex items-center justify-center')
    content = content.replace('<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />', '')
    content = content.replace('<img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" />', '<img src="/firby_logo_12jun.svg" alt="Firby" className="h-full w-auto object-contain" />')
    
    # Demo Sidebar
    content = content.replace('src="/isotype_black.png"', 'src="/firby_logo_12jun.svg"')
    
    # Fallback to catch any remaining 
    content = content.replace('src="/isotype_white.png"', 'src="/firby_logo_12jun.svg"')
    content = content.replace('className="w-full h-full object-contain"', 'className="h-full w-auto object-contain"')

    # Explicit widths that might squeeze the logo
    content = content.replace('className="w-12 h-12"', 'className="h-10 w-auto"')
    content = content.replace('className="w-8 h-8"', 'className="h-8 w-auto"')

    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            replace_in_file(os.path.join(root, file))

