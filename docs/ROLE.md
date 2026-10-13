# Firby Base/Admin

## Identidad

- ID registry: `base`
- Rol: `admin-base`
- Proceso PM2: `firby`
- Puerto: `8001`

## Responsabilidad

Base administrativa/local del proyecto Firby. No debe atender bots de Telegram de cliente ni de Ovni.

## Telegram

- Token esperado: ninguno
- Webhook publico: no debe registrar un bot productivo

## Reglas

- No usar tokens de produccion ni de Ovni.
- No actuar como instancia demo o cliente.
- Cambios operativos deben pasar `/home/ubuntu/firby/scripts/preflight_agents.sh`.
