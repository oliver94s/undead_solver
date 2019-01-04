import argparse

class Grid(object):

    def __init__(self):
        self.content = None
        self.filled = False

    def set(self, content):
        if content == 'L':
            # self.content = '\\'
            self.content = 'L'
            self.filled = True
        elif content == 'R':
            # self.content = '/'
            self.content = 'R'
            self.filled = True
        else:
            self.content = content

    def get(self):
        return self.content

    def __str__(self):
        return '|%s|' % self.content


class Board(object):

    def __init__(self, board_str):
        self.dim_x, self.dim_y = self.calc_dim(board_str)
        self.g_count, self.v_count, self.z_count = self.calc_monster_count(board_str)
        self.board = []
        self._init_board()
        self.generate_board(board_str)
        self.north_count, self.east_count, self.south_count, self.west_count = self.calc_board_monster_count(board_str)
        print(self.north_count, self.east_count, self.south_count, self.west_count)

    @staticmethod
    def calc_dim(board_str):
        """
        Given a string converts it to dimensions 
        :return: x, y
        """
        dims = []
        for dim in board_str.split(':')[0].split('x'):
            dims.append(int(dim))
        
        return dims[0], dims[1]

    @staticmethod
    def calc_monster_count(board_str):
        board_split = board_str.split(':')[1].split(',')
        ghost_count = int(board_split[0])
        vampire_count = int(board_split[1])
        zombie_count = int(board_split[2])

        return ghost_count, vampire_count, zombie_count

    def calc_board_monster_count(self, board_str):
        board_split = board_str.split(':')[1].split(',')

        monster_count_start = 4
        monster_count = []

        for mon_count in board_split[monster_count_start:]:
            monster_count.append(int(mon_count))

        top_row = monster_count[: self.dim_x]
        right_col = monster_count[self.dim_x: self.dim_x + self.dim_y]

        bottom_row = monster_count[self.dim_x + self.dim_y: (self.dim_x * 2) + self.dim_y]
        bottom_row.reverse()
        left_col = monster_count[(self.dim_x * 2) + self.dim_y: (self.dim_x * 2) + (self.dim_y * 2)]
        left_col.reverse()

        return top_row, right_col, bottom_row, left_col

    def _init_board(self):
        for x in range(0, self.dim_x):
            self.board.append([])
            for y in range(0, self.dim_y):
                empty_grid = Grid()
                self.board[x].append(empty_grid)
        

    def generate_board(self, board_str):
        board_split = board_str.split(':')[1].split(',')
        board_layout = board_split[3]

        x = 0
        y = 0


        for space in board_layout:
            if space == "L" or space == "R":
                self.board[x][y].set(space)
                if y < self.dim_y - 1:
                    y += 1
                else:
                    y = 0
                    x += 1
            else:
                for count in range(0, (ord(space) - 96)):
                    self.board[x][y].set(' ')
                    if y < self.dim_y - 1:
                        y += 1
                    else:
                        y = 0
                        x += 1    

    def print_board(self):
        x_str = []
        y_str = []
        for x in range(0, self.dim_x):
            for y in range(0, self.dim_y):
                y_str.append(str(self.board[x][y]))
            print(''.join(y_str))
            y_str = []


