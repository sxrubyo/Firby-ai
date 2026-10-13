import re

with open("src/components/ui/modern-side-bar.tsx", "r") as f:
    content = f.read()

# Replace props
content = content.replace("isCollapsed = false, onToggleCollapse", "initialCollapsed = false")
content = content.replace("export function Sidebar({ className = \"\", children, initialCollapsed }: SidebarProps) {", "export function Sidebar({ className = \"\", children, isCollapsed: initialCollapsed = false }: SidebarProps) {")

# Add state
states = """  const [profile, setProfile] = useState<any>({ name: "Santiago", email: "Santi21435@gmail.com", avatar: "" });
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [isDragging, setIsDragging] = useState(false);"""
content = re.sub(r'  const \[profile, setProfile\] = useState<any>\(\{ name: "Santiago", email: "Santi21435@gmail\.com", avatar: "" \}\);', states, content)

mouse_logic = """
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    const startX = e.clientX;
    const startWidth = sidebarWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = startWidth + (moveEvent.clientX - startX);
      setSidebarWidth(Math.min(400, Math.max(160, newWidth)));
    };

    const onMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };
"""
content = content.replace("const handleItemClick = (itemId: string, href: string) => {", mouse_logic + "\n  const handleItemClick = (itemId: string, href: string) => {")

# Update aside style
aside_search = r'<aside\s+className={`\s+bg-neutral-50 dark:bg-\[#111111\] border-r border-neutral-200 dark:border-neutral-800 z-40 flex flex-col\s+\${isOpen \? "fixed inset-y-0 left-0 translate-x-0" : "max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:-translate-x-full"}\s+md:translate-x-0\s+\${className}\s+`}\s+>'
aside_replace = """<aside
        className={`
          bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-40 flex flex-col flex-shrink-0 relative overflow-visible
          ${isOpen ? "fixed inset-y-0 left-0 translate-x-0" : "max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:-translate-x-full"}
          md:translate-x-0
          ${className}
        `}
        style={{ width: isCollapsed ? 52 : sidebarWidth, transition: isDragging ? 'none' : 'width 0.2s ease' }}
      >
        {!isCollapsed && (
            <>
                <div
                onMouseDown={handleMouseDown}
                onDoubleClick={() => setSidebarWidth(260)}
                className="absolute right-0 top-0 w-1.5 h-full cursor-col-resize z-50 hover:bg-[#e05a2b]/30 transition-colors"
                />
            </>
        )}
"""

content = re.sub(aside_search, aside_replace, content, flags=re.DOTALL)

# Let's fix the header toggle
# Right now, the header toggle might call onToggleCollapse.
content = content.replace("onToggleCollapse", "() => setIsCollapsed(!isCollapsed)")

with open("src/components/ui/modern-side-bar.tsx", "w") as f:
    f.write(content)
