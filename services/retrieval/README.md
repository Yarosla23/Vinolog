# Retrieval service

Локальный baseline поиска конкретной карточки по фотографии этикетки. Он строит SIFT-индекс по связанным с CSV изображениям Strapi, получает кандидатов через FLANN, перепроверяет их геометрию через RANSAC и использует Tesseract OCR для переранжирования. Сервис не зависит от Nuxt UI и не использует облачные ключи.

## Запуск

Корневой `docker compose up --build` сначала один раз создаёт индекс в постоянном Docker volume, затем поднимает API:

- `POST /v1/search` — продуктовый ответ `matched | uncertain | not_found`;
- `POST /v1/eval/predict` — строгий ответ `{"slug":"..."}` для скрипта организаторов;
- `GET /v1/wines/{slug}/image` — эталонное изображение карточки из локального датасета;
- `GET /health` — готовность загруженного индекса.

Индекс можно пересобрать после изменения датасета, удалив только его volume:

```bash
docker compose down
docker volume rm vinolog_retrieval-index
docker compose up --build
```

SIFT и Tesseract — измеримый baseline, а не заявленная финальная точность. Следующий этап после отчёта ошибок — добавить визуальные embeddings и улучшить OCR в этом же `SearchService`, сохранив HTTP-контракты.
