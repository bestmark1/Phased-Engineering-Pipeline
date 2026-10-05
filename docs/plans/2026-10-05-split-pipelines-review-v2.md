# Codex review of design v2 (gpt-6.1-sol, reasoning high, read-only) — 2026-10-05

REWORK

## A. Статус 15 находок v1

1. **CLOSED** — D2 добавляет bootstrap, проверку принятого snapshot и возврат после восстановления спек.
2. **PARTIAL** — INDEX назначен источником требований, но не определены его полный нормативный формат и создание для existing-system до Released.
3. **PARTIAL** — CI-запись структурирована; проверка происхождения не связывает repository/workflow/attempt и конкретную команду с receipt.
4. **CLOSED** — CI/local стали альтернативными формами; legacy FAIL сохраняет ненулевой exit code и baseline exception.
5. **PARTIAL** — два прохода разделены, но агрегирование покрытия и обновление evidence после repair не определены.
6. **PARTIAL** — роли и записи назначены; в последовательности D7 отсутствует отдельный Consistency (`product`) перед Architect.
7. **PARTIAL** — OBS отделены от AC; регистрация OBS и отклонений требует INDEX раньше предусмотренного момента его создания.
8. **PARTIAL** — baseline, suite SHA и required gate появились; исполнение замороженной suite и обработка разрешённых падений оставлены исполнителю.
9. **CLOSED** — разделены импорты, трассируемость и assertions; определены helpers, внешние mocks и негативные примеры.
10. **CLOSED** — таблица задаёт обязательность по depth, отсутствие инструментов и роль критика тестов.
11. **PARTIAL** — конфигурация и версии закреплены; абсолютные лимиты изменённого кода противоречат правилу «падает только на ухудшении».
12. **PARTIAL** — release record введён; не определены условия принятия smoke и проверяемая ссылка на принятый Done receipt.
13. **CLOSED** — D5 наследует hillclimbing, авторизацию commit и откат только собственного patch.
14. **PARTIAL** — история сохраняется, но D9 автоматически относит Full/Lite к new-product вопреки классификации по происхождению и состоянию в D2.
15. **PARTIAL** — появились негативные тесты и замер контекста; проверка всех упомянутых путей смешивает ресурсы пакета с будущими файлами проекта.

## B/C. Находки

1. **blocker · B — финальный QA блокирует промежуточные слайсы.**
   **Где:** [v2:90](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:90), [v2:196](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:196), [qa-prompt:265](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/qa-prompt.md:265).
   **Проблема:** D3 включает финальный clean-checkout QA в Done, тогда как D7 ставит его после всех слайсов. Сохранённый контракт финального QA требует всех активных AC/QR.
   **Сценарий провала:** Product уже утвердил AC исправления ошибки; первый слайс только характеризует прежнее поведение. Финальный QA отклоняет его, следующий слайс исправления недоступен. Аналогично блокируется walking skeleton нового продукта.
   **Правка:** разделить Done слайса и завершение инициативы. Для слайса проверять назначенные критерии и затронутые регрессии; полный clean-checkout QA оставить обязательным завершающим gate.

2. **blocker · B — INDEX нужен раньше собственного создания.**
   **Где:** [v2:102](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:102), [v2:120](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:120), [v2:210](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:210).
   **Проблема:** INDEX создаётся при первом Released, но existing-system требует записывать туда OBS→AC до завершения изменяющих слайсов.
   **Сценарий провала:** локальная legacy-система ещё не Released. Согласованное исправление ломает OBS, но зарегистрировать разрешённое отклонение негде; parity блокирует Done.
   **Правка:** определить создание реестра existing-system до характеризации, его автора и approval. Отдельно определить bootstrap INDEX для мигрированных проектов, чей первый релиз уже состоялся.

