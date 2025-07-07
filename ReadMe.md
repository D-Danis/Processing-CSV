### Скрипт для обработки CSV-файла, поддерживающий операции

-  путь до файла `.csv`
- `--where`- фильтрацию с операторами «`больше`», «`меньше`» и «`равно`»  (>,<,=)   
-  `--aggregate` - агрегацию с расчетом среднего (`avg)`, минимального (`min`) и максимального (`max`) значения
- `--order-by` - сортировки столбцов по возрастанию(`asc`) и убыванию(`desc`)
- `--mediana` - получение медианы по столбцу 

###  Установка
```bash
git clone https://github.com/D-Danis/Processing-CSV
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Пример работы операции

 * #### --where

```bash
python3 main.py products.csv --where "rating > 4.7"
```

```bash
+------------------+---------+---------+----------+
| name             | brand   |   price |   rating |
+==================+=========+=========+==========+
| iphone 15 pro    | apple   |     999 |      4.9 |
+------------------+---------+---------+----------+
| galaxy s23 ultra | samsung |    1199 |      4.8 |
+------------------+---------+---------+----------+
```

```bash
python3 main.py products.csv --where "brand = apple"
```

```bash
+---------------+---------+---------+----------+
| name          | brand   |   price |   rating |
+===============+=========+=========+==========+
| iphone 15 pro | apple   |     999 |      4.9 |
+---------------+---------+---------+----------+
```

* #### --aggregate

```bash
python3 main.py products.csv --aggregate "rating=avg"
```

```bash
+-------+
|   avg |
+=======+
| 4.675 |
+-------+
```

* ####  --where  --aggregate 

```bash
python3 main.py products.csv --where "brand = xiaomi" --aggregate "rating=min"
```

```bash
+-------+
|   min |
+=======+
|   4.4 |
+-------+
```

* #### --order-by

```bash
python3 main.py products.csv --order-by "rating=asc"
```

```bash
+------------------+---------+---------+----------+
| name             | brand   |   price |   rating |
+==================+=========+=========+==========+
| poco x5 pro      | xiaomi  |     299 |      4.4 |
+------------------+---------+---------+----------+
| redmi note 12    | xiaomi  |     199 |      4.6 |
+------------------+---------+---------+----------+
| galaxy s23 ultra | samsung |    1199 |      4.8 |
+------------------+---------+---------+----------+
| iphone 15 pro    | apple   |     999 |      4.9 |
+------------------+---------+---------+----------+
```

* #### --median

```bash
python3 main.py products.csv --median "price"
```

```bash
+---------+
|   price |
+=========+
|     649 |
+---------+
```

###  Тест Processing CSV
* Тестируются ключевые функции парсинга условий.
* Проверяется логика фильтрации (where), агрегации (aggregate), сортировки (order-by) и медианы (median).
* Есть тесты на чтение CSV.
* Есть базовая проверка вызова main() с мокнутыми аргументами.

```bash
pytest -v test_main.py
```

### Процент покрытия код тестами

```bash
pytest --cov=main                  
```

```bash
============ test session starts ============
platform linux -- Python 3.12.7, pytest-8.4.1, pluggy-1.6.0
rootdir: ****
plugins: mock-3.14.1, cov-6.2.1
collected 21 items                                                             

test_main.py .....................                                       [100%]

============ tests coverage ============
___ coverage: platform linux, python 3.12.7-final-0 ___

Name      Stmts   Miss  Cover
-----------------------------
main.py     174     26    85%
-----------------------------
TOTAL       174     26    85%
============ 21 passed in 0.37s =============
```


* В формате **json**

```bash
pytest --cov-report json --cov=main
```
- coverage.json
