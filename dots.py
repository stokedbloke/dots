import pygame
import sys

pygame.init()

# Dynamic Screen Size for Mobile
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
GRID_SIZE = 10
DOT_SIZE = max(10, WIDTH // 60)  # Adjust dot size for visibility
LINE_WIDTH = max(5, WIDTH // 100)
DOT_SPACING = (WIDTH - 2 * DOT_SIZE) // (GRID_SIZE - 1)
BOX_SIZE = DOT_SPACING
LINE_COLOR = (0, 0, 0)
X_COLOR = (255, 0, 0)
O_COLOR = (0, 0, 255)
BOX_FILL_X = (255, 200, 200)
BOX_FILL_O = (200, 200, 255)
BG_COLOR = (255, 255, 255)
UNDO_COLOR = (200, 200, 200)
UNDO_HOVER_COLOR = (150, 150, 150)
FONT = pygame.font.Font(None, max(36, WIDTH // 20))  # Adjust font size for readability

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Boxes Game")

# Game state
dots = [[(DOT_SIZE + x * DOT_SPACING, DOT_SIZE + y * DOT_SPACING) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
lines = set()
boxes = {}
player = "X"
scores = {"X": 0, "O": 0}
history = []  # Store moves for undo
selected_dot = None

def draw_dots():
    for row in dots:
        for dot in row:
            pygame.draw.circle(screen, LINE_COLOR, dot, DOT_SIZE // 2)

def draw_lines():
    for line, owner in lines:
        color = X_COLOR if owner == "X" else O_COLOR
        pygame.draw.line(screen, color, line[0], line[1], LINE_WIDTH)

def draw_boxes():
    for (x, y), owner in boxes.items():
        rect = pygame.Rect(dots[y][x][0], dots[y][x][1], BOX_SIZE, BOX_SIZE)
        fill_color = BOX_FILL_X if owner == "X" else BOX_FILL_O
        pygame.draw.rect(screen, fill_color, rect)

        # Draw X or O inside the box
        text_surface = FONT.render(owner, True, X_COLOR if owner == "X" else O_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_scores():
    score_x = FONT.render(f"X: {scores['X']}", True, X_COLOR)
    score_o = FONT.render(f"O: {scores['O']}", True, O_COLOR)
    screen.blit(score_x, (10, HEIGHT - 50))  # Adjust placement for visibility
    screen.blit(score_o, (WIDTH - 100, HEIGHT - 50))

def draw_undo_button(mouse_pos):
    undo_rect = pygame.Rect(10, 10, 100, 50)  # Larger for mobile
    pygame.draw.rect(screen, UNDO_HOVER_COLOR if undo_rect.collidepoint(mouse_pos) else UNDO_COLOR, undo_rect)
    screen.blit(FONT.render("Undo", True, (0, 0, 0)), (25, 15))
    return undo_rect

def check_box(x, y):
    """Checks if a box at (x, y) is completed and assigns it to the player."""
    if (x, y) in boxes:
        return False

    top = (dots[y][x], dots[y][x + 1])
    bottom = (dots[y + 1][x], dots[y + 1][x + 1])
    left = (dots[y][x], dots[y + 1][x])
    right = (dots[y][x + 1], dots[y + 1][x + 1])

    if (top, "X") in lines or (top, "O") in lines:
        if (bottom, "X") in lines or (bottom, "O") in lines:
            if (left, "X") in lines or (left, "O") in lines:
                if (right, "X") in lines or (right, "O") in lines:
                    boxes[(x, y)] = player  # Assign ownership of the box
                    scores[player] += 1  # Increment score
                    return True
    return False

def undo():
    """Undo last move and remove boxes if necessary."""
    global player
    if history:
        last_move = history.pop()
        line, owner = last_move
        lines.remove((line, owner))

        removed_boxes = [box for box, box_owner in boxes.items() if any(line == side for side in [
            ((dots[box[1]][box[0]], dots[box[1]][box[0] + 1])),
            ((dots[box[1] + 1][box[0]], dots[box[1] + 1][box[0] + 1])),
            ((dots[box[1]][box[0]], dots[box[1] + 1][box[0]])),
            ((dots[box[1]][box[0] + 1], dots[box[1] + 1][box[0] + 1]))
        ])]

        for box in removed_boxes:
            del boxes[box]
            scores[owner] -= 1

        if not removed_boxes:
            player = "O" if player == "X" else "X"

running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            if event.type == pygame.FINGERDOWN:
                x, y = int(event.x * WIDTH), int(event.y * HEIGHT)  # Convert touch position
            else:
                x, y = event.pos

            undo_rect = draw_undo_button(mouse_pos)
            if undo_rect.collidepoint(x, y):
                undo()
            else:
                for j, row in enumerate(dots):
                    for i, dot in enumerate(row):
                        if abs(x - dot[0]) < DOT_SIZE * 2 and abs(y - dot[1]) < DOT_SIZE * 2:
                            if selected_dot is None:
                                selected_dot = dot
                            else:
                                line = (min(selected_dot, dot), max(selected_dot, dot))
                                if line not in [l for l, _ in lines]:
                                    lines.add((line, player))
                                    history.append((line, player))

                                    box_completed = False
                                    for bx, by in [(i, j), (i-1, j), (i, j-1), (i-1, j-1)]:
                                        if 0 <= bx < GRID_SIZE - 1 and 0 <= by < GRID_SIZE - 1:
                                            if check_box(bx, by):
                                                box_completed = True

                                    if not box_completed:
                                        player = "O" if player == "X" else "X"

                                selected_dot = None

    screen.fill(BG_COLOR)
    draw_boxes()
    draw_lines()
    draw_dots()
    draw_scores()
    draw_undo_button(mouse_pos)

    pygame.display.flip()

pygame.quit()