3. **major · B — offline-валидатор не может отличить исторический v1 от нового.**
   **Где:** [v2:54](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:54), [v2:222](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:222), [validate_gate.py:27](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/scripts/validate_gate.py:27).
   **Проблема:** «только уже принятые фазы» — внешний факт; текущий интерфейс получает лишь сам receipt. Источник исторической принадлежности не задан.
   **Сценарий провала:** новый receipt объявляет `schema_version: 1` и проходит без обязательного evidence v2.
   **Правка:** обычный режим принимает только v2; проверка архива v1 — отдельный явный режим, не разрешающий новый Done. Если история участвует в переходах, закрепить список принятых receipts и их hashes при миграции.

4. **major · B — повторный слепой QA теряет покрытие либо использует устаревший snapshot.**
   **Где:** [v2:140](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:140), [gate-policy:84](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/gate-policy.md:84), [gate-policy:112](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/gate-policy.md:112).
   **Проблема:** shared envelope хранит findings, но не список успешно проверенных критериев. Правил сборки двух проходов и частичного повторного прогона нет; изменённый snapshot инвалидирует зависимое evidence.
   **Сценарий провала:** после repair AC-001 проверяется на SHA B, остальные PASS остаются на SHA A. Агрегатор либо смешивает snapshots, либо объявляет полный PASS по неполному прогону B.
   **Правка:** добавить явное покрытие критериев и правила инвалидации обоих проходов. Для финального QA все обязательные доказательства должны относиться к текущему snapshot; перенос прежнего результата требует определённого механизма проверки применимости.

5. **major · B — runner несовместим с разрешённым hash-манифестом.**
   **Где:** [v2:9](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:9), [v2:69](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:69), [gate-policy:119](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/gate-policy.md:119).
   **Проблема:** snapshot может быть hash-манифестом незакоммиченных изменений, но каждый command требует `head_sha == snapshot`.
   **Сценарий провала:** проверки выполнены на разрешённом незакоммиченном patch; HEAD содержит SHA A, snapshot — hash M. Корректное evidence отклоняется, возникает незаявленная обязательность commit.
   **Правка:** различить commit snapshot и manifest snapshot. Local-запись должна связываться с проверенным snapshot, отдельно хранить base HEAD и состояние дерева; CI и финальный checkout требуют commit snapshot.

6. **major · B — CI-job не доказывает исполнение каждой command-записи.**
   **Где:** [v2:58](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:58), [v2:73](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:73), [gate-policy:107](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/gate-policy.md:107).
   **Проблема:** предложенный `gh run view` не фиксирует требуемый attempt/workflow и не даёт исходный exit code каждой команды. Не задано соответствие command→job/step.
   **Сценарий провала:** успешный job не запускал заявленный eval; либо receipt относится к attempt 1, а проверяется повторный attempt 2. Формальная запись согласована, фактическое доказательство другое.
   **Правка:** получать точный repository/run/attempt, проверять workflow и job. CI должен публиковать command-level артефакт с командой, exit code и failure signatures, включая случаи пропуска; coordinator сопоставляет его с receipt.

7. **major · B — контракт INDEX недостаточен для QA и `check_index.py`.**
   **Где:** [v2:105](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:105), [product-prompt:157](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/product-prompt.md:157).
   **Проблема:** «краткое поведение + ссылка на evidence» не гарантирует сохранения Given/When/Then и Verified by. Не задан синтаксис ID в спеках, OBS-записей и признак «новая спека». Текущий PRD также не содержит единой таблицы AC/QR для заявленного переноса.
   **Сценарий провала:** QA после заморозки получает сокращённый критерий без условий ошибки; checker считает упоминание ID в комментарии трассируемостью или не может отличить историческую retired-спеку от новой.
   **Правка:** задать минимальный формат реестра и metadata спек: полное нормативное поведение, метод проверки, типизированные ссылки, OBS/отклонения и происхождение записей. Назвать gate, запускающий checker, и определить его действие до Released.

