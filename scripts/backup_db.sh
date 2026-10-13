#!/bin/bash
# =============================================================================
# SCRIPT DE RESPALDO ATÓMICO Y AUTOMÁTICO DE BASE DE DATOS FIRBY
# =============================================================================
set -e

BACKUP_DIR="/home/ubuntu/firby/backups/db"
DB_SRC="/home/ubuntu/firby/instances/clinica-de-las-americas/firby.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARGET_FILE="${BACKUP_DIR}/firby_firby_${TIMESTAMP}.db"

mkdir -p "$BACKUP_DIR"

if [ -f "$DB_SRC" ]; then
    # Respaldo consistente online con WAL checkpointing seguro
    sqlite3 "$DB_SRC" ".backup '${TARGET_FILE}'"
    gzip -9 "$TARGET_FILE"
    echo "[$(date)] Respaldo completado: ${TARGET_FILE}.gz"
    
    # Mantener solo los últimos 30 días de respaldos
    find "$BACKUP_DIR" -name "*.db.gz" -mtime +30 -delete
else
    echo "[$(date)] Error: No se encontró la base de datos en $DB_SRC" >&2
    exit 1
fi
