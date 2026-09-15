# Vinolog

Мобильный сканер российских вин для кейса РСХБ Цифра. Репозиторий следует структуре из подробного плана: Nuxt-приложение, общие контракты и отдельная граница будущего CV-сервиса.

## Быстрый старт

Требования: Node.js 22.22.2+ и npm 10+. Версия зафиксирована в `.nvmrc`.

```bash
nvm use
npm install
npm run dev
```

После запуска откройте `http://localhost:3000`. Текущий серверный маршрут работает в демонстрационном mock-режиме и не выполняет настоящее распознавание.

## Команды

```bash
npm run dev        # Nuxt dev server
npm run lint       # ESLint
npm run prepare:nuxt # пересоздать служебные типы Nuxt
npm run typecheck  # Vue/Nuxt type checking
npm run test       # unit tests
npm run build      # production build
npm run check      # все проверки подряд
```

## Структура

- `apps/web` — Nuxt 4: мобильные экраны и server API.
- `packages/contracts` — общие TypeScript-контракты без зависимости от Nuxt.
- `services/retrieval` — граница будущего Python/FastAPI CV-сервиса.
- `docs/engineering` — обязательные правила генерации и изменения кода.
- `ARCHITECTURE.md` — компоненты системы и поток запроса.

## Текущее ограничение

Каркас закрывает пользовательский путь и состояния интерфейса, но возвращает демонстрационную карточку. Подключение SigLIP 2, OCR, pgvector, реального каталога и официального маршрута оценки остаётся отдельным этапом после получения данных и проверочного Bash-скрипта.

## Диагностика TypeScript в редакторе

Папки `.nuxt` и `.output` генерируются фреймворком и не проверяются как самостоятельные TypeScript-проекты. Корневой `tsconfig.json` направляет редактор в Nuxt-конфигурацию, а workspace-настройки исключают служебные файлы из отдельной индексации.

Если редактор показывает ошибки внутри `.nuxt/*.d.ts`, хотя `npm run typecheck` проходит:

```bash
npm run prepare:nuxt
```

Затем выполните в VS Code команды `TypeScript: Select TypeScript Version` → `Use Workspace Version` и `Developer: Reload Window`.
