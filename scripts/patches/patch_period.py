with open('/home/ubuntu/firby-landing/index.html', 'r') as f:
    content = f.read()

content = content.replace("Un Agente.<br>", "Un Agente<br>")

with open('/home/ubuntu/firby-landing/index.html', 'w') as f:
    f.write(content)
