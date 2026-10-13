with open("src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

text = text.replace('<AuthForm\n        onEmailSubmit', '<AuthForm\n        title="Sign in to your workspace"\n        description="Log in to manage your AI agent, review chats, and update your knowledge base."\n        onEmailSubmit')

with open("src/app/sign-in/page.tsx", "w") as f:
    f.write(text)
