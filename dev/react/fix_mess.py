import re

for filepath in ["src/components/ui/demo-side-bar.tsx", "src/components/ui/modern-side-bar.tsx"]:
    with open(filepath, "r") as f:
        text = f.read()
        
    # Let's fix the broken blocks.
    # It looks like:
    # <img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />
    # <img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" /> { const img = e.currentTarget; ... />
    
    broken_regex = r'<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />\s*<img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" /> \{ const img = e\.currentTarget;[^\}]+\} \}\}\s*className="[^"]+"\s*/>'
    
    fixed = """<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />
              <img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" />"""
              
    text = re.sub(broken_regex, fixed, text, flags=re.DOTALL)
    
    # Also another variant on one line:
    broken_regex2 = r'<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />\s*<img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" /> \{ const img = e\.currentTarget;[^\}]+\} \}\}\s*className="[^"]+"\s*/>'
    
    text = re.sub(broken_regex2, fixed, text, flags=re.DOTALL)
    
    with open(filepath, "w") as f:
        f.write(text)
