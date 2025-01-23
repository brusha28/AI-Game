from tangram import TangramSolver
from setup import *
import sys
import time

class TangramGame(TangramSolver):

    def __init__(self):

        super().__init__()

        self.solution = []

        self.board_buffer = [[-1 for _ in range(17)] for _ in range(17)]

        self.unused_pieces = [num for num in range(1, len(self.pieces))]

        self.current_piece = self.pieces[1]

        self.piece_idx_pointer = 0

        self.game_state = "start"

        self.start_time = time.time()
        self.pieces_placed = 0
        self.pieces_removed = 0

        self.draw_buffer_event = pg.USEREVENT + 1
        pg.time.set_timer(self.draw_buffer_event, 100)

    #####################################################################
    # Methods for drawing to the screen
    #####################################################################
        
    def draw_dyanmic_board(self):
        def find_edges(shape):
            edges = set()
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for x, y in shape:
                for dx, dy in directions:
                    if (x + dx, y + dy) not in shape:
                        edges.add((x, y))
                        break
            return edges

        edges = find_edges(self.generated_shape)
        for x, y in edges:
            if (x - 1, y) not in self.generated_shape:
                pg.draw.line(SCREEN, (0, 0, 0), 
                        (BOARD_X_OFFSET + y * SQUARE_WIDTH, BOARD_Y_OFFSET + x * SQUARE_HEIGHT), 
                        (BOARD_X_OFFSET + (y + 1) * SQUARE_WIDTH, BOARD_Y_OFFSET + x * SQUARE_HEIGHT), 
                        LINE_THICKNESS)
            if (x + 1, y) not in self.generated_shape:
                pg.draw.line(SCREEN, (0, 0, 0), 
                        (BOARD_X_OFFSET + y * SQUARE_WIDTH, BOARD_Y_OFFSET + (x + 1) * SQUARE_HEIGHT), 
                        (BOARD_X_OFFSET + (y + 1) * SQUARE_WIDTH, BOARD_Y_OFFSET + (x + 1) * SQUARE_HEIGHT), 
                        LINE_THICKNESS)
            if (x, y - 1) not in self.generated_shape:
                pg.draw.line(SCREEN, (0, 0, 0), 
                        (BOARD_X_OFFSET + y * SQUARE_WIDTH, BOARD_Y_OFFSET + x * SQUARE_HEIGHT), 
                        (BOARD_X_OFFSET + y * SQUARE_WIDTH, BOARD_Y_OFFSET + (x + 1) * SQUARE_HEIGHT), 
                        LINE_THICKNESS)
            if (x, y + 1) not in self.generated_shape:
                pg.draw.line(SCREEN, (0, 0, 0), 
                        (BOARD_X_OFFSET + (y + 1) * SQUARE_WIDTH, BOARD_Y_OFFSET + x * SQUARE_HEIGHT), 
                        (BOARD_X_OFFSET + (y + 1) * SQUARE_WIDTH, BOARD_Y_OFFSET + (x + 1) * SQUARE_HEIGHT), 
                        LINE_THICKNESS)

    @staticmethod
    def draw_title():
        title_word = TITLE_FONT.render("Block Puzzle", True, (0, 0, 0))
        title_rect = title_word.get_rect()
        title_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 15)
        SCREEN.blit(title_word, title_rect)

    @staticmethod 
    def draw_piece(piece_coords, board, x_offset, y_offset):
        for row, col in piece_coords:
            # Only draw pieces in valid positions
            if board[row][col] > 0:
                pg.draw.rect(SCREEN, COLOR_MAP[board[row][col]], [SQUARE_WIDTH * col + x_offset,
                                                            SQUARE_HEIGHT * row + y_offset, 
                                                            SQUARE_WIDTH,
                                                            SQUARE_HEIGHT])

    def draw_buffer(self, check = False):
        # Initialize buffer with invalid spaces
        self.board_buffer = [[-1 for _ in range(17)] for _ in range(17)]
        for x, y in self.generated_shape:
            self.board_buffer[x][y] = 0
                
        # Get mouse position and convert to grid
        mouse_x, mouse_y = pg.mouse.get_pos()
        row = (mouse_y - BOARD_Y_OFFSET) // SQUARE_HEIGHT
        col = (mouse_x - BOARD_X_OFFSET) // SQUARE_WIDTH
        if check:
            print(row, col)
        
        # Ensure the mouse position is within the bounds of the current piece
        piece_height = len(self.current_piece)
        piece_width = len(self.current_piece[0])
        row = max(0, min(row, 16 - piece_height + 1))
        col = max(0, min(col, 16 - piece_width + 1))
        
        # Show piece preview if mouse in valid position
        _, legal = self.add_piece(self.board, self.current_piece, row, col, False)
        if legal:
            # Add piece preview to buffer
            for p_row in range(piece_height):
                for p_col in range(piece_width):
                    if self.current_piece[p_row][p_col] != 0:
                        board_row = row + p_row
                        board_col = col + p_col
                        if (board_row, board_col) in self.generated_shape:
                            self.board_buffer[board_row][board_col] = self.current_piece[p_row][p_col]
        
        # Draw buffer to screen
        self.draw_board_pieces(self.board_buffer, BOARD_X_OFFSET, BOARD_Y_OFFSET)

    def draw_board_pieces(self, board, x_offset, y_offset):
        piece_positions = self.get_piece_positions(board, len(self.pieces))
        for piece_num, coords in piece_positions.items():
            for row, col in coords:
                pg.draw.rect(SCREEN, self.color_map.get(piece_num, (0,0,0)), 
                            [SQUARE_WIDTH * col + x_offset,
                            SQUARE_HEIGHT * row + y_offset, 
                            SQUARE_WIDTH,
                            SQUARE_HEIGHT])

    @staticmethod
    def draw_fail_state():
        SCREEN.blit(pg.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        num_iterations_text = NUM_ITERATIONS_FONT.render(f"No Solutions Found!", True, (0, 0, 0))
        num_iterations_rect = num_iterations_text.get_rect()
        num_iterations_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        SCREEN.blit(num_iterations_text, num_iterations_rect)
        pg.display.update()

    def draw_start_state(self):        
        # Load the instructions image
        instructions_image = pg.image.load('assets/Block_Puzzle_Instructions.png')
        
        # Get the original dimensions of the image
        image_width, image_height = instructions_image.get_size()
        
        # Calculate the scaling factor to maintain aspect ratio
        scale_factor = min(SCREEN_WIDTH / image_width, SCREEN_HEIGHT / image_height)
        
        # Calculate the new dimensions
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)
        
        # Scale the image to fit the screen while maintaining aspect ratio
        instructions_image = pg.transform.scale(instructions_image, (new_width, new_height))
        
        # Calculate the position to center the image on the screen
        x_pos = (SCREEN_WIDTH - new_width) // 2
        y_pos = (SCREEN_HEIGHT - new_height) // 2
        
        # Blit the image onto the screen
        SCREEN.blit(instructions_image, (x_pos, y_pos))

        pg.display.update()

    def draw_text(self):
        if self.unused_pieces:
            current_piece_text = NUM_ITERATIONS_FONT.render("Current Piece: ", True, (0, 0, 0))
            current_piece_rect = current_piece_text.get_rect()
            current_piece_rect.center = (SCREEN_WIDTH / 2.5, SCREEN_HEIGHT / 1.15)
            SCREEN.blit(current_piece_text, current_piece_rect)

        # Congratulations if solved
        else:
            num_iterations_text = NUM_ITERATIONS_FONT.render(f"Solved! Thanks for playing!", True,
                                                             (0, 0, 0))
            num_iterations_rect = num_iterations_text.get_rect()
            num_iterations_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.15)
            SCREEN.blit(num_iterations_text, num_iterations_rect)

    #####################################################################
    # Methods that access or modify the board state
    #####################################################################
    @staticmethod
    def get_piece_positions(board, num_pieces):
        piece_loc_dict = {num: [] for num in range(1, num_pieces)}
        for i, row in enumerate(board):
            for j, val in enumerate(row):
                if val > 0:  # Skip -1 and 0
                    piece_loc_dict[val].append((i, j))
        return piece_loc_dict

    @staticmethod
    def clear_piece(piece_val, board):
        # Create copy to avoid modifying during iteration
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == piece_val:
                    board[i][j] = 0  # Reset to empty

    def add_piece_left_click(self, row, col):
        # Validate we have pieces to place
        if not self.unused_pieces or self.piece_idx_pointer >= len(self.unused_pieces):
            return
            
        board = self.board
        new_board, legal = self.add_piece(board, self.current_piece, row, col, False)

        if legal:
            self.board = new_board
            self.pieces_placed += 1
            
            # Safely remove piece from unused list
            if self.piece_idx_pointer < len(self.unused_pieces):
                self.unused_pieces.remove(self.unused_pieces[self.piece_idx_pointer])
                
            # Update current piece
            if self.unused_pieces:
                self.current_piece = self.pieces[self.unused_pieces[0]]
                self.piece_idx_pointer = 0
            else:
                self.current_piece = [[]]
                self.piece_idx_pointer = 0

    def remove_piece_right_click(self, row, col):
        if (row, col) not in self.generated_shape:
            return
            
        board = self.board
        val = board[row][col]
        if val > 0:  # Only remove valid pieces
            # Add piece back to unused list if not already there
            if val not in self.unused_pieces:
                self.unused_pieces.append(val)
                self.unused_pieces.sort()  # Keep pieces in order
            
            # Clear piece from board
            self.clear_piece(val, board)
            self.pieces_removed += 1
            
            # Update current piece
            if self.unused_pieces:
                self.current_piece = self.pieces[self.unused_pieces[0]]
                self.piece_idx_pointer = 0
            else:
                self.current_piece = [[]]

    @staticmethod
    def check_square(points):
        x_vals = [tup[0] for tup in points]
        y_vals = [tup[1] for tup in points]
        if (max(x_vals) - min(x_vals) == 1) and (max(y_vals) - min(y_vals) == 1):
            return True
        else:
            return False

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

    def get_piece_variants(self, piece):
        """
        Generate all possible orientations of a piece (rotations and flips).
        Returns list of piece matrices.
        """
        variants = []
        current = [row[:] for row in piece]  # Deep copy

        # Generate 4 rotations
        for _ in range(4):
            # Add current rotation
            variants.append([row[:] for row in current])
            
            # Add flipped version
            flipped = [row[::-1] for row in current]
            variants.append([row[:] for row in flipped])
            
            # Rotate 90 degrees for next iteration
            # Rotate by transposing and reversing rows
            current = list(zip(*current[::-1]))
            current = [[cell for cell in row] for row in current]
        
        # Remove duplicates by converting to tuples for comparison
        unique_variants = []
        seen = set()
        
        for variant in variants:
            variant_tuple = tuple(tuple(row) for row in variant)
            if variant_tuple not in seen:
                seen.add(variant_tuple)
                unique_variants.append(variant)
        
        return unique_variants

    def solve_board_with_existing(self, board, pieces):
        # Base case: check if board is complete
        if not pieces:
            empty_exists = False
            for row in range(len(board)):
                for col in range(len(board[0])):
                    if (row, col) in self.generated_shape and board[row][col] == 0:
                        empty_exists = True
                        break
            if not empty_exists:
                self.solutions.append([row[:] for row in board])
                return True
            return False

        current_piece = pieces[0]
        remaining_pieces = pieces[1:]
        variants = self.get_piece_variants(current_piece)
        
        print(f"\nTrying {len(pieces)} pieces")
        for variant_idx, variant in enumerate(variants):
            print(f"\nVariant {variant_idx + 1}:")
            for row in variant:
                print("".join(['■' if cell else ' ' for cell in row]))
            
            # Try all valid board positions
            for row in range(len(board)):
                for col in range(len(board[0])):
                    # Check if any valid position exists at this location
                    valid_pos = False
                    for p_row in range(len(variant)):
                        for p_col in range(len(variant[0])):
                            check_row = row + p_row
                            check_col = col + p_col
                            if (check_row, check_col) in self.generated_shape:
                                valid_pos = True
                                break
                        if valid_pos:
                            break
                    
                    if valid_pos:
                        new_board, legal = self.add_piece(board, variant, row, col, False)
                        if legal:
                            print(f"Legal move found at ({row}, {col})")
                            if self.solve_board_with_existing(new_board, remaining_pieces):
                                return True
                            else:
                                print(f"Invalid move at ({row}, {col})")
        return False

    def display_solution(self):
        print("\n=== Starting Solver ===")
        self.solutions = []
        self.terminate = False
        current_board = [[val for val in row] for row in self.board]
        unused_pieces = [self.pieces[i] for i in self.unused_pieces]
        
        if self.solve_board_with_existing(current_board, unused_pieces):
            print("\nSolution found!")
            self.board = self.solutions[0]
            self.unused_pieces = []
            self.current_piece = [[]]
            self.piece_idx_pointer = 0
        else:
            print("\nNo solution found.")
            self.game_state = "failure"

    def display_hint(self):
        elapsed_time = time.time() - self.start_time
        print(f"Game has been open for {elapsed_time:.2f} seconds.")
        print(f"Pieces placed: {self.pieces_placed}")
        print(f"Pieces removed: {self.pieces_removed}")

    #####################################################################
    # Main runner method
    #####################################################################
    def play(self):

        while True:
            # draw background
            SCREEN.blit(pg.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))

            # draw failure state if no solutions were found
            if self.game_state == "failure":
                self.draw_fail_state()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.KEYDOWN:
                        self.game_state = "play"
                continue

            elif self.game_state == "start":
                self.draw_start_state()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.KEYDOWN:
                        self.game_state = "play"

                continue

            self.draw_title()
            self.draw_text()
            self.draw_board_pieces(self.board, BOARD_X_OFFSET, BOARD_Y_OFFSET)
            self.draw_board_pieces(self.board_buffer, BOARD_X_OFFSET, BOARD_Y_OFFSET)
            self.draw_board_pieces(self.current_piece, CURR_PIECE_X_OFFSET, CURR_PIECE_Y_OFFSET)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                # add or erase tiles from the board with mouse click
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pg.mouse.get_pos()
                    row = (mouse_y - BOARD_Y_OFFSET) // SQUARE_HEIGHT
                    col = (mouse_x - BOARD_X_OFFSET) // SQUARE_WIDTH
                    if event.button == 1:  # Left click
                        self.add_piece_left_click(row, col)
                    elif event.button == 3:  # Right click
                        self.remove_piece_right_click(row, col)

                if event.type == pg.KEYDOWN and self.unused_pieces:
                    # rotate and flip current piece
                    if event.key == pg.K_r:
                        self.current_piece = self.rotate_piece(self.current_piece)
                    if event.key == pg.K_f:
                        self.current_piece = self.reflect_piece_y(self.current_piece)

                    # cycle through unused pieces
                    if event.key == pg.K_RIGHT or event.key == pg.K_SPACE:
                        self.piece_idx_pointer = (self.piece_idx_pointer + 1) % len(self.unused_pieces)
                        self.current_piece = self.pieces[self.unused_pieces[self.piece_idx_pointer]]

                    if event.key == pg.K_LEFT:
                        self.piece_idx_pointer = (self.piece_idx_pointer - 1) % len(self.unused_pieces)
                        self.current_piece = self.pieces[self.unused_pieces[self.piece_idx_pointer]]

                    # solve puzzle
                    if event.key == pg.K_s:
                        self.display_solution()

                    # provide hint
                    if event.key == pg.K_h:
                        self.display_hint()

                    if event.key == pg.K_c:
                        self.draw_buffer(True)

                # draw preview of placement of the current tile
                if event.type == self.draw_buffer_event:
                    self.draw_buffer()

            self.draw_dyanmic_board()

            pg.display.update()


if __name__ == "__main__":

    TangramGame().play()