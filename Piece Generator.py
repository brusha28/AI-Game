import random
from PIL import Image
from edge_detection import extract_shape

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

        while True:
            stuck = True
            for current in list(piece):
                neighbors = [
                    (current[0] + dx, current[1] + dy)
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                ]
                random.shuffle(neighbors)

                for neighbor in neighbors:
                    if neighbor in shape and neighbor not in piece:
                        piece.add(neighbor)
                        stuck = False
                        break
                if not stuck:
                    break

            if stuck or len(piece) >= max_piece_size:
                break
        if stuck or len(piece) >= max_piece_size:
            break

    return piece

def merge_small_pieces(pieces, min_piece_size, max_piece_size):
    """
    Merges small pieces into larger ones if they share an edge.
    """
    merged_pieces = []
    while pieces:
        piece = pieces.pop()
        if len(piece) < min_piece_size:
            neighbors = []
            for other_piece in pieces:
                if any(
                    (x + dx, y + dy) in other_piece
                    for x, y in piece
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                ) and len(other_piece) <= max_piece_size:
                    neighbors.append(other_piece)
            if neighbors:
                selected_piece = random.choice(neighbors)
                selected_piece.update(piece)
            else:
                merged_pieces.append(piece)
        else:
            merged_pieces.append(piece)
    return merged_pieces

def split_shape_into_pieces(shape, max_piece_size, min_piece_size):
    """
    Splits the shape into Tetris-like pieces using a random walking algorithm.
    If a random walk gets stuck, a new random start point is chosen.
    The process ends once the entire shape is divided into non-overlapping pieces.
    Ensures that pieces are not smaller than the minimum piece size.
    """
    shape = set(shape)
    pieces = []

    while shape:
        start_point = min(shape)  # Start from the top-left most point
        piece = generate_random_walk(shape, max_piece_size, start_point)

        if not piece or len(piece) < min_piece_size:  # If the walk didn't form a piece or is too small, choose a new random point
            start_point = random.choice(list(shape))
            piece = generate_random_walk(shape, max_piece_size, start_point)

        pieces.append(piece)
        shape -= piece  # Remove the covered points from the shape

    pieces = merge_small_pieces(pieces, min_piece_size, max_piece_size)
    return pieces

def draw_grid(grid, shape, piece_number):
    """
    Prints the grid with the given shape.
    """
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if (i, j) in shape:
                print(piece_number, end=" ")
            else:
                print(".", end=" ")
        print()

def combine_pieces(grid, pieces):
    """
    Combines all pieces into a single grid.
    """
    combined_grid = [[0] * len(grid[0]) for _ in range(len(grid))]
    for piece_number, piece in enumerate(pieces, start=1):
        for (i, j) in piece:
            combined_grid[i][j] = piece_number
    return combined_grid

def print_combined_grid(grid):
    """
    Prints the combined grid with all pieces.
    """
    for row in grid:
        for cell in row:
            if cell == 0:
                print(".", end=" ")
            else:
                print(cell, end=" ")
        print()

def convert_image_to_coordinates(image_path, max_grid_size):
    # Load the image
    image = Image.open(image_path)
    
    # Resize the image to the desired grid size
    image = image.resize((max_grid_size, max_grid_size))
    
    # Convert the image to grayscale
    image = image.convert('L')
    
    # Threshold the image to convert it to black and white
    threshold = 200
    image = image.point(lambda p: p > threshold and 255)
    
    # Extract coordinates of black pixels
    coordinates = set()
    for y in range(max_grid_size):
        for x in range(max_grid_size):
            if image.getpixel((x, y)) == 0:  # Black pixel
                coordinates.add((y, x))
    
    return coordinates

def main():
    max_piece_size = 5  # Maximum size of a Tetris-like piece (+1) Must be 5 or above
    min_piece_size = 3  # Maximum size of a Tetris-like piece (+1) 
    max_grid_size = 18  # Maximum size of square grid

    grid = [[0] * max_grid_size for _ in range(max_grid_size)]
    # shape = {
    #     (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3),
    #     (3, 1), (3, 2), (3, 3), (3, 4), (4, 4), (4, 5), (5, 4), (5, 5), (6, 5), (6, 6),
    # }
    image_path = 'images/image2.jpg'
    shape = extract_shape(image_path)
    shape = convert_image_to_coordinates(shape, max_grid_size)
    print(shape)
    print("Original Shape:")
    draw_grid(grid, shape, "#")

    pieces = split_shape_into_pieces(shape, max_piece_size, min_piece_size)

    print("\nTetris-like Pieces:")
    for index, piece in enumerate(pieces, start=1):
        print(f"Piece {index}:")
        draw_grid(grid, piece, index)
        print()

    combined_grid = combine_pieces(grid, pieces)
    print("\nCombined Grid with All Pieces:")
    print_combined_grid(combined_grid)

if __name__ == "__main__":
    main()