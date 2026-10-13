import re

with open('/home/ubuntu/firby-landing/index.html', 'r') as f:
    content = f.read()

old_logo = """        <a href="#" class="nav-logo">
            <img src="/isotype" alt="Firby AI" class="logo-mark" onerror="this.style.display='none'">
            Firby AI
        </a>"""

new_logo = """        <a href="#" class="nav-logo">
            <img src="/isotype" alt="Firby" class="logo-mark" onerror="this.style.display='none'">
            Firby
        </a>"""

content = content.replace(old_logo, new_logo)

with open('/home/ubuntu/firby-landing/index.html', 'w') as f:
    f.write(content)
