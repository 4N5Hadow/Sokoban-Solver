"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    n = len(grid)
    sub_n = int(n**0.5)

    def prop(row: int, col: int, num: int) -> int:
        return (row * n + col) * n + num
    
    cnf = CNF()

    """
    Conditions -
    Given values
    Atleast one number in each cell
    Atmost one number in each cell
    Each number appears in each row
    Each number appears in each column
    Each number appears in each subgrid
    """

    # Encoding each cell conditions
    for r in range(n):
        for c in range(n):
            clause = [prop(r, c, num) for num in range(1, n + 1)]
            cnf.append(clause)

            for i in range(n):
                for j in range(i + 1, n):
                    cnf.append([-clause[i], -clause[j]])

    # Row conditions
    for r in range(n):
        for num in range(1, n + 1):
            clause = [prop(r, c, num) for c in range(n)]
            cnf.append(clause)

    # Column conditions
    for c in range(n):
        for num in range(1, n + 1):
            clause = [prop(r, c, num) for r in range(n)]
            cnf.append(clause)

    # Subgrid conditions
    for br in range(0, n, sub_n):
        for bc in range(0, n, sub_n):
            for num in range(1, n + 1):
                clause = [prop(r, c, num) 
                          for r in range(br, br + sub_n) 
                          for c in range(bc, bc + sub_n)]
                cnf.append(clause)

    # Initial conditions
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                cnf.append([prop(r, c, grid[r][c])])

    with Solver(name='glucose3', bootstrap_with=cnf.clauses) as solver:
        solution = grid

        if solver.solve():
            model = solver.get_model()
        
            for r in range(n):
                for c in range(n):
                    for num in range(1, n + 1):
                        if model[prop(r, c, num) - 1] > 0: # proposition is 1 indexed whereas model array is 0 indexed
                            solution[r][c] = num
                            break

        return solution