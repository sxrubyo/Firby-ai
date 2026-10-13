import re

with open('/etc/caddy/Caddyfile', 'r') as f:
    caddyfile = f.read()

# Replace the firby.duckdns.org block to add the file_server handle
new_block = """# --- DASHBOARD DE FIRBY (NUEVO DOMINIO DIRECTO) ---
firby.duckdns.org {
    # --- SSL/TLS ---
    tls {
        protocols tls1.2 tls1.3
    }
    # --- HEADERS DE SEGURIDAD ---
    header {
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        X-XSS-Protection "1; mode=block"
        Referrer-Policy "strict-origin-when-cross-origin"
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        -Server
        -X-Powered-By
    }
    # --- COMPRESIÓN ---
    encode gzip zstd

    handle /video-bg {
        root * /home/ubuntu/firby/brand-assets
        rewrite * /Backgroundvideo.mp4
        file_server
    }

    handle {
        reverse_proxy 127.0.0.1:8003
    }
}"""

caddyfile = re.sub(r'# --- DASHBOARD DE FIRBY \(NUEVO DOMINIO DIRECTO\) ---[\s\S]+?\}', new_block, caddyfile)

with open('/etc/caddy/Caddyfile', 'w') as f:
    f.write(caddyfile)
