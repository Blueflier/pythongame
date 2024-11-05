import pygame
import socket
import json

class GameClient:
    def __init__(self, host='localhost', port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        
        # Initialize Pygame
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Multiplayer Game")
        
        # Player properties
        self.player_pos = {"x": 100, "y": 100}
        self.player_direction = 0  # Angle in degrees (0 = right, 90 = up)
        self.player_speed = 5
        self.bullets = []  # List to store active bullets
        self.bullet_speed = 10
        self.other_players = {}
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        # WASD movement
        if keys[pygame.K_a]:
            self.player_pos["x"] -= self.player_speed
            self.player_direction = 180
        if keys[pygame.K_d]:
            self.player_pos["x"] += self.player_speed
            self.player_direction = 0
        if keys[pygame.K_w]:
            self.player_pos["y"] -= self.player_speed
            self.player_direction = 90
        if keys[pygame.K_s]:
            self.player_pos["y"] += self.player_speed
            self.player_direction = 270
            
        # Shooting mechanic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            # Create new bullet at player position
            bullet = {
                "x": self.player_pos["x"],
                "y": self.player_pos["y"],
                "direction": self.player_direction
            }
            self.bullets.append(bullet)

    def update_bullets(self):
        # Update bullet positions
        for bullet in self.bullets[:]:  # Create a copy to safely remove bullets
            if bullet["direction"] == 0:  # Right
                bullet["x"] += self.bullet_speed
            elif bullet["direction"] == 90:  # Up
                bullet["y"] -= self.bullet_speed
            elif bullet["direction"] == 180:  # Left
                bullet["x"] -= self.bullet_speed
            elif bullet["direction"] == 270:  # Down
                bullet["y"] += self.bullet_speed
                
            # Remove bullets that are off screen
            if (bullet["x"] < 0 or bullet["x"] > self.width or 
                bullet["y"] < 0 or bullet["y"] > self.height):
                self.bullets.remove(bullet)

    def send_receive_data(self):
        # Send player position to server
        self.client.send(json.dumps(self.player_pos).encode())
        
        # Receive other players' positions
        data = self.client.recv(1024).decode()
        self.other_players = json.loads(data)
        
    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw all players as triangles to show direction
        for player_id, pos in self.other_players.items():
            if str(player_id) != str(self.client.getsockname()[1]):
                pygame.draw.circle(self.screen, (0, 0, 255), (pos["x"], pos["y"]), 20)
        
        # Draw self as a triangle
        player_triangle = self.get_player_triangle(self.player_pos["x"], self.player_pos["y"], self.player_direction)
        pygame.draw.polygon(self.screen, (255, 0, 0), player_triangle)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, (0, 0, 0), (int(bullet["x"]), int(bullet["y"])), 5)
        
        pygame.display.flip()

    def get_player_triangle(self, x, y, direction):
        # Helper function to create a triangle pointing in the right direction
        import math
        
        # Triangle size
        size = 20
        
        # Convert direction to radians
        angle = math.radians(direction)
        
        # Calculate triangle points
        point1 = (x + size * math.cos(angle), 
                 y - size * math.sin(angle))
        point2 = (x + size * math.cos(angle + 2.6),
                 y - size * math.sin(angle + 2.6))
        point3 = (x + size * math.cos(angle - 2.6),
                 y - size * math.sin(angle - 2.6))
        
        return [point1, point2, point3]

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            self.handle_input()
            self.update_bullets()  # Add bullet updates
            self.send_receive_data()
            self.draw()
            
            clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    client = GameClient()
    client.run() 