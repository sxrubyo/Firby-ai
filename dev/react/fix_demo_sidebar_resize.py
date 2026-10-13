import re

with open("src/components/ui/demo-side-bar.tsx", "r") as f:
    content = f.read()

# Add states
states_str = """  const [isCollapsed, setIsCollapsed] = useState(true);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [activeItem, setActiveItem] = useState("chat");
  const [profile, setProfile] = useState<any>({ name: "Santiago", email: "santi21435@gmail.com", avatar: "" });
  const [sidebarWidth, setSidebarWidth] = useState(260);
  const [isDragging, setIsDragging] = useState(false);"""
  
content = re.sub(r'  const \[isCollapsed, setIsCollapsed\] = useState\(true\);.*?const \[profile, setProfile\] = useState<any>\(\{ name: "Santiago", email: "santi21435@gmail\.com", avatar: "" \}\);', states_str, content, flags=re.DOTALL)

# Add handleMouseDown before return
handle_mouse_down = """
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
content = content.replace("const SidebarContent = () => (", handle_mouse_down + "\n  const SidebarContent = () => (")

# Update aside
old_aside = """      <motion.aside
        animate={{ width: isCollapsed ? 70 : 260 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className={`hidden md:flex flex-col bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-30 flex-shrink-0 h-screen overflow-hidden relative`}
      >
        <SidebarContent />
      </motion.aside>"""
      
new_aside = """      <motion.aside
        animate={{ width: isCollapsed ? 70 : sidebarWidth }}
        transition={isDragging ? { duration: 0 } : { type: "spring", damping: 25, stiffness: 200 }}
        className={`hidden md:flex flex-col bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-30 flex-shrink-0 h-screen overflow-hidden relative`}
      >
        <SidebarContent />
        {!isCollapsed && (
            <div
              onMouseDown={handleMouseDown}
              onDoubleClick={() => setSidebarWidth(260)}
              className="absolute right-0 top-0 w-1.5 h-full cursor-col-resize z-50 hover:bg-[#e05a2b]/30 transition-colors"
            />
        )}
      </motion.aside>"""
      
content = content.replace(old_aside, new_aside)

with open("src/components/ui/demo-side-bar.tsx", "w") as f:
    f.write(content)
