with open('/etc/caddy/Caddyfile', 'r') as f:
    content = f.read()
content = content.replace("root * /home/ubuntu/firby/brand-assets", "root * /var/www/firby")
with open('/etc/caddy/Caddyfile', 'w') as f:
    f.write(content)
