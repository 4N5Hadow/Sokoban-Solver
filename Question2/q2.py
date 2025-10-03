"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T + 1
        self.N = len(grid)
        self.M = len(grid[0])
        
        self.goals = []
        self.boxes = []
        self.walls = []
        self.player_start = None
        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start, self.walls
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for x in range(self.N):
            for y in range(self.M):
                if self.grid[x][y] == 'P':
                    self.player_start = (x, y)
                elif self.grid[x][y] == 'B':
                    self.boxes.append((x, y))
                elif self.grid[x][y] == 'G':
                    self.goals.append((x, y))
                elif self.grid[x][y] == '#':
                    self.walls.append((x,y))

    # ---------------- self.variable Encoding ----------------
    def var_goal(self,x,y):
        assert x < self.N and y < self.M
        assert x >= 0 and y >= 0
        return x*self.M + y + 1
	
    def var_player(self, x, y, t):
        """
        self.variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        assert x < self.N and y < self.M
        assert x >= 0 and y >= 0
        assert t>=0
        assert t < self.T
        return (t+1)*self.M*self.N + x*self.M + y + 1
    
    def var_move(self, num, t): # MoveURDL - 1234, PushURDL - 5678, Stay - 9
        assert num >= 1 and num <= 9
        assert t >= 0 and t < self.T
        return (self.T+1)*self.M*self.N + 9*t + num

    def var_box(self, b, x, y, t):
        """
        self.variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        assert b >= 1 and b <= self.num_boxes
        assert x < self.N and y < self.M
        assert x >= 0 and y >= 0
        assert t >= 0 and t < self.T
        return (1+self.T)*self.N*self.M + 9*self.T + self.num_boxes*t*self.N*self.M + (b-1)*self.N*self.M + x*self.M + y + 1
    
    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        cnf_list = []
        # TODO: Add constraints for:
        # 1. Initial conditions
        
        cnf_list.append([self.var_player(self.player_start[0], self.player_start[1], 0)])
        
        for box in range(self.num_boxes):
            cnf_list.append([self.var_box(box+1,self.boxes[box][0],self.boxes[box][1],0)])
            
        for x in range(self.N):
            for y in range(self.M):
                if (x,y) in self.goals:
                      cnf_list.append([self.var_goal(x,y)])
                else:
                    cnf_list.append([-self.var_goal(x,y)])
            
        for wall in range(len(self.walls)):
            for t in range(self.T):
                cnf_list.append([-self.var_player(self.walls[wall][0], self.walls[wall][1], t)])
                
                for box in range(self.num_boxes):
                    cnf_list.append([-self.var_box(box+1, self.walls[wall][0], self.walls[wall][1], t)])

        cnf_list.append([self.var_move(9,0)])  # Stay condition at t=0
                    
        # 2. Player movement
        for x in range(self.N):
            for y in range(self.M):
              	for move in range(4): # order -> U, R, D, L
                    for t in range(1,self.T):
                        for box in range(self.num_boxes):
                                cnf_list.append([-self.var_move(move+1,t),-self.var_box(box+1,x,y,t-1),self.var_box(box+1,x,y,t)])
                        new_x = x
                        new_y = y
                        if move == 0 : new_x-=1
                        elif move == 1: new_y+=1
                        elif move == 2: new_x+=1
                        else: new_y-=1
                        if new_x < 0 or new_y < 0 or new_x >= self.N or new_y >= self.M:
                            # print("Invalid move out of bounds")
                            cnf_list.append([-self.var_move(move+1,t),-self.var_player(x,y,t-1)])
                        else:
                            cnf_list.append([-self.var_move(move+1,t),-self.var_player(x,y,t-1),self.var_player(new_x,new_y,t)])
                    
        # 3. Box movement (push rules)  
        for x in range(self.N):
            for y in range(self.M):
                for t in range(1,self.T):
                    for move in range(4): # order -> U, R, D, L
                        new_x = x
                        new_y = y
                        if move == 0 : new_x-=1
                        elif move == 1: new_y+=1
                        elif move == 2: new_x+=1
                        else: new_y-=1
                        box_x = new_x
                        box_y = new_y
                        if move == 0 : box_x-=1
                        elif move == 1: box_y+=1
                        elif move == 2: box_x+=1
                        else: box_y-=1
                        if new_x < 0 or new_y < 0 or new_x >= self.N or new_y >= self.M or box_x < 0 or box_y < 0 or box_x >= self.N or box_y >= self.M:
                            # print("Going out of bounds")
                            cnf_list.append([-self.var_move(move+5,t),-self.var_player(x,y,t-1)])
                        else:
                            clause = [-self.var_move(move+5,t),-self.var_player(x,y,t-1)]
                            for box in range(self.num_boxes):
                                clause.append(self.var_box(box+1,new_x,new_y,t-1))
                                cnf_list.append([-self.var_move(move+5,t),-self.var_player(x,y,t-1),-self.var_box(box+1,new_x,new_y,t-1),self.var_player(new_x,new_y,t)])
                                cnf_list.append([-self.var_move(move+5,t),-self.var_player(x,y,t-1),-self.var_box(box+1,new_x,new_y,t-1),self.var_box(box+1,box_x,box_y,t)])
                                for prime_x in range(self.N):
                                    for prime_y in range(self.M):
                                        if (prime_x, prime_y) != (new_x, new_y):
                                            cnf_list.append([-self.var_move(move+5,t),-self.var_player(x,y,t-1),-self.var_box(box+1,prime_x,prime_y,t-1),self.var_box(box+1,prime_x,prime_y,t)])
                            cnf_list.append(clause)

        # 4. Non-overlap constraints
        for x in range(self.N):
            for y in range(self.M):
                for box in range(self.num_boxes):
                    for t in range(self.T):
                        cnf_list.append([-self.var_player(x,y,t), -self.var_box(box+1, x, y, t)])
                        for boxd in range(box+1, self.num_boxes):
                            cnf_list.append([-self.var_box(box+1, x, y, t), -self.var_box(boxd+1, x, y, t)])
        
        # 5. Goal conditions
        for x in range(self.N):
            for y in range(self.M):
              	for box in range(self.num_boxes):
                    cnf_list.append([-self.var_box(box+1, x, y, self.T-1), self.var_goal(x, y)])
            
        
        # 6. Other conditions
        # Exactly one move at a time

        for t in range(self.T):
            clause = []
            for i in range(1,10):
                clause.append(self.var_move(i,t))
                for j in range(i+1,10):
                    cnf_list.append([-self.var_move(i,t),-self.var_move(j,t)])
            cnf_list.append(clause)
        
        # 7. Uniqueness per time conditions
        for t in range(self.T):
            clause = [self.var_player(x,y,t) for x in range(self.N) for y in range(self.M)]
            cnf_list.append(clause)
            
            for n in range(len(clause)):
                for nd in range(n+1, len(clause)):
                    cnf_list.append([-clause[n], -clause[nd]])
                    
            for box in range(self.num_boxes):
                bclause = [self.var_box(box+1, x, y, t) for x in range(self.N) for y in range(self.M)]
                cnf_list.append(bclause)
                
                for n in range(len(bclause)):
                    for nd in range(n+1, len(bclause)):
                        cnf_list.append([-bclause[n], -bclause[nd]])
        #8. Stay conditions
        for t in range(1, self.T):
            for x in range(self.N):
                for y in range(self.M):
                    for box in range(self.num_boxes):
                        cnf_list.append([-self.var_move(9,t),-self.var_box(box+1,x,y,t-1),self.var_box(box+1,x,y,t)])
                    cnf_list.append([-self.var_move(9,t),-self.var_player(x,y,t-1),self.var_player(x,y,t)])

        return cnf_list
        


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    # TODO: Map player positions at each timestep to movement directions
    moves = []
    for index in range((T+1)*N*M, (T+1)*N*M + 9*T):
      	if (model[index]>0): 
            match ((index - (T+1)*N*M)%9):
                case 0 : moves.append('U')
                case 1 : moves.append('R')
                case 2 : moves.append('D')
                case 3 : moves.append('L')
                case 4: moves.append('U')
                case 5: moves.append('R')
                case 6: moves.append('D')
                case 7: moves.append('L')
                # case 8: moves.append('S')  
    # print(moves)
    return moves


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()
    # print(cnf)

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1
        return decode(model, encoder)


"""
Goal Position - N*M (1 - N*M)
Player position - N*M*t (N*M + 1 - (T+1)*N*M)
Moves - 9*t ((T+1)*N*M + 1 - (T+1)*N*M + 9*T)
Box Position - B*N*M*t ((T+1)*N*M + 9*T + 1 - ((B+1)*T + 1)*N*M + 9*T)
"""