8. **major · B — разрешённое OBS-отклонение не представимо обычным command gate.**
   **Где:** [v2:208](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:208), [v2:213](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:213), [gate-policy:109](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/references/gate-policy.md:109).
   **Проблема:** замороженная OBS-suite закономерно падает после разрешённого изменения. Ненулевой command exit блокирует gate; baseline exception не подходит, если baseline был зелёным.
   **Сценарий провала:** исправлено утверждённое ошибочное поведение, OBS→AC записано, но старый assertion возвращает exit 1 и Done невозможен.
   **Правка:** определить parity runner, который сохраняет raw old/new результаты и отдельно возвращает verdict сравнения. Разрешённый delta должен быть конкретнее ссылки OBS→AC. Указать способ исполнения suite из `suite_sha` на другом product SHA и состав замороженных support/fixtures/config.

9. **major · B — условия перехода в Released не определены полностью.**
   **Где:** [v2:92](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:92), [v2:102](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:102).
   **Проблема:** record содержит smoke «с результатами», но не требует полного PASS; `done_snapshot` не ссылается на конкретный принятый receipt. Создание INDEX и Consistency при первом Released меняет артефакты уже проверенного snapshot без описанного порядка.
   **Сценарий провала:** записаны одинаковые SHA и smoke UNKNOWN, после чего coordinator отмечает Released; либо INDEX создаётся после Done и остаётся вне принятого набора требований.
   **Правка:** определить release schema, ссылку на принятый Done receipt и правило «все утверждённые smoke выполнены и PASS». Подготовку INDEX и Consistency завершать до принятия release snapshot либо явно определить отдельный проверяемый snapshot метаданных.

10. **major · B — два правила ratchet дают противоположный verdict.**
    **Где:** [v2:175](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:175).
    **Проблема:** required gate падает «только на новых или ухудшенных нарушениях», но абсолютные лимиты применяются ко всему изменённому коду.
    **Сценарий провала:** функция имела complexity 20; исправление снижает её до 18. Ratchet принимает улучшение, абсолютный лимит 10 отклоняет тот же patch.
    **Правка:** определить приоритет: абсолютный предел для новых единиц, запрет ухудшения для существующих — либо явно выбрать другой вариант. Закрепить пример улучшения существующего нарушения в тестах.

11. **major · B/C — проверка всех упомянутых путей неосуществима буквально.**
    **Где:** [v2:27](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:27), [v2:237](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:237).
    **Проблема:** `.md` содержит ресурсы скилла, будущие файлы проекта, placeholders, glob-пути и примеры. Последние не должны существовать внутри пакета. Общий сканер потребует исключений без полезного усиления проверки упаковки.
    **Сценарий провала:** автономный пакет отклоняется из-за отсутствия `SPEC_PLAN/releases/<n>.json` или `specs/support/`.
    **Правка:** проверять явно обозначенные package-local ссылки/ресурсы и запрет выхода за корень. Проектные пути проверять отдельными сценариями исполнения.

12. **minor · C — правило «каждое новое правило — отдельный reference» создаёт лишнее дробление.**
    **Где:** [v2:155](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:155), [v2:248](/Users/bestmark1/.claude/skills/phased-engineering-pipeline/docs/plans/2026-10-05-split-pipelines-design.md:248).
    **Проблема:** граница «правила» не задана. Проверки runner, INDEX, двух проходов и release могут превратиться в множество файлов с одинаковым условием загрузки. Для одного владельца это увеличивает навигацию и число загрузок без уменьшения нужного контекста.
    **Сценарий провала:** coordinator загружает несколько мелких references ради одного перехода Done; части единого контракта расходятся при обновлении.
    **Правка:** зафиксировать компактный перечень references по целостным контрактам. Отдельный файл оправдан отдельным условием загрузки; связанные проверки держать вместе.

Проверено: документы и текущие контракты; 21 тест валидатора — PASS, exit 0. Файлы не изменены. CLI-тест с временными файлами, CI и прогоны v2 не запускались; выводы о v2 относятся к проекту контракта, а не к готовой реализации.