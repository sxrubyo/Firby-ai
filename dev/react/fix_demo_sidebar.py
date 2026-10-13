with open("src/components/ui/demo-side-bar.tsx", "r") as f:
    text = f.read()

import re

header_regex = r'<div\s+className={`flex items-center \${isCollapsed \? "flex-col py-5 gap-4" : "justify-between p-5"}.*?</div>'

new_header = """<div
        className={`flex items-center ${isCollapsed ? "flex-col py-5 cursor-pointer" : "justify-between p-5"} border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#111111]/60`}
        onMouseEnter={() => { if(isCollapsed) setIsCollapsed(false); }}
        onClick={() => { if(isCollapsed) setIsCollapsed(false); }}
      >
        {!isCollapsed && (
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center">
              <img
                  src="/dev-portal/isotype.png"
                  alt="Firby"
                  className="w-full h-full object-contain brightness-0 opacity-80 dark:invert dark:opacity-70"
              />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-neutral-900 dark:text-white text-sm">{profile.name}</span>
              <span className="text-[10px] text-neutral-500 dark:text-neutral-600 dark:text-neutral-400">Workspace</span>
            </div>
          </div>
        )}

        {isCollapsed && (
            <div className="w-8 h-8 rounded-lg flex items-center justify-center hover:scale-105 transition-transform" title="Expand Sidebar">
              <img
                  src="/dev-portal/isotype.png"
                  alt="Firby"
                  className="w-full h-full object-contain brightness-0 opacity-80 dark:invert dark:opacity-70"
              />
            </div>
        )}

        {!isCollapsed && (
          <button
              onClick={(e) => { e.stopPropagation(); setIsCollapsed(true); }}
              className={`p-1.5 rounded-md text-neutral-500 hover:bg-neutral-200 dark:hover:bg-neutral-800 transition-colors`}
              title="Collapse Sidebar"
          >
              <PanelLeftClose className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
          </button>
        )}
      </div>"""

text = re.sub(header_regex, new_header, text, flags=re.DOTALL)

with open("src/components/ui/demo-side-bar.tsx", "w") as f:
    f.write(text)
