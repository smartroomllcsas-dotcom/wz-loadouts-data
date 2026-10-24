"""Genera loadouts.json con la meta semanal de Warzone desde wzstats.gg.

Fuentes (verificadas 2026-10-24, sin auth):
  1. https://wzstats.gg/  -> <script id="ng-state"> JSON -> tier list + 270 armas
  2. https://app.wzstats.gg/v3/bor/builds/{weaponId}/ -> builds con 5 accesorios

Uso: python generar_loadouts.py [salida.json]
Sale 0 si todo bien; 2 si el esquema de wzstats cambio (NO sobreescribe el json previo).
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) wzcontrol-loadouts/1.0"}
MODOS = {
    "blackOpsRoyale": "Battle Royale",
    "rankedResurgence": "Resurgence Ranked",
}
MAX_ARMAS_POR_MODO = 15          # META + A hasta este tope
TIERS_INCLUIDOS = ("META", "A")


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else "loadouts.json"

    html = get("https://wzstats.gg/")
    m = re.search(r'<script id="ng-state" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        print("ERROR: no se encontro ng-state en wzstats.gg (cambio de esquema)")
        return 2
    state = json.loads(m.group(1))

    store = None
    for k, v in state.items():
        if isinstance(v, dict) and "wzStatsTierList" in v and "weapons" in v:
            store = v
            break
    if not store:
        print("ERROR: ng-state sin wzStatsTierList/weapons (cambio de esquema)")
        return 2

    armas = {w["id"]: w for w in store["weapons"]}
    tierlist = store["wzStatsTierList"]

    data = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fuente": "wzstats.gg",
        "actualizado_fuente": tierlist.get("updatedAt"),
        "modos": {},
    }

    for modo_key, modo_nombre in MODOS.items():
        tiers = tierlist.get(modo_key)
        if not isinstance(tiers, dict):
            print(f"ERROR: modo {modo_key} ausente en tier list (cambio de esquema)")
            return 2
        lista = []
        for tier in TIERS_INCLUIDOS:
            for wid in tiers.get(tier, []):
                if len(lista) >= MAX_ARMAS_POR_MODO:
                    break
                w = armas.get(wid)
                if not w:
                    continue
                try:
                    builds = json.loads(get(f"https://app.wzstats.gg/v3/bor/builds/{w['id']}/"))
                except Exception as e:
                    print(f"  aviso: builds de {w.get('name')} fallo ({e}); se omite")
                    continue
                time.sleep(1.2)  # cortesia
                build = builds[0] if builds else None
                acc = [
                    {"slot": a.get("slot"), "nombre": a.get("name")}
                    for a in (build.get("attachments") if build else []) or []
                ]
                if not acc:
                    continue  # sin build publicado: no sirve como loadout
                t = w.get("type") or {}
                lista.append({
                    "id": w["id"],
                    "nombre": w.get("name"),
                    "tipo": t.get("name"),
                    "tipo_full": t.get("fullName"),
                    "categoria": w.get("category"),
                    "tier": tier,
                    "accesorios": acc,
                })
        if not lista:
            print(f"ERROR: 0 armas resueltas para {modo_key}")
            return 2
        data["modos"][modo_key] = {"nombre": modo_nombre, "armas": lista}

    with open(salida, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    total = sum(len(m["armas"]) for m in data["modos"].values())
    print(f"OK: {salida} con {total} armas en {len(data['modos'])} modos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
