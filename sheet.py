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

class Row:
    def __init__(self):
        self.expr = None
        self.children = []
        self.parents = []

    def __repr__(self):
        return "*".join([str(x) for x in (self.expr, self.children, self.parents)])

class Column:
    def __init__(self):
        self.expr = None
        self.children = []
        self.parents = []

    def __repr__(self):
        return "*".join([str(x) for x in (self.expr, self.children, self.parents)])

def get_row_col(id):
    match = re.search(r'^([a-zA-Z]+)([0-9]+)$', id)
    return ('_'+match.group(2), match.group(1))

def create_sheet():
    return {}

def get_cell(sheet, cell_id):
    cell = sheet.get(cell_id) 
    if not cell:
        cell = Cell()
        sheet[cell_id] = cell
    return cell

def get_row(sheet, id):
    row = sheet.get(id) 
    if not row:
        row = Row()
        sheet[id] = row
    return row

def get_col(sheet, id):
    col = sheet.get(id) 
    if not col:
        col = Column()
        sheet[id] = col
    return col

def get_type(id):
    if re.search(r'^[a-zA-Z]+$', id):
        return 'Column'
    elif re.search(r'^_[0-9]+$', id):
        return 'Row'
    elif re.search(r'^([a-zA-Z]+)([0-9]+)$', id):
        return 'Cell'
    else:
        return None



def put(sheet, place, value):
    try:
        # pdb.set_trace()
        cell = get_cell(sheet, place)

        row_id, col_id = get_row_col(place) # Raises exception

        for parent_id in cell.parents:
            t = get_type(parent_id)
            if t == 'Cell':
                parent = get_cell(sheet, parent_id)
            elif t == 'Row':
                parent = get_row(sheet, parent_id)
            elif t == 'Column':
                parent = get_col(sheet, parent_id)
            else:
                raise Exception
            parent.children.remove(place)
                
        # old parents' children list is now ok.

        if callable(value):
            
            new_parents = list(inspect.signature(value).parameters)

            cell.parents = new_parents

            for parent_id in new_parents:
                t = get_type(parent_id)
                if t == 'Cell':
                    parent = get_cell(sheet, parent_id)
                elif t == 'Row':
                    parent = get_row(sheet, parent_id)
                elif t == 'Column':
                    parent = get_col(sheet, parent_id)
                else:
                    raise Exception
                parent.children.append(place)


        else:
            cell.parents = []

        cell.expr = value
        evaluate(sheet, cell, place) # evaluate works only on individual cells
        # Hence place must be a cell_id.

        return cell
    except:
        # print(place + ' is not a valid cell.', file=sys.stderr)
        print('oops')
        return None

def get(sheet, cell_id):
    return get_cell(sheet, cell_id).val

def evaluate(sheet, cell, cell_id):
    if not callable(cell.expr):
        cell.val = cell.expr
    else:
        # args = [get_cell(sheet, parent_id).val for parent_id in cell.parents]
        # cell.val = cell.expr(*args)
        args = []
        for parent_id in cell.parents:
            t = get_type(parent_id)
            if t == "Cell":
                args.append(get_cell(sheet, parent_id).val)
            elif t == "Row":
                cells_in_row = get_cells_in_row(sheet, parent_id)
                cells = [cell for (cell, id) in cells_in_row]
                args.append(cells)
            elif t == "Column":
                cells_in_col = get_cells_in_col(sheet, parent_id)
                cells = [cell for (cell, id) in cells_in_col]
                args.append(cells)
            else:
                raise Exception

        try:
            cell.val = cell.expr(*args) # All cells maynot be initialized
        except TypeError:
            cell.val = None



    for child_id in cell.children:
        evaluate(sheet, get_cell(sheet, child_id), child_id)


    row_id, col_id = get_row_col(cell_id) 
    children = get_row(sheet, row_id).children + get_col(sheet, col_id).children
    for child in children:
        evaluate(sheet, get_cell(sheet, child), child)


def get_cells_in_col(sheet, col_id):
    cell_ids = []
    pattern = r'^%s[0-9]+$' % col_id
    for id in sheet.keys():
        if re.search(pattern, id):
            cell_ids.append(id)
    return [(get_cell(sheet, id).val, id) for id in cell_ids]

def get_cells_in_row(sheet, row_id):
    cell_ids = []
    pattern = r'^[a-zA-Z]+%s$' % row_id[1:]
    for id in sheet.keys():
        if re.search(pattern, id):
            cell_ids.append(id)
    return [(get_cell(sheet, id).val, id) for id in cell_ids]



if __name__ == '__main__':

    s = create_sheet()

    # pdb.set_trace()

    # put(s, 'a1', 10)
    # put(s, 'a2', 20)
    # put(s, 'b1', lambda a: sum(a))

    put(s, 'a10', 3)
    put(s, 'b10', 3)
    put(s, 'c10', 3)
    put(s, 'b2', lambda _10: sum(_10))

    # put(s, 'a1', 1)
    # put(s, 'a2', 2)
    # put(s, 'a3', 3)
    # put(s, 'a4', 4)
    # put(s, 'b1', lambda a: sum(a)) # This now works. column aggregation works.
# 
# put(s, 'a10', 100)
# put(s, 'b10', 200)
# put(s, 'c10', 300)
# put(s, 'd10', 400)
# put(s, 'b2', lambda _10: sum(_10))
# 
# 
