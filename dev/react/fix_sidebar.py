with open("src/components/ui/modern-side-bar.tsx", "r") as f:
    text = f.read()

text = text.replace('{ id: "dashboard", name: "New Chat", icon: Home, href: "/chats/" },', '{ id: "dashboard", name: "Home", icon: Home, href: "/panel/" },\n  { id: "admin-chat", name: "Admin Chat", icon: MessageSquare, href: "/chats/" },')

with open("src/components/ui/modern-side-bar.tsx", "w") as f:
    f.write(text)
