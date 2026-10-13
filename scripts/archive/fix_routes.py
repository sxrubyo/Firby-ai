from pathlib import Path

def fix_file(filepath):
    p = Path(filepath)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    
    # Define clean route block
    old_section_start = '@app.get("/sign-up"'
    old_section_end = 'async def serve_sign_up():'
    
    # Find start and end
    s_idx = text.find(old_section_start)
    if s_idx == -1:
        print(f"Could not find @app.get('/sign-up') in {filepath}")
        return
        
    e_idx = text.find('async def serve_token():', s_idx)
    if e_idx == -1:
        print(f"Could not find async def serve_token in {filepath}")
        return

    clean_routes = '''@app.get("/sign-up", response_class=HTMLResponse, include_in_schema=False)
@app.get("/sign-up/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/register", response_class=HTMLResponse, include_in_schema=False)
@app.get("/register/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/crear-cuenta", response_class=HTMLResponse, include_in_schema=False)
@app.get("/crear-cuenta/", response_class=HTMLResponse, include_in_schema=False)
async def serve_sign_up():
    p = Path("/home/ubuntu/firby/src/interfaces/web/static/sign-up.html")
    if not p.exists():
        p = Path("/home/ubuntu/firby/dev/react/out/sign-up.html")
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return RedirectResponse(url="/sign-in")

@app.get("/onboarding", response_class=HTMLResponse, include_in_schema=False)
@app.get("/onboarding/", response_class=HTMLResponse, include_in_schema=False)
async def serve_onboarding():
    p = Path("/home/ubuntu/firby/src/interfaces/web/static/onboarding.html")
    if p.exists():
        return HTMLResponse(p.read_text(encoding="utf-8"))
    return RedirectResponse(url="/workspace/")

'''
    text = text[:s_idx] + clean_routes + text[e_idx:]
    
    # Also in calendar_oauth_callback: ensure onboarding check is strict:
    # If not completed or clinic unconfigured, ALWAYS redirect to /onboarding
    text = text.replace(
        'is_new_user = True\n        clinic = db.get_clinic()\n        if clinic:\n            clinic_email = (clinic.get("email") or "").strip().lower()\n            setup_done = clinic.get("setup_done", 0)\n            onboarding_done = clinic.get("onboarding_done", 0)\n            if clinic_email and email and clinic_email == email.lower() and (setup_done or onboarding_done):\n                is_new_user = False',
        '''is_new_user = True
        clinic = db.get_clinic()
        if clinic:
            clinic_email = (clinic.get("email") or "").strip().lower()
            setup_done = clinic.get("setup_done", 0)
            onboarding_done = clinic.get("onboarding_done", 0)
            clinic_name = (clinic.get("name") or "").strip()
            # Requiere que el onboarding este marcado como completado Y tenga nombre configurado
            if clinic_email and email and clinic_email == email.lower() and onboarding_done and clinic_name and "Clinica" not in clinic_name and "Clínica" not in clinic_name:
                is_new_user = False'''
    )
    
    p.write_text(text, encoding="utf-8")
    print(f"Successfully fixed routes in {filepath}")

fix_file("/home/ubuntu/firby/src/interfaces/web/app.py")
fix_file("/home/ubuntu/firby/instances/clinica-de-las-americas/src/interfaces/web/app.py")
