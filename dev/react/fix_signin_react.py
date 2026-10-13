with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

import re

# Update handleEmailSubmit
new_email_submit = """
  const handleEmailSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = new FormData(e.currentTarget).get("email") as string;
    const password = new FormData(e.currentTarget).get("password") as string;
    
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email, password: password })
      });
      
      if (!res.ok) {
        // Fallback robusto: ¿Es el master key directo?
        try {
          const configRes = await fetch('/api/config', { headers: { 'Authorization': `Bearer ${password}` } });
          if (configRes.ok) {
            localStorage.setItem('firby_master_key', password);
            router.push('/panel/');
            return;
          }
        } catch(err) {}
        setError("Credenciales incorrectas");
        return;
      }
      
      const data = await res.json();
      if (data.master_key) {
        localStorage.setItem('firby_master_key', data.master_key);
        router.push('/panel/');
      } else {
        setError("Credenciales incorrectas");
      }
    } catch (err) {
      setError("Error de conexión al servidor");
    }
  };
"""
text = re.sub(r'const handleEmailSubmit = .*?alert\("Customer email login triggered"\);\n  };', new_email_submit, text, flags=re.DOTALL)

# Update handleTokenSubmit
new_token_submit = """
  const handleTokenSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const token = new FormData(e.currentTarget).get("token") as string;
    
    // Explicitly reject Dev API tokens
    if (token && token.startsWith("dev_")) {
      setError("This is a developer token. Please use the Developer Console to sign in.");
      return;
    }
    
    // Validar token intentando acceder a la config
    try {
      const res = await fetch('/api/config', { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) {
        localStorage.setItem('firby_master_key', token);
        router.push('/panel/');
      } else {
        setError("Token inválido");
      }
    } catch(err) {
      setError("Error de red");
    }
  };
"""
text = re.sub(r'const handleTokenSubmit = .*?alert\("Customer API token logic triggered\."\);\n  };', new_token_submit, text, flags=re.DOTALL)

with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "w") as f:
    f.write(text)
