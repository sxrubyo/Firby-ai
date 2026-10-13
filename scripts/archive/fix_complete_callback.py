from pathlib import Path

def fix(fpath):
    p = Path(fpath)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    
    start_marker = '@app.get("/calendar-callback")'
    end_marker = '@app.get("/agenda/disponibilidad")'
    
    s_idx = text.find(start_marker)
    e_idx = text.find(end_marker)
    
    if s_idx == -1 or e_idx == -1:
        print("Markers not found in", fpath)
        return

    clean_callback = '''@app.get("/calendar-callback")
async def calendar_oauth_callback(code: str = None, error: str = None,
                                  request: Request = None):
    from fastapi.responses import HTMLResponse, RedirectResponse
    import urllib.parse
    import httpx

    if error:
        return RedirectResponse(url="/sign-in?error=google_denied")

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

        # Comprobar si onboarding esta completado
        is_new_user = True
        clinic = db.get_clinic()
        if clinic:
            clinic_email = (clinic.get("email") or "").strip().lower()
            setup_done = clinic.get("setup_done", 0)
            onboarding_done = clinic.get("onboarding_done", 0)
            clinic_name = (clinic.get("name") or "").strip()
            if clinic_email and email and clinic_email == email.lower() and onboarding_done and clinic_name and "Clinica" not in clinic_name and "Clínica" not in clinic_name:
                is_new_user = False

        if is_new_user and email:
            try:
                with db._conn() as c:
                    if picture:
                        try:
                            c.execute("UPDATE clinic SET email=?, avatar=?, updated_at=datetime('now') WHERE id=1", (email, picture))
                        except Exception:
                            c.execute("UPDATE clinic SET email=?, updated_at=datetime('now') WHERE id=1", (email,))
                    else:
                        c.execute("UPDATE clinic SET email=?, updated_at=datetime('now') WHERE id=1", (email,))
            except Exception as e:
                log.warning(f"[calendar] clinic update error: {e}")

        master_key = Config.MASTER_API_KEY
        if is_new_user:
            target_url = f"/onboarding?email={urllib.parse.quote(email)}&name={urllib.parse.quote(name)}&avatar={urllib.parse.quote(picture)}&trial=7d"
        else:
            target_url = "/workspace/"

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Firby</title></head>
<body style="background:#fafafa;margin:0;">
<script>
    try {{
        localStorage.setItem('firby_master_key', '{master_key}');
        localStorage.setItem('firby_user_email', '{email}');
        localStorage.setItem('firby_user_name', '{name}');
        localStorage.setItem('firby_user_avatar', '{picture}');
        localStorage.removeItem('dev_master_key');
        localStorage.removeItem('firby_dev_mode');
    }} catch(e) {{}}
    window.location.replace('{target_url}');
</script>
</body></html>"""
        return HTMLResponse(html)

    except Exception as e:
        log.error(f"[calendar] OAuth callback error: {e}", exc_info=True)
        return RedirectResponse(url="/sign-in?error=oauth_error")


'''
    text = text[:s_idx] + clean_callback + text[e_idx:]
    p.write_text(text, encoding="utf-8")
    print("Fixed:", fpath)

fix("/home/ubuntu/firby/src/interfaces/web/app.py")
fix("/home/ubuntu/firby/instances/clinica-de-las-americas/src/interfaces/web/app.py")
