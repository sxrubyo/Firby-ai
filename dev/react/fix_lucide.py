with open("/home/ubuntu/firby-dev-react/src/components/ui/animated-ai-chat.tsx", "r") as f:
    text = f.read()

text = text.replace("Figma,", "Layout,")
text = text.replace("<Figma ", "<Layout ")

with open("/home/ubuntu/firby-dev-react/src/components/ui/animated-ai-chat.tsx", "w") as f:
    f.write(text)
