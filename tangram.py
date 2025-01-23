from piece_generator import game_generator

class TangramSolver:

    def __init__(self):
        self.generated_pieces, self.generated_shape = game_generator()
        self.pieces = [[], *self.generated_pieces]

        self.color_map = {
            -1: (255, 255, 255), # white
            0: (255, 255, 255),  # white
            1: (255, 0, 0),      # red
            2: (255, 165, 0),    # orange
            3: (0, 255, 0),      # green
            4: (0, 0, 255),      # blue
            5: (128, 0, 128),    # purple
            6: (139, 69, 19),    # brown
            7: (255, 192, 203),  # pink
            8: (255, 255, 0),    # yellow
            9: (0, 255, 255),    # cyan
            10: (128, 128, 128), # gray
            11: (0, 128, 0),     # dark green
            12: (255, 140, 0),   # dark orange
            13: (139, 0, 0),     # dark red
            14: (0, 0, 128)      # dark blue
        }

        self.board_size = 17  # Keep max size for array
        self.board = [[-1 for _ in range(17)] for _ in range(17)]
        # Set valid positions to 0
        for x, y in self.generated_shape:
            self.board[x][y] = 0
        
        self.piece_positions = self.gen_piece_positions(self.pieces)

        self.iterations = 0
        self.solutions = []
        self.terminate = False

    def draw_board(self, board):
        symbol_map = {    
            -1: "  ",    
            0: "  ",
            1: "■ ",
            2: "▣ ",
            3: "▤ ",
            4: "▴ ",
            5: "▶ ",
            6: "▱ ",
            7: "▷ ",
            8: "▩ ",
            9: "▰ ",
            10: "▢ ",
            11: "▲ ",
            12: "▭ ",
            13: "▮ ",
            14: "▯ "
        }
    
        for row in board:
            out_row = [symbol_map.get(cell, "?") for cell in row]
            print(" ".join(out_row))

    @staticmethod
    def rotate_piece(piece):
        return [list(row[::-1]) for row in zip(*piece)]

    def get_rotations(self, piece):
        unique_rotations = [piece]
        for _ in range(3):
            piece = self.rotate_piece(piece)
            if piece not in unique_rotations:
                unique_rotations.append(piece)

        return unique_rotations, len(unique_rotations)

    @staticmethod
    def reflect_piece_x(piece):
        return piece[::-1]

    @staticmethod
    def reflect_piece_y(piece):
        return [row[::-1] for row in piece]

    def get_all_positions(self, piece):
        positions, _ = self.get_rotations(piece)
        for pos in positions:
            y_reflect = self.reflect_piece_y(pos)
            x_reflect = self.reflect_piece_x(pos)
            if y_reflect not in positions:
                positions.append(y_reflect)
            if x_reflect not in positions:
                positions.append(x_reflect)
        return positions

    def gen_piece_positions(self, pieces):
        piece_positions = []
        for piece in pieces[1:]:
            piece_positions.append(self.get_all_positions(piece))
        return piece_positions

    @staticmethod
    def legal_islands(self, board):
        # use bfs to find number of distinct islands
        board = [[elem if elem != -1 else "#" for elem in row] for row in board]
        board_height = len(board)
        board_width = len(board[0])
        island_cells = []

        def island_bfs(row, col):
            cell_queue = [(row, col)]

            while cell_queue:
                row, col = cell_queue.pop()
                if board[row][col] != 0:
                    continue
                island_cells.append((row, col))
                board[row][col] = "#"
                for row_offset, col_offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    temp_row = row + row_offset
                    temp_col = col + col_offset
                    if 0 <= temp_row < board_height and 0 <= temp_col < board_width and board[temp_row][
                        temp_col] == 0:
                        cell_queue.append((temp_row, temp_col))

        for row in range(board_height):
            for col in range(board_width):
                if board[row][col] == 0:
                    island_bfs(row, col)
                    island_size = len(island_cells)

                    # islands smaller than 4 are illegal
                    if island_size < 4:
                        return False

                    # only allow square shapes for islands of size 4
                    elif island_size == 4:
                        if not self.check_square(island_cells):
                            return False

                    # islands of size 6,7, and 8 are impossible
                    elif island_size in (6, 7, 8):
                        return False

                    island_cells = []
        return True

    def add_piece(self, board, piece, start_row, start_col, check_islands=True):
        try:
            piece_height = len(piece)
            piece_width = len(piece[0])
            
            # Get first non-zero position to calculate offset
            min_row = piece_height
            min_col = piece_width
            piece_cells = []
            
            for i in range(piece_height):
                for j in range(piece_width):
                    if piece[i][j] != 0:
                        piece_cells.append((i, j))
                        min_row = min(min_row, i)
                        min_col = min(min_col, j)
            
            # Adjust start position based on offset
            start_row -= min_row
            start_col -= min_col
            
            # Validate only non-zero cells with adjusted position
            for p_row, p_col in piece_cells:
                board_row = start_row + p_row
                board_col = start_col + p_col
                
                if (board_row < 0 or board_col < 0 or
                    board_row >= len(board) or
                    board_col >= len(board[0]) or
                    (board_row, board_col) not in self.generated_shape or
                    board[board_row][board_col] != 0):
                    return board, False
            
            # Copy board and place piece
            new_board = [row[:] for row in board]
            for p_row, p_col in piece_cells:
                board_row = start_row + p_row
                board_col = start_col + p_col
                new_board[board_row][board_col] = piece[p_row][p_col]
            
            if check_islands and (not self.legal_islands(new_board)):
                return board, False
                
            return new_board, True
            
        except (IndexError, TypeError):
            return board, False
        
    def get_legal_squares(self, board, piece, check_islands=True):
        legal_moves = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if (row, col) in self.generated_shape:
                    _, legal = self.add_piece(board, piece, row, col, check_islands)
                    if legal:
                        legal_moves.append((row, col))
        return legal_moves
    
    def solve_board(self, board, pieces):
        # Base case: check if board is complete
        empty_exists = False
        for row in range(len(board)):
            for col in range(len(board[0])):
                if (row, col) in self.generated_shape and board[row][col] == 0:
                    empty_exists = True
                    break
        
        if not empty_exists:
            self.solutions = [[row[:] for row in board]]
            return True

        if not pieces:
            return False

        # Try each piece variant
        for position in pieces[0]:
            for row in range(len(board)):
                for col in range(len(board[0])):
                    if (row, col) in self.generated_shape and board[row][col] == 0:
                        new_board, legal = self.add_piece(board, position, row, col)
                        if legal:
                            if self.solve_board(new_board, pieces[1:]):
                                return True
        return False

    def run(self):
        # Initialize solver
        current_board = [[val for val in row] for row in self.board]
        unused_piece_positions = []
        
        # Get positions for unused pieces only
        for piece_idx in self.unused_pieces:
            unused_piece_positions.append(self.piece_positions[piece_idx - 1])
        
        if self.solve_board(current_board, unused_piece_positions):
            self.board = self.solutions[0]
            return True
        return False

    # def solve_board(self, board, pieces):

    #     self.iterations += 1

    #     if self.terminate:
    #         return

    #     # win condition is whole board is covered in pieces
    #     if all([all(row) for row in board]):
    #         self.solutions.append(board)
    #         print(f"Solutions: {len(self.solutions):,}")
    #         print(f"Iterations: {self.iterations:,}\n")
    #         self.draw_board(board)
    #         return board
    #     else:
    #         piece_positions = pieces[0]
    #         for position in piece_positions:
    #             legal_squares = self.get_legal_squares(board, position)
    #             for row, col in legal_squares:
    #                 self.solve_board(self.add_piece(board, position, row, col)[0], pieces[1:])

    # def run(self):
    #     self.solve_board(self.board, self.piece_positions)


if __name__ == "__main__":
    TangramSolver().run()
