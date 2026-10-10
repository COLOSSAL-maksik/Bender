# Bender

Самостоятельный вычислительный проект для генерации и аналитического решения
задач сопротивления материалов, эпюр, независимых проверок и пошаговых объяснений.
Сейчас это частный source candidate: skeleton, BND-00 architecture checks,
BND-01 data foundation и Axial1D benchmark specification/tests сохранены unchanged.
Наличие этих файлов не означает review/acceptance, готовые solvers или release.

## Граница готовности

Packaging, lock, independent test fixtures и CI ещё не подготовлены. Их
bootstrap делает исключительно Jules после подключения нового GitHub repo.
Поддерживаемого install command, wheel, CLI, API или GUI здесь пока нет.
Не использовать monorepo Qt/ORM/Studium environment как proof независимости.
API/solvers/GUI не являются условиями сохранения этого source candidate.

Bender работает независимо от Studium, без общей DB или обязательного cloud.
Первый будущий API transport — JSON-RPC 2.0 over stdio; HTTP и собственный GUI
допускаются как последующие adapters. Bender API пишет Jules, Studium client
Codex; implementation интеграции здесь не добавлен.

docs/bender содержат unchanged архитектурный snapshot: прежние упоминания
внутреннего subsystem/import integration подлежат review Jules при bootstrap.
Для границ текущего репозитория использовать этот README и AGENTS.
License и publication не согласованы. Private migration provenance/handoff
и остаточные задачи находятся вне source tree; Actions не запускались.
