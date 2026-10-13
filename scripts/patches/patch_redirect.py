with open('/home/ubuntu/.firby/repo/src/interfaces/web/static/app.js', 'r') as f:
    js = f.read()

# Replace the login logic
old_logic = """if(data.is_developer) {
                localStorage.setItem('firby_dev_mode', 'true');
                showScreen('dashboard');
            } else {
                localStorage.removeItem('firby_dev_mode');
                showScreen('dashboard');
            }"""

new_logic = """if(data.is_developer) {
                localStorage.setItem('firby_dev_mode', 'true');
                window.location.href = '/dev-portal';
            } else {
                localStorage.removeItem('firby_dev_mode');
                showScreen('dashboard');
            }"""

if old_logic in js:
    js = js.replace(old_logic, new_logic)
else:
    # Let's just find "localStorage.setItem('firby_dev_mode', 'true');"
    import re
    js = re.sub(r"localStorage\.setItem\('firby_dev_mode', 'true'\);\s*showScreen\('dashboard'\);",
                "localStorage.setItem('firby_dev_mode', 'true');\n                window.location.href = '/dev-portal';",
                js)

with open('/home/ubuntu/.firby/repo/src/interfaces/web/static/app.js', 'w') as f:
    f.write(js)
with open('/home/ubuntu/firby/src/interfaces/web/static/app.js', 'w') as f:
    f.write(js)