class Walker(object):
    def __init__(self):
        pass

    def walk(self, board, row, col, direction, path=None):
        if path is None:
            path = []

        path.append((row, col))

        if board.board[row][col].get() == 'L':
            direction = self.left_bounce(direction)
        elif board.board[row][col].get() == 'R':
            direction = self.right_bounce(direction)

        if direction == 'north':
            # The top left of the array is considered to be 0. 0
            # as we go down we are incrementing col
            row -= 1
        elif direction == 'east':
            col += 1
        elif direction == 'south':
            row += 1
        elif direction == 'west':
            col -= 1

        if (row >= 0 and row < board.dim_x) and (col >= 0 and col < board.dim_y):
            self.walk(board, row, col, direction, path)

        return path

    def solve_zero_case(self, board):
        for col_idx in range(0, board.dim_y):
            monster_count = board.north_count[col_idx]
            
            if monster_count == 0:
                path_traversed = self.walk(board, 0, col_idx, 'south')

                self._set_zero_case(board, path_traversed)

            monster_count = board.south_count[col_idx]
            
            if monster_count == 0:
                path_traversed = self.walk(board, board.dim_x - 1, col_idx, 'north')

                self._set_zero_case(board, path_traversed)

        for row_idx in range(0, board.dim_x):
            monster_count = board.west_count[row_idx]
            
            if monster_count == 0:
                path_traversed = self.walk(board, row_idx, 0, 'east')

                self._set_zero_case(board, path_traversed)

            monster_count = board.east_count[row_idx]
            
            if monster_count == 0:
                path_traversed = self.walk(board, row_idx, board.dim_y - 1, 'west')

                self._set_zero_case(board, path_traversed)

    @staticmethod
    def _set_zero_case(board, path_traversed):
        after_bounce = False

        for coord in path_traversed:
            row, col = coord

            if board.board[row][col].get() == 'R' or board.board[row][col].get() == 'L':
                after_bounce = True
            elif board.board[row][col].get() == ' ' and not after_bounce:
                board.board[row][col].set('G')
            elif board.board[row][col].get() == ' ' and after_bounce:
                board.board[row][col].set('V')

    @staticmethod
    def get_path_monster_count(board, path_traversed):
        after_bounce = False
        monster_count = 0

        for coord in path_traversed:
            row, col = coord

            if board.board[row][col].get() == 'R' or board.board[row][col].get() == 'L':
                after_bounce = True

            elif board.board[row][col].get() == 'G':
                if after_bounce:
                    monster_count += 1

            elif board.board[row][col].get() == 'V':
                if not after_bounce:
                    monster_count += 1

        return monster_count

    def after_zero_solve(self, board):
        for col_idx in range(0, board.dim_y):
            monster_count = board.north_count[col_idx]
            
            if monster_count > 0:
                path_traversed = self.walk(board, 0, col_idx, 'south')

                path_monster_count = self.get_path_monster_count(board, path_traversed)

                board.north_count[col_idx] -= path_monster_count

                if board.north_count[col_idx] < 0:
                    raise ValueError("Monster Counts cannot be lower than 0")

                if board.north_count[col_idx] == 0:
                    self._set_zero_case(board, path_traversed)

            monster_count = board.south_count[col_idx]

            if monster_count > 0:
                path_traversed = self.walk(board, board.dim_x - 1, col_idx, 'north')

                path_monster_count = self.get_path_monster_count(board, path_traversed)

                board.south_count[col_idx] -= path_monster_count

                if board.south_count[col_idx] < 0:
                    raise ValueError("Monster Counts cannot be lower than 0")

                if board.south_count[col_idx] == 0:
                    self._set_zero_case(board, path_traversed)

        for row_idx in range(0, board.dim_x):
            monster_count = board.west_count[row_idx]

            if monster_count > 0:
                path_traversed = self.walk(board, row_idx, 0, 'east')

                path_monster_count = self.get_path_monster_count(board, path_traversed)

                board.west_count[row_idx] -= path_monster_count

                if board.west_count[row_idx] < 0:
                    raise ValueError("Monster Counts cannot be lower than 0")

                if board.west_count[row_idx] == 0:
                    self._set_zero_case(board, path_traversed)

            monster_count = board.east_count[row_idx]

            if monster_count > 0:
                path_traversed = self.walk(board, row_idx, board.dim_y - 1, 'west')

                path_monster_count = self.get_path_monster_count(board, path_traversed)

                board.east_count[row_idx] -= path_monster_count

                if board.east_count[row_idx] < 0:
                    raise ValueError("Monster Counts cannot be lower than 0")

                if board.east_count[row_idx] == 0:
                    self._set_zero_case(board, path_traversed)

    def solve(self, board):
        self.solve_zero_case(board)
        self.after_zero_solve(board)

    @staticmethod
    def right_bounce(direction):
        if direction == 'north':
            return 'east'
        elif direction == 'east':
            return 'north'
        elif direction == 'south':
            return 'west'
        elif direction == 'west':
            return 'south'
        else:
            raise ValueError('%s not a valid direction' % direction) 

    @staticmethod
    def left_bounce(direction):
        if direction == 'north':
            return 'west'
        elif direction == 'west':
            return 'north'
        elif direction == 'south':
            return 'east'
        elif direction == 'east':
            return 'south'
        else:
            raise ValueError('%s not a valid direction' % direction) 


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("Given a link it will attempt to solve the simon undead puzzle")

    arg_parser.add_argument('undead_link', help='Link to the undead puzzle')

    args, unknown = arg_parser.parse_known_args()


    # test_link = "https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/undead.html#4x4:0,8,3,aRbLcLcRbL,3,0,4,3,3,3,3,0,0,4,4,0,0,0,0,1"
    test_link = args.undead_link
    board_txt = test_link.split('#')[-1]
    board = Board(board_txt)
    # print('printing board out')
    # board.print_board()

    walkman = Walker()
    # row = 0
    # col = 2
    # print(walkman.walk(board, row, col, 'south'))
    walkman.solve(board)
    board.print_board()