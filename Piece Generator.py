import random

def generate_random_walk(shape, max_piece_size, start_point):
    """
    Generates a random walk to form a piece from the shape starting at a specific point.
    If the walk gets stuck, it stops.
    """
    piece = set()
    piece.add(start_point)

    while len(piece) < max_piece_size:
        current = random.choice(list(piece))
        neighbors = [
            (current[0] + dx, current[1] + dy)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
        ]
        random.shuffle(neighbors)

        stuck = True
        for neighbor in neighbors:
            if neighbor in shape and neighbor not in piece:
                piece.add(neighbor)
                stuck = False
                break

        if stuck:
            break

    return piece

def split_shape_into_pieces(shape, max_piece_size):
    """
    Splits the shape into Tetris-like pieces using a random walking algorithm.
    If a random walk gets stuck, a new random start point is chosen.
    The process ends once the entire shape is divided into non-overlapping pieces.
    """
    shape = set(shape)
    pieces = []

    while shape:
        start_point = min(shape)  # Start from the top-left most point
        piece = generate_random_walk(shape, max_piece_size, start_point)

        if not piece:  # If the walk didn't form a piece, choose a new random point
            start_point = random.choice(list(shape))
            piece = generate_random_walk(shape, max_piece_size, start_point)

        pieces.append(piece)
        shape -= piece  # Remove the covered points from the shape

    return pieces

def draw_grid(grid, shape):
    """
    Prints the grid with the given shape.
    """
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if (i, j) in shape:
                print("#", end=" ")
            else:
                print(".", end=" ")
        print()

def main():
    # Example shape (can be customized)
    grid = [[0] * 10 for _ in range(10)]
    shape = {
        (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3),
        (3, 1), (3, 2), (3, 3), (4, 4), (4, 5), (5, 4), (5, 5)
    }

    print("Original Shape:")
    draw_grid(grid, shape)

    max_piece_size = 4  # Maximum size of a Tetris-like piece
    pieces = split_shape_into_pieces(shape, max_piece_size)

    print("\nTetris-like Pieces:")
    for index, piece in enumerate(pieces, start=1):
        print(f"Piece {index}:")
        draw_grid(grid, piece)
        print()

if __name__ == "__main__":
    main()