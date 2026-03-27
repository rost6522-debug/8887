import pygame, sys, random

# --- Config ---
W, H = 400, 400
CELL = 20
FPS = 10
BLACK, WHITE = (0,0,0), (255,255,255)
GREEN, DGREEN = (0,200,0), (0,140,0)
RED = (200,0,0)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


def random_food(snake):
    cells = [(x, y) for x in range(0, W, CELL) for y in range(0, H, CELL)]
    free = [c for c in cells if c not in snake]
    return random.choice(free)


def draw(snake, food, score):
    screen.fill(BLACK)
    # Food
    pygame.draw.rect(screen, RED, (*food, CELL, CELL))
    # Snake
    for i, (x, y) in enumerate(snake):
        color = DGREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, (x, y, CELL, CELL))
        pygame.draw.rect(screen, BLACK, (x, y, CELL, CELL), 1)
    # Score
    screen.blit(font.render(f"Score: {score}", True, WHITE), (5, 5))
    pygame.display.flip()


def game_over(score):
    screen.fill(BLACK)
    screen.blit(font.render("GAME OVER", True, RED), (W//2 - 75, H//2 - 40))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (W//2 - 55, H//2))
    screen.blit(font.render("R — restart", True, WHITE), (W//2 - 70, H//2 + 40))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                return


def main():
    while True:
        snake = [(W//2, H//2)]
        dx, dy = CELL, 0
        food = random_food(snake)
        score = 0

        while True:
            clock.tick(FPS)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP    and dy == 0: dx, dy = 0, -CELL
                    if e.key == pygame.K_DOWN  and dy == 0: dx, dy = 0,  CELL
                    if e.key == pygame.K_LEFT  and dx == 0: dx, dy = -CELL, 0
                    if e.key == pygame.K_RIGHT and dx == 0: dx, dy =  CELL, 0

            head = (snake[0][0] + dx, snake[0][1] + dy)

            # Collision: wall or self
            if not (0 <= head[0] < W and 0 <= head[1] < H) or head in snake:
                break

            snake.insert(0, head)
            if head == food:
                score += 1
                food = random_food(snake)
            else:
                snake.pop()

            draw(snake, food, score)

        game_over(score)


if __name__ == "__main__":
    main()
