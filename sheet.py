#!/usr/bin/env python3
import inspect
import pdb
import re
import sys

class Cell:
    def __init__(self):
        self.id = None
        self.val = None
        self.expr = None
        self.row = None
        self.col = None
        self.children = []
        self.parents = []
    
    def __repr__(self):
        return str(self.val)

class Aggregate:
    def __init__(self):
        self.id = None
        self.expr = None
        self.children = []
        self.parents = []
        self.members = set()

class Row(Aggregate):
    pass

class Column(Aggregate):
    pass

def extract_row_col(cell):
    match = re.search(r'^([a-zA-Z]+)([0-9]+)$', cell)
    return ('_'+match.group(2), match.group(1))

def create_sheet():
    return {}

def get_unit(sheet, id, ctor):
    unit = sheet.get(id)
    if not unit:
        unit = ctor()
        unit.id = id
        sheet[id] = unit
    return unit

def get_cell(sheet, id):
    return get_unit(sheet, id, Cell)

def select_ctor(id):
    if re.search(r'^[a-zA-Z]+$', id):
        return Column
    elif re.search(r'^_[0-9]+$', id):
        return Row
    elif re.search(r'^([a-zA-Z]+)([0-9]+)$', id):
        return Cell
    else:
        raise ValueError(id + 'is not a valid unit.')

def put(sheet, id, value):
    kind = select_ctor(id)

    if kind is Cell:
        cell = get_cell(sheet, id)

        for parent in cell.parents:
            parent.children.remove(cell)
                
        if callable(value):
            new_parents = []
            for pid in list(inspect.signature(value).parameters):
                new_parent = get_unit(sheet, pid, select_ctor(pid))
                new_parent.children.append(cell)
                new_parents.append(new_parent)
            cell.parents = new_parents
        else:
            cell.parents = []

        cell.expr = value

        row, col = extract_row_col(id) 
        cell.row = get_unit(sheet, row, Row)
        cell.col = get_unit(sheet, col, Column)
        cell.row.members.add(cell) 
        cell.col.members.add(cell) 
        
        evaluate(sheet, cell, id) 

        return cell
    else:
        print('Cant handle non cell lvalues yet.')
        return None

def get(sheet, cell):
    if select_ctor(cell) is Cell:
        return get_cell(sheet, cell).val
    else:
        print('get works only on cells')

def evaluate(sheet, cell, id):
    if not callable(cell.expr):
        cell.val = cell.expr
    else:
        args = []
        for parent in cell.parents:
            if type(parent) is Cell:
                args.append(parent.val)
            else:
                args.append([member.val for member in 
                    get_unit(sheet, parent.id, type(parent)).members])

        try:
            cell.val = cell.expr(*args) # All cells maynot be initialized
        except TypeError:
            cell.val = None

    for child in cell.children:
        evaluate(sheet, child, child.id)

    children = cell.row.children + cell.col.children
    for child in children:
        evaluate(sheet, child, child.id)


if __name__ == "__main__":
    s = {}
    pdb.set_trace()
    put(s, 'a1', 10)
    put(s, 'a2', 20)
    put(s, 'b1', lambda a: sum(a))
    get(s, 'b1')


