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

Новые remote/push/PR/Actions/Jules session changes и publication требуют
соответствующего разрешения. Текущие sessions не останавливать/retarget без
учёта residual work. Required CI приоритетны; second reviewer отдельно.
Не выбирать license/final remote name и не переписывать source history.
