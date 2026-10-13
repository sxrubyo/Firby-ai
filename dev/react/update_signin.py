with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "r") as f:
    text = f.read()

import re
text = text.replace('bg-[#FBF8F3] dark:bg-muted/20', 'bg-[#05050A] dark:bg-[#05050A]')
text = re.sub(r'logoSrc="data:image[^"]+"', 'logoSrc="/isotype.png"', text)

with open("/home/ubuntu/firby-dev-react/src/app/sign-in/page.tsx", "w") as f:
    f.write(text)
