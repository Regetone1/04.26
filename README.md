# Лабораторная работа №3 — работа с уязвимостями

**Вариант:** https://github.com/tensorflow/tensorflow  
**Версия проекта:** TensorFlow v2.7.0, релиз 2021 года  
**Дистрибутив ОС:** Linux Mint 21.3 Virginia

Проект содержит скрипты для выполнения задач 1–3:

1. сбор зависимостей проекта в `result_task_1.json`;
2. проверка зависимостей через GitHub Security Advisory GraphQL API и формирование `result_task_2.json`;
3. анализ уязвимых зависимостей и формирование таблицы `result_task_3.json` / `result_task_3_table.md`.

Итоговые файлы лежат в папке `results/`. В реальный GitHub-репозиторий их выгружать не нужно: они добавлены в `.gitignore`, так как по заданию итоговые результаты не должны попадать в репозиторий.

## Структура проекта

```text
lab3_tensorflow_linuxmint_project/
├── data/
│   ├── tensorflow_v2_7_dependencies.json      # воспроизводимый снимок зависимостей TensorFlow v2.7.0
│   └── offline_ghsa_tensorflow_v2_7.json      # offline-снимок GHSA для демонстрации без токена
├── docs/
│   ├── Отчет_Лабораторная_3_TensorFlow.docx   # готовый отчет
│   └── os_scan_linux_mint_21_3.md             # команды для проверки Linux Mint 21.3
├── results/
│   ├── result_task_1.json
│   ├── result_task_2.json
│   ├── result_task_3.json
│   └── result_task_3_table.md
├── src/
│   ├── collect_task1.py
│   ├── scan_task2_ghsa.py
│   ├── analyze_task3.py
│   └── run_all.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Быстрый запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py
```

После выполнения будут созданы/обновлены файлы:

```text
results/result_task_1.json
results/result_task_2.json
results/result_task_3.json
results/result_task_3_table.md
```

## Запуск с реальным GitHub Security Advisory GraphQL API

По умолчанию используется offline-снимок, чтобы проект можно было показать без GitHub-токена. Для реальной проверки через API нужно создать GitHub Personal Access Token и выполнить:

```bash
export GITHUB_TOKEN="ghp_..."
python src/collect_task1.py
python src/scan_task2_ghsa.py --online
python src/analyze_task3.py
```

На Windows PowerShell переменная задаётся так:

```powershell
$env:GITHUB_TOKEN="ghp_..."
python src\collect_task1.py
python src\scan_task2_ghsa.py --online
python src\analyze_task3.py
```

## Как выгрузить код в GitHub с verified-коммитом

```bash
git init
git add README.md requirements.txt .gitignore src data docs/os_scan_linux_mint_21_3.md
git commit -S -m "Add lab 3 vulnerability scanner for TensorFlow"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

Проверка подписи последнего коммита:

```bash
git log --show-signature -1
```

## Что не коммитить

Не нужно выгружать в GitHub:

- `results/result_task_1.json`;
- `results/result_task_2.json`;
- `results/result_task_3.json`;
- `results/result_task_3_table.md`;
- готовый Word-отчёт из `docs/*.docx`.
