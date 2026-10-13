# PM2 Restart Guard

Antes de reiniciar procesos Firby, ejecutar:

```bash
/home/ubuntu/firby/scripts/preflight_agents.sh
```

Si el preflight falla, no reiniciar.

## Reinicio Seguro

```bash
/home/ubuntu/firby/scripts/preflight_agents.sh
pm2 restart firby-clinica-de-las-americas firby-ovni firby-melissa-x --update-env
```

## Reglas Que Protege

- Produccion usa solo el bot ID `8779529912`.
- Ovni usa solo el bot ID `8749260201`.
- `melissa-x` queda en cuarentena sin token Telegram.
- No hay `WEBHOOK_SECRET` publico con prefijo `conny_`.
- No hay alias `connyai` en Caddy.
- Los prompts activos no vuelven a identidad humana falsa ni a marca Conny.
- El frontend estatico no vuelve a usar `conny_logo`, `conny_master_key` ni `conny_dev_mode`.
