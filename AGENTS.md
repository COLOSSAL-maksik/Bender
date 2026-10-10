# Ответственность и границы Bender

Bender — независимый проект, без dependencies на Studium/Qt/ORM и без общей DB.
Весь implementation, source/tests, packaging, locks, CI, solvers/generation/
graphics, API/CLI/GUI и содержательные исправления пишет исключительно Jules.
Codex разрешён unchanged export существующих bytes и management/privacy data:
root README, AGENTS и три docs/security policies. Он может читать/review/design
границы, но не адаптирует Bender code/tests или инфраструктуру.

Independent packaging/tests/CI bootstrap выполняет Jules после GitHub access
в отдельной task branch. Source migration не подтверждает acceptance BND-01
и не ждёт API/solvers/GUI. API transport: JSON-RPC 2.0 over stdio; HTTP позднее.
Studium client относится к отдельному Studium repo и принадлежит Codex.

Только synthetic fixtures и temporary profiles. Не читать student data,
Studium DB/storage, production logs/backups. Не добавлять private ledger,
task/session IDs, old Git metadata, secrets или operational records.
Policies target-scoped: reviewed material hashes, только подтверждённые noreply,
пустые history contact/raw-log exceptions. Hook не обходить.

Разработку ведёт только владелец при помощи Jules; внешние PR не входят
в текущий процесс. Целевой репозиторий — COLOSSAL-maksik/Bender, Public,
основная ветка main. Лицензирование определено в README: All rights reserved,
открытая лицензия не предоставлена; лицензии сторонних компонентов сохраняются.

После initial push изменения main проходят через PR; обязательные approvals
и второй reviewer не требуются. Force-push и удаление main запрещены.
Required CI checks добавляются отдельно после появления workflows и первых
успешных проверок; отсутствующие checks не требовать.

Push/PR, запуск Actions и изменения sessions Jules требуют соответствующего
разрешения. Bootstrap сам по себе не разрешает запуск Actions. Текущие sessions
не останавливать/retarget без учёта residual work. Новую задачу Jules не запускать
автоматически. Не менять лицензирование без решения владельца и не переписывать
существующую Git history.
