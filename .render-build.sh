#!/bin/bash
#Иногда помогает явно указать, что pip должен использовать только wheel-файлы (без компиляции):
# .render-build.sh

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости БЕЗ компиляции
pip install --only-binary=all -r requirements.txt
