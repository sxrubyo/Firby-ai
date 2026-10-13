<div align="center">
  <img src="brand-assets/firby-logo.png" alt="Firby AI" width="960"/>

### 💜 **The Autonomous Operator Runtime for Real Business Work**

*Connect tools, apply governance, and let Firby complete real operations—not merely answer chats.*

[![NPM Version](https://img.shields.io/npm/v/%40innvisor%2Ffirby-ai.svg?style=for-the-badge&color=9333ea&logo=npm&logoColor=white)](https://www.npmjs.com/package/%40innvisor%2Ffirby-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-9333ea.svg?style=for-the-badge)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-9333ea.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Production Ready](https://img.shields.io/badge/PRODUCTION-READY-9333ea?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com/sxrubyo/firby)
[![Governance](https://img.shields.io/badge/GOVERNED-ACTIONS-16A34A?style=for-the-badge)](https://github.com/sxrubyo/firby)
[![Telegram](https://img.shields.io/badge/Telegram-READY-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com/sxrubyo/firby)

</div>

---

## 💰 Turn AI Assistants Into Recurring Revenue

**Firby** is a white-label platform for **governed autonomous business operators**. It connects to the tools a company already uses, carries out approved work, and escalates sensitive actions for human approval.

<div align="center">

| Your Client's Pain | What They Pay You For |
|:---|:---|
| 🧾 Repetitive operational work = costly bottlenecks | ⚙️ Autonomous operator that completes governed actions |
| 🔁 Manual handoffs across inboxes and systems | 🔗 Tool-aware execution with durable context |
| ✅ Updating records, schedules, and workflows manually | 🛡️ Guardrailed automation with approval gates, services, prices |
| 📊 No visibility into autonomous work | 📈 Audit trails, daily reporting, and human oversight |

</div>

---

## 🚀 Your Business Model (The Firby Way)

```
┌─────────────────────────────────────────────────────────────┐
│  1. Install Firby (5 minutes)                             │
│     npm install -g /firby-ai                               │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Train ONE agent with a prompt (15 minutes)              │
│     "You are Maria, operator for a dental clinic.       │
│      Book appointments, answer FAQ, send price list."       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Clone to unlimited client instances (1 command)         │
│     firby sync --add /opt/firby-client-restaurant       │
│     firby sync --add /opt/firby-client-salon            │
│     firby sync --add /opt/firby-client-realestate       │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Each client gets their own isolated instance            │
│     ✅ Web, email, and optional messaging integrations                    │
│     ✅ Telegram approvals for governed actions                              │
│     ✅ Custom personality via personas/                     │
│     ✅ Isolated database & credentials                      │
│     ✅ Their own .env — you never touch it again            │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Charge $97–$497/month per client                        │
│     They connect their operating systems and approval channels                       │
│     They define permitted actions and escalation policies             │
│     You maintain the core and sync updates in 1 command     │
└─────────────────────────────────────────────────────────────┘
```

<div align="center">

| Clients | Monthly Fee | Your MRR |
|:---:|:---:|:---:|
| 10 clients | $197/mo | **$1,970/mo** |
| 50 clients | $197/mo | **$9,850/mo** |
| 100 clients | $197/mo | **$19,700/mo** |

**Your cost:** $5–15/mo per client (OpenAI API + server)
**Your margin:** 85–95% 🚀

</div>

---

## 🎯 Why Firby Destroys the Competition

<table>
<tr>
<th width="20%">Solution</th>
<th width="40%">Their Reality</th>
<th width="40%">Firby Reality</th>
</tr>
<tr>
<td><strong>Voiceflow / Botpress</strong></td>
<td>❌ $99–$625/mo per bot<br>❌ Vendor lock-in<br>❌ You pay per conversation</td>
<td>✅ Open source, MIT license<br>✅ Unlimited instances<br>✅ You control pricing</td>
</tr>
<tr>
<td><strong>n8n / Make / Zapier</strong></td>
<td>❌ Complex workflow builders<br>❌ No memory between sessions<br>❌ Breaks with API changes</td>
<td>✅ Zero external dependencies<br>✅ Built-in memory engine<br>✅ 1 command to update all clients</td>
</tr>
<tr>
<td><strong>Hiring a Dev Team</strong></td>
<td>❌ $5,000–$20,000 upfront<br>❌ 3–6 months development<br>❌ Single-client solution</td>
<td>✅ Install in 5 minutes<br>✅ Deploy client in 10 minutes<br>✅ One core, infinite clients</td>
</tr>
<tr>
<td><strong>Custom Python Script</strong></td>
<td>❌ No state management<br>❌ Security nightmare<br>❌ Dies when you restart</td>
<td>✅ Production-grade FastAPI<br>✅ Zero-trust architecture<br>✅ Systemd + Docker ready</td>
</tr>
</table>

---

## ⚡ Start Selling in 3 Steps

### Step 1 — Install Firby

Recommended GitHub installer (always tracks the current `main` branch):

```bash
curl -fsSL https://raw.githubusercontent.com/sxrubyo/firby/latest/install.sh | bash
firby --version
```

Direct GitHub install with npm:

```bash
npm install -g github:sxrubyo/firby#main
firby --version
```

Registry install:

```bash
npm install -g /firby-ai
firby --version
```

### Step 2 — Create Your First Agent

```bash
firby persona create restaurant-operator
```

Edit `personas/restaurant-operator.txt`:

```
You are Sofia, the AI operator for "La Cucina Bella" Italian restaurant.

Your job:
- Answer questions about menu, hours, location
- Take reservations (collect: name, phone, date, time, party size)
- Send the menu PDF when asked
- Be warm, friendly, professional

Hours: Mon–Sun 11am–10pm
Location: 123 Main St, Miami, FL

When someone wants to book:
"Perfect! I'll need your name, phone number, preferred date & time, and party size."

Never confirm reservations — say "I'll pass this to our manager to confirm."
```

### Step 3 — Deploy to Client

```bash
firby sync --add /opt/firby-restaurant-bella
cd /opt/firby-restaurant-bella
cp .env.example .env
nano .env
python3 firby.py
```

**Done.** Their operations now have a governed AI operator. You never touch their credentials again.

---

## 🏗️ Architecture

```
                  ┌──────────────────────────┐
                  │    Your Development Core  │
                  │      ~/firby-dev/       │
                  └────────────┬─────────────┘
                               │  firby sync
                  ┌────────────┼────────────┐
                  │            │            │
         ┌────────▼───┐ ┌──────▼─────┐ ┌───▼────────┐
         │  Client A  │ │  Client B  │ │  Client C  │
         │ Restaurant │ │   Salon    │ │ Real Estate│
         ├────────────┤ ├────────────┤ ├────────────┤
         │ .env       │ │ .env       │ │ .env       │
         │ persona    │ │ persona    │ │ persona    │
         │ database   │ │ database   │ │ database   │
         │ Web/Email  │ │ Telegram   │ │ Optional Msg │
         └────────────┘ └────────────┘ └────────────┘
```

| Module | Purpose |
|:---|:---|
| **`firby.py`** | FastAPI orchestrator — webhooks, routing, concurrency |
| **`firby_brain_v10.py`** | Memory layer — context normalization, conversation history |
| **`firby_domino.py`** | Quality control — validates responses before delivery |
| **`firby_core/`** | Shared conversation logic and state retention |
| **`firby_agents/`** | Pluggable skills — calendar, CRM, payments, custom functions |
| **`personas/`** | Personality configs — tone, language, brand voice per client |

---

## 🔄 Core vs. Instance State

<table>
<tr>
<td width="50%">

### ✅ Synced to all instances

```
firby.py               # Main engine
firby_brain_v10.py     # Memory system
firby_domino.py        # Quality control
firby_core/            # Shared logic
firby_agents/          # Skills & integrations
personas/                # Personality templates
requirements.txt         # Dependencies
```

</td>
<td width="50%">

### ❌ Never synced (instance-specific)

```
.env                     # API keys, secrets
*.db                     # Conversation history
auth_info_*.txt          # optional messaging sessions
logs/                    # Instance logs
backups/                 # Local backups
```

</td>
</tr>
</table>

**Updates are safe.** Sync the engine without ever touching client credentials or data.

---

## 🎮 CLI Reference

```bash
curl -fsSL https://raw.githubusercontent.com/sxrubyo/firby/latest/install.sh | bash
firby --version                  # Check version

firby sync --list                # List all client instances
firby sync --add /opt/client     # Register new client
firby sync --remove /opt/client  # Remove client
firby sync -y                    # Push updates to all clients

firby persona create <name>      # New personality template
firby agent list                 # Show available agents
firby validate                   # Health check — config, deps, files
firby config                     # Panel interactivo: red, modelos, webhooks, Python/venv
firby doctor --fix               # Diagnóstico con auto-reparación de PM2, deps y webhook
```

---

## 🛡️ Security by Design

| Risk | Other Platforms | Firby |
|:---|:---|:---|
| API keys in version control | ❌ Common mistake | ✅ `.env` never synced |
| Shared database across clients | ❌ GDPR violation | ✅ Isolated SQLite per instance |
| Session hijacking | ❌ No isolation | ✅ Separate auth per client |
| Cross-client data contamination | ❌ Possible | ✅ Impossible by design |

---

## 📊 Industry Use Cases

| Industry | What the AI Handles | Suggested Price |
|:---|:---|:---:|
| 🍕 **Restaurants** | Reservations, menu, hours, delivery | $147–$297/mo |
| 💇 **Salons & Spas** | Bookings, services, prices, upsells | $197–$397/mo |
| 🏠 **Real Estate** | Lead qualification, listings, viewings | $297–$597/mo |
| 🦷 **Medical / Dental** | Consultations, forms, reminders | $347–$697/mo |
| 🛒 **E-commerce** | Product questions, order tracking, returns | $197–$497/mo |
| 🏋️ **Gyms & Studios** | Class bookings, schedules, memberships | $197–$397/mo |

---

## 🔥 Production Deployment

### VPS (DigitalOcean, Linode, Vultr — $6/mo)

```bash
npm install -g /firby-ai
firby sync --add /opt/client-001
cd /opt/client-001
cp .env.example .env && nano .env
```

**Systemd service (auto-restart on crash):**

```ini
[Unit]
Description=Firby AI — Client 001
After=network.target

[Service]
WorkingDirectory=/opt/client-001
ExecStart=/usr/bin/python3 /opt/client-001/firby.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable firby-client-001
sudo systemctl start firby-client-001
```

### Docker

```bash
docker run -d \
  --name firby-client-001 \
  -p 8000:8000 \
  -v /opt/client-001:/app \
  --env-file /opt/client-001/.env \
  firby-ai:latest
```

---

## 🗺️ Roadmap

- [ ] Web dashboard for clients (no-code persona editor)
- [ ] Multi-language personas (auto-switch by locale)
- [ ] Built-in analytics — conversation metrics per instance
- [ ] Voice support — Telegram voice → transcription → AI response
- [ ] Redis-backed session sharing for horizontal scaling
- [ ] Plugin marketplace — community agents and skills
- [ ] Edge deployment — Cloudflare Workers / Vercel Edge

---

## 🎓 What You DON'T Need

❌ n8n workflows &nbsp;&nbsp; ❌ Zapier subscriptions &nbsp;&nbsp; ❌ Voiceflow licenses  
❌ AWS Lambda complexity &nbsp;&nbsp; ❌ Kubernetes &nbsp;&nbsp; ❌ Redis (unless 500+ clients)  
❌ PostgreSQL &nbsp;&nbsp; ❌ Docker Swarm &nbsp;&nbsp; ❌ A dev team

**Firby runs on a $6/mo VPS. One server. Dozens of clients.**

---

<div align="center">

## 💜 Ready to Build?

[![Install Now](https://img.shields.io/badge/📦_Install_Now-npm_install_-g_firby--ai-9333ea?style=for-the-badge&logo=npm&logoColor=white)](https://www.npmjs.com/package/%40innvisor%2Ffirby-ai)
[![GitHub Issues](https://img.shields.io/badge/🐛_Issues-Report_Here-9333ea?style=for-the-badge&logo=github)](https://github.com/sxrubyo/firby/issues)
[![Discussions](https://img.shields.io/badge/💬_Community-GitHub_Discussions-9333ea?style=for-the-badge&logo=github)](https://github.com/sxrubyo/firby/discussions)

---

**Built for agencies. Designed for profit. Engineered for scale.**

No vendor lock-in · No recurring SaaS fees · You own the code · You set the price

**Created by [sxrubyo](https://github.com/sxrubyo)** · MIT License · Open Source

</div>
