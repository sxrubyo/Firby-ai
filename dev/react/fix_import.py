with open('/home/ubuntu/firby-dev-react/src/components/ui/modern-side-bar.tsx', 'r') as f:
    content = f.read()

if "import {" in content and "Server" not in content:
    content = content.replace("HelpCircle", "HelpCircle,\n  Server")

with open('/home/ubuntu/firby-dev-react/src/components/ui/modern-side-bar.tsx', 'w') as f:
    f.write(content)
