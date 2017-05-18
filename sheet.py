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

def extract_row_col_ids(cell_id):
    match = re.search(r'^([a-zA-Z]+)([0-9]+)$', cell_id)
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

def get_type(id):
    if re.search(r'^[a-zA-Z]+$', id):
        return 'Column'
    elif re.search(r'^_[0-9]+$', id):
        return 'Row'
    elif re.search(r'^([a-zA-Z]+)([0-9]+)$', id):
        return 'Cell'
    else:
        return None

def get_ctor(id):
    if re.search(r'^[a-zA-Z]+$', id):
        return Column
    elif re.search(r'^_[0-9]+$', id):
        return Row
    elif re.search(r'^([a-zA-Z]+)([0-9]+)$', id):
        return Cell
    else:
        return None




def put(sheet, id, value):
    try:
        # pdb.set_trace()
        cell = get_cell(sheet, id)

        row_id, col_id = extract_row_col_ids(id) # Raises exception

        for parent_id in cell.parents:
            ctor = get_ctor(parent_id)
            parent = get_unit(sheet, parent_id, ctor)
            parent.children.remove(id)
                
        # old parents' children list is now ok.

        if callable(value):
            
            new_parents = list(inspect.signature(value).parameters)

            cell.parents = new_parents

            for parent_id in new_parents:
                ctor = get_ctor(parent_id)
                parent = get_unit(sheet, parent_id, ctor)
                parent.children.append(id)


        else:
            cell.parents = []

        cell.expr = value
        evaluate(sheet, cell, id) # evaluate works only on individual cells
        # Hence id must be a cell_id.

        return cell
    except:
        # print(id + ' is not a valid cell.', file=sys.stderr)
        print('oops')
        return None

def get(sheet, cell_id):
    return get_cell(sheet, cell_id).val

def evaluate(sheet, cell, cell_id):
    if not callable(cell.expr):
        cell.val = cell.expr
    else:
        args = []
        for parent_id in cell.parents:
            ctor = get_ctor(parent_id)
            if ctor == Cell:
                args.append(get_cell(sheet, parent_id).val)
            else:
                args.append([get_cell(sheet, id).val for id in get_cells_in_aggregate(sheet, parent_id, ctor)])

        try:
            cell.val = cell.expr(*args) # All cells maynot be initialized
        except TypeError:
            cell.val = None

    for child_id in cell.children:
        evaluate(sheet, get_cell(sheet, child_id), child_id)

    row_id, col_id = extract_row_col_ids(cell_id) 
    children = get_row(sheet, row_id).children + get_col(sheet, col_id).children
    for child in children:
        evaluate(sheet, get_cell(sheet, child), child)


def get_cells_in_aggregate(sheet, agg_id, ctor):
    cell_ids = []
    if ctor == Column:
        pattern = r'^%s[0-9]+$' % agg_id
    else:
        pattern = r'^[a-zA-Z]+%s$' % agg_id[1:]

    for id in sheet.keys():
        if re.search(pattern, id):
            cell_ids.append(id)
    return [id for id in cell_ids]
    


