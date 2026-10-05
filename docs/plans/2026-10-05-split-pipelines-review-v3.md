# Codex review of design v3 (gpt-6.1-sol, reasoning high, read-only, blocker-only scope) — 2026-10-05

REWORK

| # v2 | Находка | Статус | Основание в v3 |
|---|---|---|---|
| 1 | Финальный QA блокирует слайсы | CLOSED | D3 разделяет Done слайса и завершение инициативы |
| 2 | INDEX нужен раньше создания | WRONG | Создание перенесено, но источник требований для ролей противоречив; см. ниже |
| 3 | Исторический v1 неотличим от нового | CLOSED | Новый валидатор принимает только v2; история не перевалидируется |
| 4 | Повторный QA теряет покрытие/snapshot | DEFERRED-TO-TEST (acceptable) | Фаза 2: покрытие, актуальность snapshot, проверка применимости |
| 5 | Runner несовместим с hash-манифестом | CLOSED | D3 различает commit/manifest и отдельно хранит base HEAD |
| 6 | CI-job не доказывает каждую команду | DEFERRED-TO-TEST (acceptable) | Фаза 2: command-level artifact, точный attempt и происхождение |
| 7 | Недостаточный контракт INDEX | DEFERRED-TO-TEST (acceptable) | Фаза 2: нормативное поведение, методы проверки, ссылки и метки |
| 8 | OBS-отклонение несовместимо с command gate | DEFERRED-TO-TEST (acceptable) | Фаза 3: raw результаты отделены от parity verdict |
| 9 | Неполные условия Released | DEFERRED-TO-TEST (acceptable) | D3 задаёт условия; фаза 2 проверяет receipt, smoke и порядок INDEX |
| 10 | Противоположные правила ratchet | CLOSED | D6: абсолютные лимиты для новых единиц, запрет ухудшения существующих |
| 11 | Буквальная проверка всех путей | CLOSED | D1 ограничивает проверку package-local ссылками |
| 12 | Излишнее дробление references | CLOSED | D5 группирует references по целостным контрактам |

1. **blocker — два источника требований для existing-system до Released.**

   **Где:** [v3:120](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:120), [v3:126](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:126); текущий [role-inputs.md:14](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/role-inputs.md:14).

   **Проблема:** existing-system сразу использует INDEX как реестр, но следующая общая инструкция **всем ролям** требует до первого Released читать AC/QR из PRD. Закрытие #2 вводит противоречие в выборе нормативного источника. Тесты формата INDEX этот выбор не разрешают.

   **Сценарий провала:** существующая система ещё не Released; Product утверждает AC изменения в INDEX. PRD отсутствует либо содержит прежнее поведение. Consistency и QA по общей инструкции получают отсутствующие или устаревшие требования; по специальной инструкции должны получить другой набор. Реализация вынуждена самостоятельно выбрать, какое правило нарушить.

   **Правка:** ограничить правило «PRD до Released» режимом new-product. Для existing-system явно закрепить INDEX как источник входов всех ролей начиная с шага 4. В фазу 3 добавить сценарий: existing-system без Released и PRD получает утверждённые критерии из INDEX.

Других блокеров уровня дизайна не обнаружено.

Проверено: версии документов, текущие контракты и валидатор; 21 тест — PASS, exit 0. CLI-тест с записью файлов, CI и пробные прогоны не запускались. Файлы не изменены.