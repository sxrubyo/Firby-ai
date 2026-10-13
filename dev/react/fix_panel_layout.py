import re

with open("src/app/panel/page.tsx", "r") as f:
    text = f.read()

# Replace the layout
old_layout = """    <div 
      className="bg-neutral-50 dark:bg-[#1a1a1a] font-sans text-neutral-900 dark:text-[#ffffff] transition-premium duration-300"
      style={{ display: "grid", gridTemplateColumns: `${isCollapsed ? 52 : sidebarWidth}px 1fr`, gridTemplateRows: "1fr", height: "100vh", width: "100%", overflow: "hidden", transition: "grid-template-columns 0.2s ease" }}
    >
            <div style={{ position: "relative", height: "100%" }}>
        <Sidebar isCollapsed={isCollapsed} onToggleCollapse={() => setSidebarWidth(isCollapsed ? 240 : 52)} />
        {!isCollapsed && (
          <>
            <div
              onMouseDown={handleMouseDown}
              onDoubleClick={() => setSidebarWidth(240)}
              className="hover:bg-[#e05a2b]/30 transition-colors duration-150"
              style={{ position: "absolute", right: 0, top: 0, width: 4, height: "100%", cursor: "col-resize", zIndex: 10, background: "transparent" }}
            />
            <button
              onClick={() => setSidebarWidth(52)}
              className="hidden md:flex absolute -right-3 top-[26px] z-50 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-full p-1 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white shadow-[0_2px_8px_rgba(0,0,0,0.1)] transition-transform hover:scale-110"
            >
              <ChevronLeft className="h-3 w-3" />
            </button>
          </>
        )}
      </div>"""

new_layout = """    <div className="flex h-screen w-full bg-neutral-50 dark:bg-[#1a1a1a] font-sans text-neutral-900 dark:text-[#ffffff] overflow-hidden transition-premium duration-300">
        <Sidebar />"""

text = text.replace(old_layout, new_layout)

# Also remove the handleMouseDown logic and state from panel/page.tsx
text = re.sub(r'  const \[sidebarWidth, setSidebarWidth\] = useState\(240\);', '', text)
text = re.sub(r'  const \[isCollapsed, setIsCollapsed\] = useState\(false\);', '', text)
text = re.sub(r'  const handleMouseDown = \(e: React\.MouseEvent\) => \{.*?\n  \};\n', '', text, flags=re.DOTALL)

with open("src/app/panel/page.tsx", "w") as f:
    f.write(text)
