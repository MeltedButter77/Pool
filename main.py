import pygame
import asyncio
from objects import Table, Ball


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    # Wait for user to tap/click to start (required on mobile)
    print("Waiting for user interaction...")
    await asyncio.sleep(0)  # allow pygbag to initialize

    # Wait for a click/tap before starting
    while not pygame.event.peek((pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN)):
        await asyncio.sleep(0.05)
    print("Starting game loop!")

    table = Table(screen, "8-ball")

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

        await asyncio.sleep(0)  # Yield to web

asyncio.run(main())
