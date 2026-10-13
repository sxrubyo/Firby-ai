import re
from pathlib import Path

app_path = Path("/home/ubuntu/firby/src/interfaces/web/app.py")
content = app_path.read_text(encoding="utf-8")

# 1. Add /onboarding route if not present
if "@app.get(\"/onboarding\"" not in content:
    route_addition = '''
@app.get("/onboarding", response_class=HTMLResponse, include_in_schema=False)
@app.get("/onboarding/", response_class=HTMLResponse, include_in_schema=False)
async def serve_onboarding():
    p = Path("/home/ubuntu/firby/src/interfaces/web/static/onboarding.html")
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return RedirectResponse(url="/workspace/")
'''
    # Insert right after serve_sign_up
    content = content.replace('async def serve_sign_up():', route_addition + '\nasync def serve_sign_up():', 1)

# 2. Replace calendar_link_start and calendar_oauth_callback
old_start_marker = '# ─── Calendario — OAuth y disponibilidad ────────────────────────────────────────'
old_end_marker = '@app.get("/agenda/disponibilidad")'

new_oauth_code = '''# ─── Calendario — OAuth y disponibilidad ────────────────────────────────────────

@app.get("/vincular-agenda")
@app.get("/calendar-auth")
@app.get("/auth/google")
async def calendar_link_start(request: Request, scope_type: str = "login"):
    client_id = os.getenv("GCAL_CLIENT_ID", "")
    if not client_id:
        return {
            "error": "Google OAuth no configurado",
            "solucion": "Verifica GCAL_CLIENT_ID en tu archivo .env"
        }

    redirect_uri = "https://firbyai.lat/calendar-callback"
    import urllib.parse
    
    if scope_type == "calendar":
        scopes = [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ]
    else:
        # Scopes 100% no sensibles: Cero advertencias, cero video, aprobacion instantanea
        scopes = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]

    params = {
        "client_id":     client_id,
        "redirect_uri":  redirect_uri,
        "response_type": "code",
        "scope":         " ".join(scopes),
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url)


@app.get("/calendar-callback")
async def calendar_oauth_callback(code: str = None, error: str = None,
                                  request: Request = None):
    from fastapi.responses import HTMLResponse, RedirectResponse
    import urllib.parse
    import httpx

    if error:
        html = f"""<!DOCTYPE html>
        <html><body style="font-family:Arial,sans-serif;padding:40px;text-align:center;background:#0a0a0c;color:#fff;">
        <h2 style="color:#ef4444">Error de autenticacion con Google</h2>
        <p style="color:#a1a1aa;">{error}</p>
        <a href="/sign-in" style="color:#b8f901;text-decoration:none;font-weight:bold;">Volver a Iniciar Sesion</a>
        </body></html>"""
        return HTMLResponse(html, status_code=400)

    if not code:
        return RedirectResponse(url="/sign-in")

    try:
        redirect_uri = "https://firbyai.lat/calendar-callback"
        client_id = os.getenv("GCAL_CLIENT_ID", "")
        client_secret = os.getenv("GCAL_CLIENT_SECRET", "")

        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post("https://oauth2.googleapis.com/token", data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            })
            tokens = token_resp.json() if token_resp.status_code == 200 else {}

        access_token = tokens.get("access_token", "")
        refresh_token = tokens.get("refresh_token", "")

        email = ""
        name = ""
        picture = ""
        if access_token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    ui_resp = await client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if ui_resp.status_code == 200:
                        ud = ui_resp.json()
                        email = ud.get("email", "")
                        name = ud.get("name", "")
                        picture = ud.get("picture", "")
            except Exception as e:
                log.warning(f"[calendar] userinfo fetch error: {e}")

        # Guardar refresh token si vino
        if refresh_token:
            try:
                from src.core.globals import calendar_bridge
                if calendar_bridge:
                    calendar_bridge.update_tokens(access_token, refresh_token)
                with db._conn() as c:
                    try:
                        c.execute("ALTER TABLE clinic ADD COLUMN gcal_refresh_token TEXT DEFAULT ''")
                    except Exception:
                        pass
                    c.execute("UPDATE clinic SET gcal_refresh_token=? WHERE id=1", (refresh_token,))
            except Exception as e:
                log.warning(f"[calendar] no se pudo guardar refresh_token: {e}")

        # Detectar usuario nuevo vs existente
        is_new_user = True
        clinic = db.get_clinic()
        if clinic:
            clinic_email = (clinic.get("email") or "").strip().lower()
            setup_done = clinic.get("setup_done", 0)
            onboarding_done = clinic.get("onboarding_done", 0)
            if clinic_email and email and clinic_email == email.lower() and (setup_done or onboarding_done):
                is_new_user = False

        if is_new_user and email:
            try:
                with db._conn() as c:
                    if picture:
                        c.execute("UPDATE clinic SET email=?, avatar=?, updated_at=datetime('now') WHERE id=1", (email, picture))
                    else:
                        c.execute("UPDATE clinic SET email=?, updated_at=datetime('now') WHERE id=1", (email,))
            except Exception as e:
                log.warning(f"[calendar] clinic update error: {e}")

        # Configurar URLs
        master_key = Config.MASTER_API_KEY
        if is_new_user:
            target_url = f"/onboarding?email={urllib.parse.quote(email)}&name={urllib.parse.quote(name)}&avatar={urllib.parse.quote(picture)}&trial=7d"
            status_text = "¡Cuenta verificada! Preparando tus 7 dias de prueba gratis..."
        else:
            target_url = "/workspace/"
            status_text = "Iniciando sesion en tu espacio de trabajo..."

        html = f"""<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <title>Autenticacion Exitosa — Firby AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #0a0a0c;
                    color: #f4f4f5;
                    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                }}
                .card {{
                    background: #121215;
                    border: 1px solid #27272a;
                    border-radius: 20px;
                    padding: 40px 32px;
                    max-width: 420px;
                    width: 90%;
                    text-align: center;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
                }}
                .badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 12px;
                    border-radius: 9999px;
                    background: rgba(184, 249, 1, 0.1);
                    color: #b8f901;
                    border: 1px solid rgba(184, 249, 1, 0.25);
                    font-size: 12px;
                    font-weight: 600;
                    margin-bottom: 16px;
                }}
                .spinner {{
                    width: 32px;
                    height: 32px;
                    border: 3px solid rgba(184, 249, 1, 0.2);
                    border-top-color: #b8f901;
                    border-radius: 50%;
                    animation: spin 0.7s linear infinite;
                    margin: 24px auto 0;
                }}
                @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">Prueba de 7 Dias Gratis</div>
                <h2 style="font-size: 22px; font-weight: 700; margin: 0 0 10px; color: #ffffff;">Conexion Exitosa</h2>
                <p style="font-size: 14px; color: #a1a1aa; margin: 0; line-height: 1.5;">{status_text}</p>
                <div class="spinner"></div>
            </div>
            <script>
                try {{
                    localStorage.setItem('firby_master_key', '{master_key}');
                    localStorage.setItem('firby_user_email', '{email}');
                    localStorage.setItem('firby_user_name', '{name}');
                    localStorage.setItem('firby_user_avatar', '{picture}');
                    localStorage.removeItem('dev_master_key');
                    localStorage.removeItem('firby_dev_mode');
                }} catch(e) {{}}
                setTimeout(function() {{
                    window.location.replace('{target_url}');
                }}, 500);
            </script>
        </body>
        </html>"""
        return HTMLResponse(html)

    except Exception as e:
        log.error(f"[calendar] OAuth callback error: {e}", exc_info=True)
        return RedirectResponse(url="/sign-in?error=oauth_error")

'''

start_idx = content.find(old_start_marker)
end_idx = content.find(old_end_marker)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_oauth_code + "\n" + content[end_idx:]
    app_path.write_text(content, encoding="utf-8")
    print("SUCCESS: app.py patched successfully!")
else:
    print(f"ERROR: Markers not found (start: {start_idx}, end: {end_idx})")
