import re

with open("src/components/ui/modern-side-bar.tsx", "r") as f:
    text = f.read()

aside_regex = r'<aside\s+className={`[^`]+`}\s*>'
aside_match = re.search(aside_regex, text, flags=re.DOTALL)

if aside_match:
    old_aside = aside_match.group(0)
    new_aside = """<aside
        className={`
          bg-neutral-50 dark:bg-[#111111] border-r border-neutral-200 dark:border-neutral-800 z-40 flex flex-col flex-shrink-0 relative overflow-visible
          ${isOpen ? "fixed inset-y-0 left-0 translate-x-0" : "max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:-translate-x-full"}
          md:translate-x-0
          ${className}
        `}
        style={{ width: isCollapsed ? 52 : sidebarWidth, transition: isDragging ? 'none' : 'width 0.2s ease' }}
      >
        {!isCollapsed && (
            <div
            onMouseDown={handleMouseDown}
            onDoubleClick={() => setSidebarWidth(260)}
            className="absolute right-0 top-0 w-1.5 h-full cursor-col-resize z-50 hover:bg-[#e05a2b]/30 transition-colors"
            />
        )}"""
    text = text.replace(old_aside, new_aside)

with open("src/components/ui/modern-side-bar.tsx", "w") as f:
    f.write(text)
