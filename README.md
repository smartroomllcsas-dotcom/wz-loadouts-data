# wz-loadouts-data

Datos de las armas meta de Warzone que consume [wzcontrol.vercel.app/loadouts/](https://wzcontrol.vercel.app/loadouts/).

- `loadouts.json` — 3 modos (Battle Royale, Resurgence Ranked, Iron Gauntlet), tiers META+A, hasta 15 armas por modo con sus accesorios.
- `generar_loadouts.py` — generador (Python 3, solo stdlib). Fuente: [wzstats.gg](https://wzstats.gg). Sale con código 2 si el esquema de la fuente cambió (y no sobreescribe el JSON previo).

Se actualiza automáticamente cada lunes. Datos de meta vía wzstats.gg. Este proyecto no está afiliado a Activision ni a wzstats.
