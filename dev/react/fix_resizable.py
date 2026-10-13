with open("src/components/ui/resizable.tsx", "r") as f:
    text = f.read()

text = text.replace('import * as ResizablePrimitive from "react-resizable-panels"', 'import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels"')

text = text.replace('ResizablePrimitive.PanelGroup', 'PanelGroup')
text = text.replace('ResizablePrimitive.Panel', 'Panel')
text = text.replace('ResizablePrimitive.PanelResizeHandle', 'PanelResizeHandle')

with open("src/components/ui/resizable.tsx", "w") as f:
    f.write(text)
