# Telegram Usage Guide

## Команды:
* `/run <задача>` — применить и протестировать (кодовые задачи)
* `/dryrun <задача>` — только diff (без применения)
* `/smoke host=<host>` — staging-smoke: `/health` и `/metrics`
* `/deploy host=<host> ref=<main|branch>` — деплой ветки/рефа на staging
* `/promote host=<host> tag=<image_tag>` — продвинуть собранный образ на staging
* `/rollback host=<host> to=<prev|tag>` — откат на предыдущий или конкретный tag

## Примеры:

```
/use people_counter
/smoke host=staging.example.com
/deploy host=staging.example.com ref=main
/promote host=staging.example.com tag=abc1234
/rollback host=staging.example.com to=prev
```

## Натуральные фразы:

Можно писать простыми словами:
- "staging-smoke для people_counter host=staging.local"
- "deploy to staging host=192.168.1.100 ref=main"
- "promote image host=staging.example.com tag=abc1234"
- "rollback release host=staging.local to=prev"

## OPS операции:

### Smoke Check
Проверяет что staging сервис работает:
1. GET `/health` → `{"ok": true}`
2. GET `/metrics` → содержит `version.git_sha`, `version.image_tag`, `profile.active="staging"`

### Deploy
Деплоит указанную ветку на staging через Ansible

### Promote
Продвигает готовый Docker образ на staging

### Rollback
Откатывает версию на предыдущую или указанный tag