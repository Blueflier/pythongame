import pygame
import asyncio
import websockets
import json
import sys

class GameClient:
    def __init__(self, server_url):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Multiplayer Game")
        self.clock = pygame.time.Clock()

        # Game state
        self.player_pos = {"x": 100, "y": 100, "direction": 0}
        self.player_speed = 5
        self.other_players = {}
        self.server_url = server_url
        self.websocket = None
        self.my_id = None

    async def connect(self):
        try:
            print(f"Attempting to connect to {self.server_url}")
            self.websocket = await websockets.connect(self.server_url)
            print("Connected to server!")
            self.my_id = str(id(self.websocket))
        except Exception as e:
            print(f"Failed to connect: {str(e)}")
            print(f"Error type: {type(e)}")
            sys.exit(1)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.player_pos["x"] -= self.player_speed
            self.player_pos["direction"] = 180
        if keys[pygame.K_d]:
            self.player_pos["x"] += self.player_speed
            self.player_pos["direction"] = 0
        if keys[pygame.K_w]:
            self.player_pos["y"] -= self.player_speed
            self.player_pos["direction"] = 90
        if keys[pygame.K_s]:
            self.player_pos["y"] += self.player_speed
            self.player_pos["direction"] = 270

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw other players
        for player_id, pos in self.other_players.items():
            if player_id != self.my_id:
                pygame.draw.circle(self.screen, (0, 0, 255), 
                                 (int(pos["x"]), int(pos["y"])), 20)
        
        # Draw self
        pygame.draw.circle(self.screen, (255, 0, 0), 
                         (int(self.player_pos["x"]), int(self.player_pos["y"])), 20)
        
        pygame.display.flip()

    async def game_loop(self):
        while True:
            # Handle Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            # Handle input and update position
            self.handle_input()

            # Send position to server
            try:
                await self.websocket.send(json.dumps(self.player_pos))
                # Receive updates from server
                response = await self.websocket.recv()
                self.other_players = json.loads(response)
            except websockets.ConnectionClosed:
                print("Connection to server closed")
                return

            # Draw game state
            self.draw()
            
            # Maintain 60 FPS
            self.clock.tick(60)
            await asyncio.sleep(0)  # Let other tasks run

async def main():
    # Use Railway URL when deployed, localhost for testing
    SERVER_URL = "wss://pythongame-production.up.railway.app:8765"  # Change this to your Railway URL when deployed
    #SERVER_URL = "ws://localhost:8765"
    game = GameClient(SERVER_URL)
    await game.connect()
    await game.game_loop()

if __name__ == "__main__":
    asyncio.run(main()) 