import pygame

ball_radius = 10
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
        self.radius = ball_radius
        self.id = id
        self.on_board = True

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
    def __init__(self, screen, mode):
        self.color = "dark green"

        size = (750, 400)
        self.surface = pygame.surface.Surface(size)
        self.surface.fill(self.color)

        screen_center = (screen.get_width() //2, screen.get_height() //2)
        self.rect = self.surface.get_rect(center=screen_center)

        self.mouse_down_pos = None

        self.balls = []
        self.holes = []

        self.wall_offset = 20  # wall thickness
        self.hole_offset = self.wall_offset * 1  # 1 = hole center on wall, <1 = hole inside wall, >1 = hole more on felt
        self.hole_radius = ball_radius * 1.5
        self.hole_strength = 0.7  # Higher = stronger

        for x in range(3):
            for y in range(2):
                self.holes.append(pygame.math.Vector2((self.rect.width - (self.hole_offset * 2)) // 2 * x + self.hole_offset, (self.rect.height - (self.hole_offset * 2)) * y + self.hole_offset))

        if mode == "8-ball":
            r = ball_radius
            rack_location = (200, self.rect.height // 2)
            dx = r * 2 * 0.87  # horizontal spacing (cos(30°) * diameter)
            self.balls = [
                # cue ball
                Ball(0, (400, rack_location[1])),
                # first row
                Ball(1, (rack_location[0], rack_location[1])),
                # second row
                Ball(11, (rack_location[0] - dx, rack_location[1] - r)),
                Ball(5, (rack_location[0] - dx, rack_location[1] + r)),
                # third row
                Ball(2, (rack_location[0] - 2*dx, rack_location[1] - 2*r)),
                Ball(8, (rack_location[0] - 2*dx, rack_location[1])),
                Ball(10, (rack_location[0] - 2*dx, rack_location[1] + 2*r)),
                # fourth row
                Ball(9, (rack_location[0] - 3*dx, rack_location[1] - 3*r)),
                Ball(7, (rack_location[0] - 3*dx, rack_location[1] - r)),
                Ball(14, (rack_location[0] - 3*dx, rack_location[1] + r)),
                Ball(4, (rack_location[0] - 3*dx, rack_location[1] + 3*r)),
                # fifth row
                Ball(6, (rack_location[0] - 4*dx, rack_location[1] - 4*r)),
                Ball(15, (rack_location[0] - 4*dx, rack_location[1] - 2*r)),
                Ball(13, (rack_location[0] - 4*dx, rack_location[1])),
                Ball(3, (rack_location[0] - 4*dx, rack_location[1] + 2*r)),
                Ball(12, (rack_location[0] - 4*dx, rack_location[1] + 4*r)),
            ]

    def draw(self, draw_surface):
        self.surface.fill(self.color)

        # draw cue line
        if self.mouse_down_pos:
            pos = pygame.mouse.get_pos()  # gets SCREEN pos
            current_mouse_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)  # Converts to table surface pos
            pygame.draw.line(self.surface, "white", self.balls[0].position, self.balls[0].position + pygame.math.Vector2(current_mouse_pos) - pygame.math.Vector2(self.mouse_down_pos))

        # draw walls
        wall_rect = self.rect.copy()
        wall_rect.topleft = (0, 0)
        pygame.draw.rect(self.surface, "brown", wall_rect, self.wall_offset)

        # draw holes
        for hole_pos in self.holes:
            pygame.draw.circle(self.surface, "black", hole_pos, self.hole_radius)

        # draw balls
        for ball in self.balls:
            if ball.on_board:
                ball.draw(self.surface)

        # draw game to screen
        draw_surface.blit(self.surface, self.rect)

    def update(self):
        for ball in self.balls:
            ball.update()

        for current_ball in self.balls:
            if current_ball.velocity.length() < 0.01:  # Only calculate collisions for moving balls
                continue
            if not current_ball.on_board:
                continue

            # --- 1. Ball–Ball Collisions ---
            for other_ball in self.balls:
                if current_ball == other_ball:  # Skip comparing self
                    continue
                if not other_ball.on_board:
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

                    # Elastic collision for equal mass (from hs physics / found online)
                    # v1' = v1 - (v_rel · n) * n
                    # v2' = v2 + (v_rel · n) * n
                    # This swaps the normal velocity components while preserving momentum.
                    current_ball.velocity -= vel_along_normal * n
                    other_ball.velocity += vel_along_normal * n

                    # Separate overlapping balls
                    overlap = (min_dist - distance) / 2
                    current_ball.position += n * overlap
                    other_ball.position -= n * overlap

            # --- 3. Hole Collisions ---
            for hole_pos in self.holes:
                delta_pos = current_ball.position - hole_pos
                distance = delta_pos.length()
                min_dist = current_ball.radius + self.hole_radius
                if distance < min_dist:
                    n = delta_pos.normalize()

                    # Attract overlapping balls
                    overlap = (min_dist - distance) / 2
                    current_ball.position -= n * overlap * self.hole_strength

                if distance < 15:
                    current_ball.on_board = False

            # --- 2. Ball–Wall Collisions (within self.rect) ---
            # LEFT wall
            if current_ball.position.x - current_ball.radius < 0 + self.wall_offset:
                current_ball.position.x = 0 + current_ball.radius + self.wall_offset
                current_ball.velocity.x *= -1  # Reflect X velocity

            # RIGHT wall
            if current_ball.position.x + current_ball.radius > self.rect.width - self.wall_offset:
                current_ball.position.x = self.rect.width - current_ball.radius - self.wall_offset
                current_ball.velocity.x *= -1

            # TOP wall
            if current_ball.position.y - current_ball.radius < 0 + self.wall_offset:
                current_ball.position.y = 0 + current_ball.radius + self.wall_offset
                current_ball.velocity.y *= -1

            # BOTTOM wall
            if current_ball.position.y + current_ball.radius > self.rect.height - self.wall_offset:
                current_ball.position.y = self.rect.height - current_ball.radius - self.wall_offset
                current_ball.velocity.y *= -1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse_down_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_up_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
            vector = pygame.math.Vector2(mouse_up_pos) - pygame.math.Vector2(self.mouse_down_pos)
            vector *= -1
            self.mouse_down_pos = None

            self.balls[0].move(vector)

        # Touch input (mobile)
        elif event.type == pygame.FINGERDOWN:
            # Convert normalized touch coordinates to screen pixels
            x = event.x * self.screen.get_width()
            y = event.y * self.screen.get_height()
            self.mouse_down_pos = (x - self.rect.x, y - self.rect.y)

        elif event.type == pygame.FINGERUP:
            x = event.x * self.screen.get_width()
            y = event.y * self.screen.get_height()
            mouse_up_pos = (x - self.rect.x, y - self.rect.y)
            vector = pygame.math.Vector2(mouse_up_pos) - pygame.math.Vector2(self.mouse_down_pos)
            vector *= -1
            self.mouse_down_pos = None
            self.balls[0].move(vector)