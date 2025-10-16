import pygame

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

ball_colors = {
    0: "white",
    1: "gold",
    2: "dark blue",
    3: "red",
    4: "purple",
    5: "orange",
    6: "green",
    7: "dark red",
    8: "black"
}


class Ball:
    def __init__(self, id, position):
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2((0, 0))
        self.radius = 10

        self.drag = 0.02  # Higher = More drag
        self.cue_strength = 0.1  # Higher = Stronger

        self.type = "solid"
        if id > 8:
            id -= 8
            self.type = "strip"
        self.color = ball_colors[id]

    def update(self):
        self.position += self.velocity
        self.velocity *= 1 - self.drag

    def move(self, vector):
        self.velocity += vector * self.cue_strength

    def draw(self, surface):
        if self.type == "solid":
            pygame.draw.circle(surface, self.color, self.position, self.radius)
        else:
            pygame.draw.circle(surface, self.color, self.position, self.radius)
            pygame.draw.circle(surface, "white", self.position, self.radius, 3)


class Table:
    def __init__(self):
        self.color = "dark green"

        size = (750, 400)
        self.surface = pygame.surface.Surface(size)
        self.surface.fill(self.color)

        screen_center = (screen.get_width() //2, screen.get_height() //2)
        self.rect = self.surface.get_rect(center=screen_center)

        self.mouse_down_pos = None

        self.balls = []

    def draw(self, draw_surface):
        self.surface.fill(self.color)

        for ball in self.balls:
            ball.draw(table.surface)

        # draw cue line
        if self.mouse_down_pos:
            pos = pygame.mouse.get_pos()  # gets SCREEN pos
            current_mouse_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)  # Converts to table surface pos
            pygame.draw.line(self.surface, "white", self.balls[0].position, self.balls[0].position + pygame.math.Vector2(current_mouse_pos) - pygame.math.Vector2(self.mouse_down_pos))

        draw_surface.blit(self.surface, self.rect)

    def update(self):
        for ball in self.balls:
            ball.update()

        for current_ball in self.balls:
            if current_ball.velocity.length() < 0.01:  # Only calculate collisions for moving balls
                continue

            # --- 1. Ball–Ball Collisions ---
            for other_ball in self.balls:
                if current_ball == other_ball:  # Skip comparing self
                    continue

                delta_pos = current_ball.position - other_ball.position
                distance = delta_pos.length()
                min_dist = current_ball.radius + other_ball.radius

                if distance < min_dist:
                    # Get collision normal
                    n = delta_pos.normalize()

                    # Get relative velocity
                    v_rel = current_ball.velocity - other_ball.velocity

                    # Get speed along the normal
                    vel_along_normal = v_rel.dot(n)
                    if vel_along_normal > 0:  # Balls are separating
                        continue

                    # Elastic collision for equal mass (found online)
                    # v1' = v1 - (v_rel · n) * n
                    # v2' = v2 + (v_rel · n) * n
                    # This swaps the normal velocity components while preserving momentum.
                    current_ball.velocity -= vel_along_normal * n
                    other_ball.velocity += vel_along_normal * n

                    # Separate overlapping balls
                    overlap = (min_dist - distance) / 2
                    current_ball.position += n * overlap
                    other_ball.position -= n * overlap

            # --- 2. Ball–Wall Collisions (within self.rect) ---
            # LEFT wall
            if current_ball.position.x - current_ball.radius < 0:
                current_ball.position.x = 0 + current_ball.radius
                current_ball.velocity.x *= -1  # Reflect X velocity

            # RIGHT wall
            if current_ball.position.x + current_ball.radius > self.rect.width:
                current_ball.position.x = self.rect.width - current_ball.radius
                current_ball.velocity.x *= -1

            # TOP wall
            if current_ball.position.y - current_ball.radius < 0:
                current_ball.position.y = 0 + current_ball.radius
                current_ball.velocity.y *= -1

            # BOTTOM wall
            if current_ball.position.y + current_ball.radius > self.rect.height:
                current_ball.position.y = self.rect.height - current_ball.radius
                current_ball.velocity.y *= -1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_up_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
            vector = pygame.math.Vector2(mouse_up_pos) - pygame.math.Vector2(self.mouse_down_pos)
            vector *= -1
            self.mouse_down_pos = None

            self.balls[0].move(vector)


table = Table()
for i in range(16):
    table.balls.append(Ball(i, (25*i+20, 100)))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(200)

        table.handle_event(event)

    table.update()
    table.draw(screen)

    pygame.display.flip()
    screen.fill("dark gray")
    clock.tick(60)