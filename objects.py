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

        self.type = "solid"
        if id > 8:
            id -= 8
            self.type = "stripe"
        self.color = ball_colors[id]

    def update(self):
        if not self.on_board: return
        self.position += self.velocity
        self.velocity *= 1 - self.drag

    def move(self, vector):
        self.velocity += vector

    def draw(self, surface, color_override=None):
        if color_override:
            pygame.draw.circle(surface, color_override, self.position, self.radius)
        else:
            pygame.draw.circle(surface, self.color, self.position, self.radius)
        if self.type == "stripe":
            pygame.draw.circle(surface, "white", self.position, self.radius, 3)

    def sink(self):
        self.on_board = False
        self.velocity = pygame.Vector2(0, 0)


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
        self.white_line_dist = 500
        self.hole_offset = self.wall_offset * 1  # 1 = hole center on wall, <1 = hole inside wall, >1 = hole more on felt
        self.hole_radius = ball_radius * 1.5
        self.hole_strength = 0.7  # Higher = stronger

        self.max_cue_strength = 150
        self.cue_strength = 0.2  # Higher = Stronger

        for x in range(3):
            for y in range(2):
                self.holes.append(pygame.math.Vector2((self.rect.width - (self.hole_offset * 2)) // 2 * x + self.hole_offset, (self.rect.height - (self.hole_offset * 2)) * y + self.hole_offset))

        if mode == "8-ball":
            r = ball_radius
            rack_location = (200, self.rect.height // 2)
            dx = r * 2 * 0.87  # horizontal spacing (cos(30°) * diameter)
            self.balls = [
                # cue ball
                Ball(0, (self.wall_offset + self.white_line_dist, rack_location[1])),
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

        # Draw white line
        pygame.draw.line(self.surface, "white",
                        (self.wall_offset + self.white_line_dist - 1, 0),
                        (self.wall_offset + self.white_line_dist - 1, self.rect.h),
                        2,
                        )
        pygame.draw.circle(self.surface, "white",(self.wall_offset + self.white_line_dist, self.rect.h//2), 3)

        # draw prediction line
        if self.mouse_down_pos and self.balls[0].on_board:
            pos = pygame.mouse.get_pos()  # gets SCREEN pos
            current_mouse_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)  # Converts to table surface pos

            # Prediction line
            direction = pygame.math.Vector2(self.mouse_down_pos) - pygame.math.Vector2(current_mouse_pos)
            start_pos = self.balls[0].position
            if direction.length() > 0:
                end_pos = start_pos + direction.normalize() * max(self.rect.w, self.rect.h)
                pygame.draw.line(self.surface, "white", start_pos, end_pos)

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

        # Draw placing white ball
        if not self.balls[0].on_board:
            if self.is_white_valid():
                self.balls[0].draw(self.surface)
            else:
                self.balls[0].draw(self.surface, "red")

        # draw game to screen
        draw_surface.blit(self.surface, self.rect)

        if self.mouse_down_pos and self.balls[0].on_board:
            # Draw mouse down pos
            pygame.draw.circle(draw_surface, "white", self.mouse_down_pos + pygame.math.Vector2(self.rect.topleft), 7, 3)

            pos = pygame.mouse.get_pos()  # gets SCREEN pos
            current_mouse_pos = (pos[0] - self.rect.x, pos[1] - self.rect.y)  # Converts to table surface pos

            # Cue line
            cue_length = 150
            direction = pygame.math.Vector2(current_mouse_pos) - pygame.math.Vector2(self.mouse_down_pos)
            if direction.length() > 0:
                if direction.length() > self.max_cue_strength:
                    direction.scale_to_length(self.max_cue_strength)
                start_pos = pygame.math.Vector2(self.rect.topleft) + self.balls[0].position + direction.normalize() * direction.length()
                end_pos = pygame.math.Vector2(self.rect.topleft) + self.balls[0].position + direction.normalize() * (direction.length() + cue_length)
                pygame.draw.line(draw_surface, "brown", start_pos, end_pos, 10)

    def update(self):
        # Update placing white ball
        if not self.balls[0].on_board:
            pos = pygame.mouse.get_pos()
            self.balls[0].position = pygame.Vector2(pos[0] - self.rect.x, pos[1] - self.rect.y)

        for ball in self.balls:
            ball.update()

        for current_ball in self.balls:
            if current_ball.velocity.length() < 0.01:  # Only calculate collisions for moving balls
                continue
            if not current_ball.on_board:  # Only calc for balls on the board
                continue

            # --- Ball–Ball Collisions ---
            for other_ball in self.balls:
                if self == other_ball:  # Skip comparing self
                    continue
                if not other_ball.on_board:  # Only calc for balls on the board
                    continue

                delta_pos = current_ball.position - other_ball.position
                distance = delta_pos.length()
                min_dist = current_ball.radius + other_ball.radius

                if distance < min_dist and delta_pos.length() > 0:
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

            # --- Holes ---
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
                    current_ball.sink()

            # --- Walls --
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
            self.mouse_down_pos = pygame.math.Vector2(event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)

            if not self.balls[0].on_board and self.is_white_valid():
                self.balls[0].on_board = True
                self.mouse_down_pos = None  # Clears the selection i.e ball doesn't get shot right as u place it

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.mouse_down_pos and self.balls[0].on_board:
                mouse_up_pos = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                vector = pygame.math.Vector2(mouse_up_pos) - pygame.math.Vector2(self.mouse_down_pos)
                vector *= -1

                if vector.length() > self.max_cue_strength:
                    vector.scale_to_length(self.max_cue_strength)
                self.balls[0].move(vector * self.cue_strength)
            self.mouse_down_pos = None

    def is_white_valid(self):
        white_ball = self.balls[0]

        for other_ball in self.balls:
            if white_ball == other_ball:  # Skip comparing self
                continue

            delta_pos = white_ball.position - other_ball.position
            distance = delta_pos.length()
            min_dist = white_ball.radius + other_ball.radius

            if distance < min_dist:
                return False

        # LEFT wall
        if white_ball.position.x < 0 + self.wall_offset + self.white_line_dist:
            white_ball.position.x = self.wall_offset + self.white_line_dist
        # RIGHT wall
        if white_ball.position.x + white_ball.radius > self.rect.width - self.wall_offset:
            white_ball.position.x = self.rect.width - white_ball.radius - self.wall_offset
        # TOP wall
        if white_ball.position.y - white_ball.radius < 0 + self.wall_offset:
            white_ball.position.y = 0 + white_ball.radius + self.wall_offset
        # BOTTOM wall
        if white_ball.position.y + white_ball.radius > self.rect.height - self.wall_offset:
            white_ball.position.y = self.rect.height - white_ball.radius - self.wall_offset

        return True
