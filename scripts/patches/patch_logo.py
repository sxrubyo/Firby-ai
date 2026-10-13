import os

with open('/home/ubuntu/firby-landing/index.html', 'r') as f:
    content = f.read()

# Remove the FIRBY text
old_logo_html = """<a href="#" class="logo">
                <img src="/isotype" alt="Firby" class="logo-mark" onerror="this.style.display='none'">
                FIRBY
            </a>"""
new_logo_html = """<a href="#" class="logo">
                <img src="/isotype" alt="Firby" class="logo-mark" onerror="this.style.display='none'">
            </a>"""
content = content.replace(old_logo_html, new_logo_html)

# Increase logo size
content = content.replace("""        .logo-mark {
            height: 32px;""", """        .logo-mark {
            height: 48px;""")

with open('/home/ubuntu/firby-landing/index.html', 'w') as f:
    f.write(content)
