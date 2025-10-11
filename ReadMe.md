python -m data_util utility db-create food-types 5
python -m data_util utility db-create franchises 46

python -m data_util utility queue-create franchises 500
python -m data_util utility queue-create menus 500 
python -m data_util utility queue-person-create people 10 --periodic-run

alembic revision -m "Add menu_category_id column to menus table"

INSERT INTO public.menus(created_on, modified_on, description, menu_name, menu_category_id)	VALUES (NOW(), NOW(), 'Grilled Steak with Roasted Veggies', 'Grilled Steak with Roasted Veggies', 5);
INSERT INTO public.menus(created_on, modified_on, description, menu_name, menu_category_id)	VALUES (NOW(), NOW(), 'Baked Salmon with Lemon Butter', 'Baked Salmon with Lemon Butter', 5);
INSERT INTO public.menus(created_on, modified_on, description, menu_name, menu_category_id)	VALUES (NOW(), NOW(), 'chocolate, vanilla, or strawberry', 'Milkshakes', 9);

ruff check --diff
ruff check --fix
ruff check
ruff linter -h
ruff format