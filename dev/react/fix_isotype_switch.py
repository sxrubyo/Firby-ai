import re
import os

files_to_fix = [
    "src/components/ui/modern-side-bar.tsx",
    "src/components/ui/demo-side-bar.tsx"
]

old_img_regex = r'<img\s+src="/isotype(?:_black)?.png"\s+alt="Firby"\s*(?:onError=\{.*?\})?\s*className="w-full h-full object-contain(?: brightness-0 opacity-80 dark:invert dark:opacity-70)?"\s*/>'

# Need to handle variations in the className, so let's just write a more robust regex or manually replace
# Actually, the string varies a bit. Let's find all img tags with isotype.

for filepath in files_to_fix:
    with open(filepath, "r") as f:
        content = f.read()

    # Find the block where the img is.
    # In demo-side-bar.tsx:
    # <img \n src="/isotype_black.png" \n alt="Firby" \n onError={...} \n className="w-full h-full object-contain brightness-0 opacity-80 dark:invert dark:opacity-70" \n />
    
    # Let's replace the whole <img> tag.
    new_imgs = """<img src="/isotype_black.png" alt="Firby" className="w-full h-full object-contain block dark:hidden" />
              <img src="/isotype_white.png" alt="Firby" className="w-full h-full object-contain hidden dark:block" />"""
              
    content = re.sub(r'<img[^>]+src="/isotype[^>]+>', new_imgs, content)
    
    with open(filepath, "w") as f:
        f.write(content)

