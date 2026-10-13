with open("src/app/dev-portal/login/page.tsx", "r") as f:
    text = f.read()

text = text.replace('<AuthForm', '<AuthForm\n        title="Developer Login"\n        description="Access the Firby AI console to manage instances, instances, and configurations."')

with open("src/app/dev-portal/login/page.tsx", "w") as f:
    f.write(text)
