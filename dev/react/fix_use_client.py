with open("/home/ubuntu/firby-dev-react/src/components/ui/animated-ai-chat.tsx", "r") as f:
    text = f.read()

text = text.replace('import { MessageLoading } from "@/components/ui/message-loading";\nimport { ShiningText } from "@/components/ui/shining-text";\n"use client";', '"use client";\nimport { MessageLoading } from "@/components/ui/message-loading";\nimport { ShiningText } from "@/components/ui/shining-text";')

with open("/home/ubuntu/firby-dev-react/src/components/ui/animated-ai-chat.tsx", "w") as f:
    f.write(text)
