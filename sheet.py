#!/usr/bin/env python3
import inspect
import pdb

class Cell:
    def __init__(self, val=None, expr=None ):
        self.val = val
        self.expr = expr
        self.children = []
        self.parents = []
    
    def __repr__(self):
        return "*".join([str(x) for x in (self.val, self.expr, self.children, self.parents)])

def create_sheet():
    return {}

def get_cell(sheet, cell_id):
    cell = sheet.get(cell_id) 
    if not cell:
        cell = Cell()
        sheet[cell_id] = cell
    return cell


def put(sheet, cell_id, value):
    cell = get_cell(sheet, cell_id)

    for parent_id in cell.parents:
        parent_cell = get_cell(sheet, parent_id)
        parent_cell.children.remove(cell_id)
    # old parents' children list is now ok.

    if callable(value):
        
        new_parents = list(inspect.signature(value).parameters)

        cell.parents = new_parents

        for parent_id in new_parents:
            parent_cell = get_cell(sheet, parent_id)
            parent_cell.children.append(cell_id)

    else:
        cell.parents = []

    cell.expr = value
    evaluate(sheet, cell)
    
    return cell

def evaluate(sheet, cell):
    if not callable(cell.expr):
        cell.val = cell.expr
    else:
        args = [get_cell(sheet, parent_id).val for parent_id in cell.parents]
        cell.val = cell.expr(*args)
    for child_id in cell.children:
        evaluate(sheet, get_cell(sheet, child_id))

            

def foo(a, b):
    return a+b

def id(c):
    return c

def bar(a):
    return a+1

def baz(b):
    return b+1

if __name__ == '__main__':

    s = create_sheet()


    put(s, 'a', 1)
    put(s, 'b', 2)
    put(s, 'c', foo)

    put(s, 'a', 5)

    put(s, 'd', id)

    put(s, 'b', 6)
    
    pdb.set_trace()
    # b a c d
    put(s, 'c', bar)
    
    put(s, 'a', baz)

    print("hello da")


