# Benni Notification Router

Eine native Home-Assistant-Custom-Integration (HACS-kompatibel), die Ereignisse aus
Doorbell, Haushaltsgeräten, Sicherheitszuständen, Lock-Battery und Systemwarnungen
**kontextabhängig routet**. Dadurch muss kein einzelnes Modul mehr eine eigene
Notification-Logik bauen.

Die Routing-Entscheidung selbst ist eine **reine Python-Funktion** (`routing.decide`)
und ohne Home Assistant testbar.

## Installation (HACS)

1. Repo als Custom-Repository in HACS hinzufügen → Integrations.
2. *Benni Notification Router* installieren, Home Assistant neu starten.
3. *Einstellungen → Geräte & Dienste → Integration hinzufügen* → „Benni Notification Router".
4. Kontext-Entitäten (Bio-State, Activity, Presence, …) und optionale Output-Targets zuordnen.

## Kontext-Eingaben

| Kontext | Erwartete Zustände |
|---|---|
| `bio_state` | `sleep`, `waking`, `awake` |
| `activity_state` | `idle`, `free_time`, `work_home`, `work_away`, `private_time`, `household` |
| `presence_personal` | `zuhause`, `bei_eltern`, `abwesend` (letzteres: nur dies eskaliert wie „abwesend") |
| `media_context` | `on`/`off` |
| `headset_active` | `on`/`off` |
| `quiet_mode_active` | `on`/`off` |
| `doorbell_state` | beliebig (Edge-Trigger) |
| `opening_safety` | beliebig |
| `lock_battery` | numerisch (< 20 → low) oder `low`/`critical`/`on` |

## Outputs

- `sensor.benni_notification_mode` — `silent` | `soft` | `normal` | `urgent` | `critical`
- `sensor.benni_last_notification_event` — letztes geroutetes Ereignis (+ Debug-Attribute)
- `binary_sensor.benni_notification_dnd_active`
- HA-Event `benni_notification_router_event` mit vollständigem Routing-Snapshot

## Services

```yaml
service: benni_notification_router.route
data:
  event_type: doorbell        # doorbell|security|appliance_done|device_health|lock|climate|media|info
  severity: normal            # info|normal|urgent|critical
  title: "Türklingel"
  message: "Jemand steht vor der Tür"
  dedupe_key: doorbell_front  # optional, gegen Spam
  payload: {camera: front}
```

```yaml
service: benni_notification_router.clear
data: {dedupe_key: doorbell_front}      # optional, sonst alles
```

```yaml
service: benni_notification_router.set_dnd
data: {duration: 1800}                   # Sekunden, 0 = aus
```

## Routing-Matrix (Übersicht)

Zeile = Event/Severity, Spalten = Kontextmodifier. ✓ = aktiv, ✗ = unterdrückt, ↧ = weicher Modus.

| Event | Default | + sleep | + waking | + headset | + quiet_mode | + media | + work_home | + private_time | + away | + DND |
|---|---|---|---|---|---|---|---|---|---|---|
| doorbell / normal | push + light + media + dash | bus/dash, soft | push + light | push + light, **no media** | push + light, **no media** | push + light | push + light | push + light, **msg masked** | push + dash, **no light** | push + light only if critical |
| security / urgent–critical | push + persistent + media + light + dash | **immer** push+persistent | dito | push + persistent + light | push + persistent + light | push + persistent + light | dito | dito (kein Mask bei critical) | push + persistent | **bricht DND** |
| appliance_done / normal | push + dash | bus/dash, soft | push | push | push | push | push | push, masked | push | bus/dash |
| device_health / normal | push + dash | bus/dash, soft | push | push | push | push | push | masked | push | bus/dash |
| info / info | dash + bus | dash + bus | dash + bus | dash + bus | dash + bus | dash + bus | dash + bus | masked | dash + bus | dash + bus |
| _critical (any class)_ | push + persistent + media + light + dash | **gleich** | gleich | gleich | gleich | gleich | gleich | **nicht** maskiert | push + persistent | **bricht DND** |

Spezialregeln:
- `bei_eltern` = home-equivalent (keine away-Eskalation).
- Security-Events werden mind. auf `urgent` angehoben.
- `device_health`/`lock` produzieren nie Audio (außer critical).
- `private_time` ersetzt sichtbaren Inhalt durch `(privater Modus)` (außer critical).

## Deduplication & Cooldowns

- `dedupe_key` unterdrückt identische Events innerhalb von 60 s.
- Pro Event-Klasse gibt es Default-Cooldowns (`appliance_done` = 600 s, `doorbell` = 5 s, …), in Options überschreibbar.
- Rate-Limit (default 20/min) gegen Notification-Sturm.
- Persistente Speicherung über `Store` — bleibt über Neustarts erhalten.

## Debug-Attribute

`sensor.benni_notification_mode` exponiert:

- `routes` — tatsächlich gewählte Routen
- `suppressed_routes` — was warum unterdrückt wurde
- `reason` — verkettete Begründung der Routing-Engine
- `context` — vollständiger Kontext-Snapshot zum Entscheidungszeitpunkt
- `severity`, `masked`

## Tests

```bash
python -m pytest tests/
```

Die Routing-Engine ist eine pure Funktion in `custom_components/benni_notification_router/routing.py`
und hat 17 deterministische Tests (Doorbell+Headset, Doorbell+Sleep, Security/DND,
Appliance/Away+Sleep, private_time-Mask, quiet_mode, Dedupe-Serialisierbarkeit, …).

## Architektur

```
┌─────────────────────┐
│  Service: .route    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐    pure        ┌────────────────┐
│ NotificationRouter  │──────────────▶ │ routing.decide │
│ (coordinator.py)    │   Event + Ctx  │   (engine)     │
└─────────┬───────────┘                └────────┬───────┘
          │ dispatch                            │ Decision
          ▼                                     ▼
   notify.* / script / persistent_notification   HA event bus
   sensor / binary_sensor (entities)             benni_notification_router_event
```

V1 implementiert die Service-/Event-Architektur und die Routes `push`, `persistent`,
`light` (script), `media` (script). `dashboard_event` und `bus_only` sind über den
HA-Event-Bus erreichbar — Lovelace/Automations können dort anknüpfen.
