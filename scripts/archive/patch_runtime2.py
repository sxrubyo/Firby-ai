import re

with open("/home/ubuntu/firby/src/core/runtime.py", "r") as f:
    text = f.read()

def replace_method(text, method_name, wrapper_code):
    pattern = r"(    (?:async )?def " + method_name + r"\(self,[\s\S]*?)(?=\n    (?:async )?def |\Z)"
    match = re.search(pattern, text)
    if not match:
        print(f"Could not find method {method_name}")
        return text
    
    # ensure we don't accidentally match another nested def or something, but since we use \n    (?:async )?def we should be good.
    return text[:match.start()] + wrapper_code + text[match.end():]

# Let's restore the backup since I partially replaced some methods
import os
# wait I didn't backup
