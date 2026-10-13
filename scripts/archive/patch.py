with open("/home/ubuntu/firby/src/core/message_sender.py", "r") as f:
    content = f.read()
target = """        except Exception:
            pass
        return {"platform": self.config.PLATFORM}"""
replacement = """        except Exception:
            pass
        normalized_chat_id = str(chat_id or "").lower()
        if any(marker in normalized_chat_id for marker in (
            "@lid", "@s.whatsapp.net", "@g.us", "@broadcast",
        )):
            return {"platform": "whatsapp"}
        return {"platform": self.config.PLATFORM}"""
content = content.replace(target, replacement)
with open("/home/ubuntu/firby/src/core/message_sender.py", "w") as f:
    f.write(content)
