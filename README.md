# sheet.py
A tiny spreadsheet in Python.

## Names
* Column names are a sequence of uppercase and/or lowercase characters. eg: `'a'`, `'AB'`, `'foo'`.
_Hint: Columns are not ordered. `'A'` does not necessarily come before `'B'`._
* Row names are a sequence of digits. eg: `12`,`0`, `1`.
* Cells are named by their column and row names written together. eg: `'foo12'`, `'A1'`

## Values
A cell can hold any valid Python object as its value.
Formulas can be specified by callables. For eg:
```
lambda a1: a1+1           # The cell's value is one greater than the value in the cell named 'a1'
lambda a2, b2: a2-b2      # Dependency on 2 cells: 'a2' and 'b2'
lambda marks: sum(marks)  # Dependency on the entire column named 'marks'
lambda _1 : len(_1)       # Dependency on row '1'
```

## Operations
There are only 3:
1. `create_sheet()` which returns a new sheet object.
2. `put(sheet, name, value)` which enters the value `value` into the cell named `name`.
3. `get(sheet, name)` which returns the value at the cell named `name`.

## Sample Session
```
# Irrelevant output edited out

>>> from sheet import *
>>> sheet1 = create_sheet()
>>> i = 0
>>> for subject, mark in [('Transfiguration', 70), ('Charms', 72), ('Portions', 74)]:
...   put(sheet1, 'subjects'+str(i), subject)
...   put(sheet1, 'marks'+str(i), mark)
...   i = i + 1
>>> put(sheet1, 'total0', lambda marks: sum(marks))
216
>>> put(sheet1, 'avg0', lambda total0, subjects: total0/len(subjects))
72.0
>>> put(sheet1, 'subjects3', 'Defence Against the Dark Arts')
>>> put(sheet1, 'marks3', 75)
>>> get(sheet1, 'total0')
291
>>> get(sheet1, 'avg0')
72.75



```
