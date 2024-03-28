import pygame
import math

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
pygame.init()
# Set up the window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Turbo Racer")

class Car:
    def __init__(self, name, image, accelerationFactor, topSpeed, topacceleration, startPos):
        self.name = name
        self.pos = startPos
        self.speed = 0.0
        self.velocity = 0.0
        self.acceleration = 0.0
        self.rotation = 0.0

        self.drag_factor = 0.03

        self.topSpeed = topSpeed
        self.topacceleration = topacceleration
        
        self.accelerationFac = accelerationFactor

        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(image), (20, 35)), 90)

        self.rect = self.image.get_rect()
        self.rect.center = startPos
    
    def accelerate(self):
        self.acceleration = max(self.acceleration + self.accelerationFac, self.topacceleration)  # Gradual change

    def decelerate(self):
        self.acceleration = max(self.acceleration - self.accelerationFac, 0) 

    # https://stackoverflow.com/questions/46525021/what-is-the-simplest-way-to-rotate-a-pygame-sprite-on-holding-a-button
    def turnLeft(self):  # Need to fuck with ang rotation & then each tick use it to change the cars  rotation based on the forces
        self.rotation = (self.rotation + 1) % 360

    def turnRight(self): 
        self.rotation = (self.rotation - 1) % 360

    def updateacceleration(self):
        print("Velocity:", self.velocity)
        
        print("Acceleration before:", self.acceleration) 
        if self.acceleration != 0:
            drag = self.drag_factor * self.speed**2  # Square speed for gradual drag
            if self.velocity < 0:  
                drag *= -1  
            print("Drag:", drag)  
            if self.acceleration > 0:
                self.acceleration -= drag  
            elif self.acceleration < 0:
                self.acceleration += drag  
            print("Acceleration after:", self.acceleration)   
                
    def updateVelocity(self):
        self.velocity += self.acceleration
        self.velocity = max(-self.topSpeed, min(self.velocity, self.topSpeed))  # Clamp velocity
        if self.velocity > 0:
            self.velocity = max(self.velocity - 1, 0)
        
        self.speed = abs(self.velocity)

    def updatePosition(self, walls):
        radians = math.radians(self.rotation)
        dx = math.cos(radians) * self.velocity
        dy = -math.sin(radians) * self.velocity
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        for wall in walls:
            if wall.colliderect(pygame.Rect(*new_pos, self.rect.width, self.rect.height)):
                self.velocity = 0
                self.acceleration = 0
                return

        self.pos = new_pos
        self.rect.center = self.pos

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect)

    def raycast(self, walls):
        ray_length = 250
        radians = math.radians(self.rotation)
        end_x = self.pos[0] + ray_length * math.cos(radians)
        end_y = self.pos[1] - ray_length * math.sin(radians)
        
        intersection = None
        #for wall in walls:
           # intersection_point = wall.clipline(self.pos, (end_x, end_y))
           # print("Wall:", wall, "Intersection Point:", intersection_point)
           # if intersection_point:
           #     intersection = intersection_point
            #    break
           # print("LO")

        
        #if intersection:
            #print(f"YO YO YO {intersection}")
        pygame.draw.line(screen, (255, 0, 0), self.pos, (end_x, end_y), 2)


if __name__ == "__main__":
    img = pygame.image.load("images/map.png") # Setup color map
    surface = img.convert()
    width, height = surface.get_size()
    track_color = (180, 168, 77) # Use the RGB color of the racing track in the image
    background_color = (0, 0, 0) # Use the RGB color of the background in the image

    # Setup walls
    walls = []
    for x in range(width):
        for y in range(height):
            color = surface.get_at((x, y))
            if color == track_color:
                if surface.get_at((x+1, y)) != track_color or surface.get_at((x-1, y)) != track_color or \
                surface.get_at((x, y+1)) != track_color or surface.get_at((x, y-1)) != track_color:
                    rect = pygame.Rect(x, y, 1, 1)
                    walls.append(rect)
    wallWidth = 150
    wallHeight = 30
    c = Car('Chevy Cruze', 'images/car.png', 0.17, 18, 3, (1500, 900))

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Handle keybindings
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and keys[pygame.K_a]:
            c.accelerate()
            c.turnLeft()
        elif keys[pygame.K_w] and keys[pygame.K_d]:
            c.accelerate()
            c.turnRight()
        elif keys[pygame.K_a] and keys[pygame.K_s]:
            c.decelerate()
            c.turnLeft() 
        elif keys[pygame.K_s] and keys[pygame.K_d]:
            c.decelerate()
            c.turnRight()
        elif keys[pygame.K_w]:
            c.accelerate()
        elif keys[pygame.K_s]:
            c.decelerate()
        elif keys[pygame.K_a]:
            c.turnLeft()
        elif keys[pygame.K_d]:
            c.turnRight()

        # Update & Finalize
        c.updateacceleration()
        c.updateVelocity()
        c.updatePosition(walls)
        
        # Draw
        screen.fill((255, 255, 255))
        screen.blit(surface, (0,0))
        c.draw()
        for w in walls:
            pygame.draw.rect(screen, (255, 0, 0), w)
            c.raycast(walls)  # Draw raycast lines
        pygame.display.update()
        #print(c.speed)
       