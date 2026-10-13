import os

files = [
    '/home/ubuntu/firby/src/domain/prompts/prospect_pitch.py',
    '/home/ubuntu/.firby/repo/src/domain/prompts/prospect_pitch.py'
]

for file in files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
        
        # Replace the bad prompt examples
        content = content.replace(
            'soy una recepcionista virtual',
            'soy una asistente de inteligencia artificial de demostración'
        )
        content = content.replace(
            'una recepcionista virtual creada por Innvisor',
            'una inteligencia artificial de demostración creada por Innvisor'
        )
        
        with open(file, 'w') as f:
            f.write(content)

print("Patched prospect!")
