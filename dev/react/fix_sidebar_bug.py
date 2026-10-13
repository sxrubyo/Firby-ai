with open("src/components/ui/modern-side-bar.tsx", "r") as f:
    text = f.read()

# Change name to "Chat"
text = text.replace('{ id: "admin-chat", name: "Admin Chat", icon: MessageSquare, href: "/chats/" },', '{ id: "admin-chat", name: "Chat", icon: MessageSquare, href: "/chats/" },')

# Fix active state logic
new_logic = """    if (pathname?.includes("/panel/instances")) {
        setActiveItem("instances");
    } else if (pathname?.includes("/panel/analytics")) {
        setActiveItem("analytics");
    } else if (pathname?.includes("/panel/documents")) {
        setActiveItem("documents");
    } else if (pathname?.includes("/settings")) {
        setActiveItem("settings");
    } else if (pathname?.includes("/help")) {
        setActiveItem("help");
    } else if (pathname?.includes("/chats")) {
        setActiveItem("admin-chat");
    } else {
        setActiveItem("dashboard");
    }"""

old_logic = """    if (pathname?.includes("/panel/instances")) {
        setActiveItem("instances");
    } else if (pathname?.includes("/panel/analytics")) {
        setActiveItem("analytics");
    } else if (pathname?.includes("/panel/documents")) {
        setActiveItem("documents");
    } else if (pathname?.includes("/settings")) {
        setActiveItem("settings");
    } else if (pathname?.includes("/help")) {
        setActiveItem("help");
    } else {
        setActiveItem("dashboard");
    }"""

text = text.replace(old_logic, new_logic)

with open("src/components/ui/modern-side-bar.tsx", "w") as f:
    f.write(text)
