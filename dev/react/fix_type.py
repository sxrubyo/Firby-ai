with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

import re
new_email_submit = """
  const handleEmailSubmit = async (email: string, password: string) => {
    try {
"""
text = re.sub(r'const handleEmailSubmit = async \(e: React\.FormEvent<HTMLFormElement>\) => {\n    e\.preventDefault\(\);\n    const email = new FormData\(e\.currentTarget\)\.get\("email"\) as string;\n    const password = new FormData\(e\.currentTarget\)\.get\("password"\) as string;\n    \n    try {', new_email_submit, text, flags=re.DOTALL)

with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "w") as f:
    f.write(text)
