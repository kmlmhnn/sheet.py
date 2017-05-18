#!/usr/bin/env python3
import inspect
import pdb
import re
import sys

class Cell:
    def __init__(self):
        self.val = None
        self.expr = None
        self.children = []
        self.parents = []
    
    def __repr__(self):
        return "*".join([str(x) for x in (self.val, self.expr, self.children, self.parents)])

class Aggregate:
    def __init__(self):
        self.expr = None
        self.children = []
        self.parents = []

    def __repr__(self):
        return "*".join([str(x) for x in (self.expr, self.children, self.parents)])


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
        sheet[id] = unit
    return unit

def get_cell(sheet, id):
    return get_unit(sheet, id, Cell)

def get_row(sheet, id):
    return get_unit(sheet, id, Row)

def get_col(sheet, id):
    return get_unit(sheet, id, Column)

def select_ctor(id):
    if re.search(r'^[a-zA-Z]+$', id):
        return Column
    elif re.search(r'^_[0-9]+$', id):
        return Row
    elif re.search(r'^([a-zA-Z]+)([0-9]+)$', id):
        return Cell
    else:
        raise ValueError(id, 'is not a valid unit.')

def put(sheet, id, value):
    kind = select_ctor(id)

    if kind is Cell:
        cell = get_cell(sheet, id)

        for parent in cell.parents:
            ctor = select_ctor(parent)
            parent = get_unit(sheet, parent, ctor) # parent was a str. Now its a Cell
            parent.children.remove(id)
                
        if callable(value):
            new_parents = list(inspect.signature(value).parameters)
            cell.parents = new_parents
            for parent in new_parents:
                ctor = select_ctor(parent)
                parent = get_unit(sheet, parent, ctor)
                parent.children.append(id)

        else:
            cell.parents = []

        cell.expr = value
        evaluate(sheet, cell, id) 

        return cell
    else:
        print('Cant handle non cell lvalues yet.')
        return None

def get(sheet, cell):
    return get_cell(sheet, cell).val

def evaluate(sheet, cell, id):
    if not callable(cell.expr):
        cell.val = cell.expr
    else:
        args = []
        for parent in cell.parents:
            ctor = select_ctor(parent)
            if ctor is Cell:
                args.append(get_cell(sheet, parent).val)
            else:
                args.append([get_cell(sheet, id).val for id in get_cells_in_aggregate(sheet, parent, ctor)])

        try:
            cell.val = cell.expr(*args) # All cells maynot be initialized
        except TypeError:
            cell.val = None

    for child in cell.children:
        evaluate(sheet, get_cell(sheet, child), child)

    row, col = extract_row_col(id) 
    children = get_row(sheet, row).children + get_col(sheet, col).children
    for child in children:
        evaluate(sheet, get_cell(sheet, child), child)


def get_cells_in_aggregate(sheet, agg, ctor):
    if ctor is Column:
        pattern = r'^%s[0-9]+$' % agg
    else:
        pattern = r'^[a-zA-Z]+%s$' % agg[1:]

    cells = []
    for id in sheet.keys():
        if re.search(pattern, id):
            cells.append(id)
    return [id for id in cells]
    


