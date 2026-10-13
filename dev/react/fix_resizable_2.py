with open("src/components/ui/resizable.tsx", "r") as f:
    text = f.read()

text = text.replace('import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels"', 'import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from "react-resizable-panels"')

with open("src/components/ui/resizable.tsx", "w") as f:
    f.write(text)
