with open("src/components/ui/resizable.tsx", "r") as f:
    text = f.read()

text = text.replace('const ResizablePanelGroup = ({\n  className,\n  ...props\n}: React.ComponentProps<typeof PanelGroup>) => (', 
'const ResizablePanelGroup = ({\n  className,\n  direction,\n  ...props\n}: React.ComponentProps<typeof PanelGroup> & { direction?: "horizontal" | "vertical" }) => (')

text = text.replace('<PanelGroup\n    className={cn(\n      "flex h-full w-full data-[panel-group-direction=vertical]:flex-col",\n      className\n    )}\n    {...props}\n  />',
'<PanelGroup\n    orientation={direction}\n    className={cn(\n      "flex h-full w-full data-[panel-group-direction=vertical]:flex-col",\n      className\n    )}\n    {...props}\n  />')

with open("src/components/ui/resizable.tsx", "w") as f:
    f.write(text)
