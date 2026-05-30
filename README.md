# Лабораторная работа №3 — работа с уязвимостями

Вариант: https://github.com/tensorflow/tensorflow  
ерсия проекта: TensorFlow v2.7.0, релиз 2021 года  
Дистрибутив ОС: Linux Mint 21.3 Virginia

1. сбор зависимостей проекта в `result_task_1.json`;
2. проверка зависимостей через GitHub Security Advisory GraphQL API и формирование `result_task_2.json`;
3. анализ уязвимых зависимостей и формирование таблицы `result_task_3.json` / `result_task_3_table.md`.

## Быстрый запуск

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_all.py 