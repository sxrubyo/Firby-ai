with open("src/app/dev-portal/login/page.tsx", "r") as f:
    text = f.read()

text = text.replace('          title="Sign in with email"\n', '')
text = text.replace('          description="Make a new doc to bring your words, data, and teams together. For free."\n', '')

with open("src/app/dev-portal/login/page.tsx", "w") as f:
    f.write(text)
