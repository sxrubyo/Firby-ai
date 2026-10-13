from pathlib import Path

def patch_file(fpath):
    p = Path(fpath)
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    
    # Replace the HTML block in calendar_oauth_callback with instant silent redirect
    import re
    old_html_regex = r'html = f"""<!DOCTYPE html>.*?return HTMLResponse\(html\)'
    new_html = '''html = f"""<!DOCTYPE html>
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
        return HTMLResponse(html)'''
    
    new_text = re.sub(old_html_regex, new_html, text, flags=re.DOTALL)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        print(f"Patched instant redirect in {fpath}")
    else:
        print(f"Regex did not match in {fpath}")

patch_file("/home/ubuntu/firby/src/interfaces/web/app.py")
patch_file("/home/ubuntu/firby/instances/clinica-de-las-americas/src/interfaces/web/app.py")
