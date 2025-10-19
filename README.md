python -m data_util utility db-create food-types 5
python -m data_util utility db-create franchises 46

python -m data_util utility queue-create franchises 500
python -m data_util utility queue-create menus 500 
python -m data_util utility queue-person-create people 10 --periodic-run

alembic revision -m "Add menu_category_id column to menus table"

ruff check --diff
ruff check --fix
ruff check

ruff format
