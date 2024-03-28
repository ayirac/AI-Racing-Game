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
        self.braking_factor = 0.05
        self.topSpeed = topSpeed
        self.topacceleration = topacceleration

        self.recordings = []
        self.recording = False
        self.recordingLastTime = -1
        self.recordingCoolDown = -1
        
        self.accelerationFac = accelerationFactor
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(image), (20, 35)), 90)

        self.rect = self.image.get_rect()
        self.rect.center = startPos
    
    def accelerate(self):
        self.acceleration = min(self.acceleration + self.accelerationFac, self.topacceleration)  # Gradual change

    def decelerate(self):
        self.acceleration = max(-self.braking_factor, -self.topacceleration)


    # https://stackoverflow.com/questions/46525021/what-is-the-simplest-way-to-rotate-a-pygame-sprite-on-holding-a-button
    def turnLeft(self):  # Need to fuck with ang rotation & then each tick use it to change the cars  rotation based on the forces
        self.rotation = (self.rotation + 1) % 360

    def turnRight(self): 
        self.rotation = (self.rotation - 1) % 360

    def updateAcceleration(self):
        if self.acceleration != 0:
            drag = self.drag_factor
            if self.acceleration > 0: 
                self.acceleration = max(self.acceleration - drag, 0) 
            elif self.acceleration < 0:
                self.acceleration = min(self.acceleration + drag, 0) 
                
    def updateVelocity(self):
        self.velocity += self.acceleration

        # Apply Drag 
        drag = self.drag_factor * self.speed**2  # Square the speed for realistic drag
        if self.velocity > 0: 
            self.velocity -= drag
        elif self.velocity < 0:
            self.velocity += drag  # Drag opposes the direction of motion
        
        # Clamp velocity
        self.velocity = max(-self.topSpeed, min(self.velocity, self.topSpeed)) 
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

        if (self.recording == True):
            curTime = pygame.time.get_ticks()
            if (self.recordingLastTime + 200 < curTime):
                self.recordingLastTime = curTime
                self.recordings.append((self.pos, self.rotation))

    #def navigateToPos()

    def startRecording(self):
        curTime = pygame.time.get_ticks()
        if self.recordingCoolDown + 600 < curTime:
            self.recordingCoolDown = curTime
            if self.recording:  # You can directly use `if self.recording:` instead of `if self.recording == True:`
                with open("routes.txt", "a") as f:
                    # Convert each tuple to a string representation
                    recordings_str = ', '.join([str(pos) for pos in self.recordings])
                    f.write(recordings_str + '\n')  # Add a newline after each recording
                print("Recordings saved to routes.txt")
                self.recording = False
            else:
                print("Recording started!")
                self.recording = True


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
    cars = []
    c = Car('Chevy Cruze', 'images/car.png', 0.10, 8, 2, (1500, 900))
    cars.append(c)
    c1 = Car('Chevy Cruze', 'images/car.png', 0.10, 8, 2, (1500, 900))
    cars.append(c1) 
    

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
        elif keys[pygame.K_SPACE]:
            c.startRecording()

        # Update & Finalize
        c.updateAcceleration()
        c.updateVelocity()
        c.updatePosition(walls)
        
        # Draw
        screen.fill((255, 255, 255))
        screen.blit(surface, (0,0))

        for cs in cars:
            cs.draw()
        for w in walls:
            pygame.draw.rect(screen, (255, 0, 0), w)
        c.raycast(walls)
        pygame.display.update()
       