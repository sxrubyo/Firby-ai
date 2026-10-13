import re
with open("src/components/ui/modern-side-bar.tsx", "r") as f:
    text = f.read()

text = text.replace('{ id: "dashboard", name: "New Chat", icon: Home, href: "/panel/" },\n  { id: "admin-chat", name: "Admin Chat", icon: MessageSquare, href: "/panel/chats/" },', '{ id: "dashboard", name: "New Chat", icon: Home, href: "/panel/chats/" },')
text = text.replace('{ id: "dashboard", name: "New Chat", icon: Home, href: "/panel/" },', '{ id: "dashboard", name: "New Chat", icon: Home, href: "/panel/chats/" },')

with open("src/components/ui/modern-side-bar.tsx", "w") as f:
    f.write(text)
