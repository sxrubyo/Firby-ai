with open('/home/ubuntu/firby/src/interfaces/web/static/index.html', 'r') as f:
    html = f.read()

# Remove the DEV VIEWS section
import re
html = re.sub(r'<!-- DEV VIEWS -->.*?</section>', '', html, flags=re.DOTALL)

with open('/home/ubuntu/firby/src/interfaces/web/static/index.html', 'w') as f:
    f.write(html)
with open('/home/ubuntu/.firby/repo/src/interfaces/web/static/index.html', 'w') as f:
    f.write(html)
