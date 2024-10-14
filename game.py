"""
DUNGEON ALGORITHM STEPS:
Initialize a grid.
Generate rooms
    Room corner
    Check if corner will work
    Take tiles out of walls and deposit into room
    OPTIONAL - furnish rooms
Generate pathways
"""

import math
import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 800), pygame.DOUBLEBUF)
pygame.display.set_caption("Dungeon: Random")

width = 40
height = 30
roomcount = 8
rooms = 0
maze = []
roomSet = []
roomList = []
wallSet = []
frontier = []
directionsR3 = [(3, 0), (0, 3), (-3, 0), (0, -3)]
directionsR2 = [(2, 0), (0, 2), (-2, 0), (0, -2)]
directionsR1 = [(1, 0), (0, 1), (-1, 0), (0, -1)]

# PLAYER STATS
health = 100
stamina = 200
magic = 100
coords = [0, 0]
equipped = [['pants', 'Cloth Covering', 0, 0, 0]]
invisible = 0
freezetime = 0
waitingOnTP = 0
# equipment format: [slot,name,def boost, hp boost, damage boost]

# UI STUFF
mousecoords = []
mouseover = ''
mouseover1 = ''

# ATTACKS
attacks = [
    [True, "Stab", 0, 0, 0],
    [True, "Longshot", 4, 0, 0],
    [False, "Poison", 3, 0, 0],
    [False, "Freeze", 2, 0, 0],
    [True, "Heal", 6, 0, 5],
    [True, "Explode", 5, 0, 0],
    [True, "Cultivate", 5, 0, 5],
    [False, "Lifesteal", 5, 0, 0],
    [True, "Time Freeze", 5, 0, 50],
    [True, "Invisibility", 5, 0, 20],
    [False, "Decoy", 20, 0, 0],
    [True, "Teleport", 25, 0, 25],
    [False, "Magic Bullet", 10, 0, 0],
    [True, "Armageddon", 50, 0, 60]
]
# attacks stores unlocked, description, max cooldown, current cooldown
attackpulse = [0, []]

# ENEMY CLASS
enemies = []
enemiesCoords = []


class Enemy:
    def __init__(self, x, y, health, damage, range, type):
        self.rect = pygame.Rect(5 + 20 * x, 5 + 20 * y, 18, 18)
        self.coords = [x, y]
        self.health = health
        self.damage = damage
        self.range = range
        self.type = type


class attackFlash:
    def __init__(self, x, y):
        self.rect = pygame.Rect(5 + 20 * x, 5 + 20 * y, 18, 18)


def enemyWander(enemy):
    # WANDERING MOVEMENT
    neighbors = []
    for i in directionsR1:
        if [enemy.coords[0] + i[0], enemy.coords[1] + i[1]] in roomSet and [enemy.coords[0] + i[0], enemy.coords[1] + i[
            1]] not in enemiesCoords:
            neighbors.append([enemy.coords[0] + i[0], enemy.coords[1] + i[1]])

    if enemy.coords not in roomSet:
        for i in directionsR1:
            if [enemy.coords[0] + i[0], enemy.coords[1] + i[1]] in maze and [enemy.coords[0] + i[0],
                                                                             enemy.coords[1] + i[
                                                                                 1]] not in enemiesCoords:
                neighbors.append([enemy.coords[0] + i[0], enemy.coords[1] + i[1]])
    if neighbors:
        enemiesCoords.remove(enemy.coords)
        enemy.coords = random.choice(neighbors)
        enemy.rect = pygame.Rect(5 + 20 * enemy.coords[0], 5 + 20 * enemy.coords[1], 18, 18)
        enemiesCoords.append(enemy.coords)


def enemyTracking(enemy):
    # TRACKING MOVEMENT
    dx = int(coords[0] - enemy.coords[0])
    dy = int(coords[1] - enemy.coords[1])
    confirm = None
    # Move closer to the player along the axis with the greater distance
    if dx or dy:

        # Diagonal
        if abs(dy) == abs(dx):
            dx = math.copysign(1 if dx != 0 else 0, dx)
            dy = math.copysign(1 if dy != 0 else 0, dy)
            neighbors = []
            testcase = [enemy.coords[0], enemy.coords[1] + dy]
            if testcase in maze or testcase in roomSet:
                if testcase not in enemiesCoords and testcase != coords:
                    neighbors.append(testcase)
            testcase = [enemy.coords[0] + dx, enemy.coords[1]]
            if testcase in maze or testcase in roomSet:
                if testcase not in enemiesCoords and testcase != coords:
                    neighbors.append(testcase)
            if neighbors:
                confirm = random.choice(neighbors)

        # Largest axis
        else:
            directionStack = [[math.copysign(1 if dx != 0 else 0, dx), 0], [0, math.copysign(1 if dy != 0 else 0, dy)]]
            largest = 0 if abs(dx) > abs(dy) else 1
            smallest = 1 if abs(dx) > abs(dy) else 0
            testcase = [enemy.coords[0] + directionStack[smallest][0], enemy.coords[1] + directionStack[smallest][1]]

            if testcase in maze or testcase in roomSet:
                if testcase != coords and testcase not in enemiesCoords:
                    confirm = testcase
            testcase = [enemy.coords[0] + directionStack[largest][0], enemy.coords[1] + directionStack[largest][1]]
            if testcase in maze or testcase in roomSet:
                if testcase != coords and testcase not in enemiesCoords:
                    confirm = testcase
        if confirm:
            confirm = [int(confirm[0]), int(confirm[1])]
            enemiesCoords.remove(enemy.coords)
            enemy.coords = confirm
            enemiesCoords.append(enemy.coords)
            enemy.rect = pygame.Rect(5 + 20 * enemy.coords[0], 5 + 20 * enemy.coords[1], 18, 18)


def playerAttack(attack):
    global health, stamina, magic, invisible, freezetime, waitingOnTP
    # Stab - FINISHED
    if attack == 0:
        for attackcoords in directionsR1:
            for enemy in enemies:
                if [coords[0] + attackcoords[0], coords[1] + attackcoords[1]] == enemy.coords:
                    enemy.health -= 5
            attackpulse[1].append(attackFlash(coords[0] + attackcoords[0], coords[1] + attackcoords[1]))
            attackpulse[0] += 5
    # Longshot - FINISHED
    elif attack == 1:
        for attackcoords in directionsR3:
            for enemy in enemies:
                if [coords[0] + attackcoords[0], coords[1] + attackcoords[1]] == enemy.coords:
                    enemy.health -= 5
            attackpulse[1].append(attackFlash(coords[0] + attackcoords[0], coords[1] + attackcoords[1]))
        for attackcoords in directionsR2:
            for enemy in enemies:
                if [coords[0] + attackcoords[0], coords[1] + attackcoords[1]] == enemy.coords:
                    enemy.health -= 5
            attackpulse[1].append(attackFlash(coords[0] + attackcoords[0], coords[1] + attackcoords[1]))
        for attackcoords in directionsR1:
            for enemy in enemies:
                if [coords[0] + attackcoords[0], coords[1] + attackcoords[1]] == enemy.coords:
                    enemy.health -= 5
            attackpulse[1].append(attackFlash(coords[0] + attackcoords[0], coords[1] + attackcoords[1]))
        attackpulse[0] += 5
        attacks[attack][3] += 4
    # Poison
    elif attack == 2:
        pass
    # Freeze
    elif attack == 3:
        pass
    # Heal - FINISHED
    elif attack == 4:
        if magic >= 5 and health < 100:
            if health <= 90:
                health += 10
                healthBar.width += 20
                magic -= 5
                magicBar.width -= 10
            elif health < 100:
                health = 100
                healthBar.width = 200
                magic -= 5
                magicBar.width -= 10
            attacks[attack][3] += 5
    # Explode - FINISHED
    elif attack == 5:
        for enemy in enemies:
            distance = math.sqrt((abs(enemy.coords[0]-coords[0]))**2 + (abs(enemy.coords[1]-coords[1]))**2)
            if distance <= 3:
                enemy.health -= 20
        health -= 10
        healthBar.width -= 20
        attacks[attack][3] += 5
    # Cultivate - FINISHED
    elif attack == 6:
        if magic >= 5 and stamina < 200:
            if stamina <= 190:
                stamina += 11
                print(stamina)
                staminaBar.width += 10
                magic -= 5
                magicBar.width -= 10
            else:
                stamina = 201
                staminaBar.width = 201
                magic -= 5
                magicBar.width -= 10
    # Time Freeze
    elif attack == 8:
        if magic >= 50:
            freezetime += 8
            magic -= 50
            magicBar.width -= 100
    # Invisibility - FINISHED
    elif attack == 9:
        if magic >= 20:
            invisible += 5
            print(invisible)
            magic -= 20
            magicBar.width -= 40
    # Teleport - FINISHEd
    elif attack == 11:
        if magic >= 25 and not waitingOnTP:
            magic -= 25
            magicBar.width -= 50
            waitingOnTP = 1
    # Armageddon - FINISHED
    elif attack == 13:
        if magic >= 60:
            # Damage everyone
            for enemy in enemies:
                enemy.health -= 20

            # Pulse
            for x in range(39):
                for y in range(29):
                    attackpulse[1].append(attackFlash(x, y))
            attackpulse[0] += 40

            # Cooldown and magic
            attacks[attack][3] += 30
            magic -= 60
            magicBar.width -= 120

    for i in attackpulse[1]:
        pygame.draw.rect(screen, (255, 255, 255), i.rect)


def enemyAttack(enemy):
    global health
    if enemy.type == 0:
        health -= 5
        healthBar.width -= 10


def initializeGrid():
    global wallSet, roomSet, rooms, roomList
    wallSet = []
    print("Initializing grid...")
    for x in range(width):
        for y in range(height):
            wallSet.append([x, y])
    roomSet = []
    rooms = 0
    roomList = []
    print(len(wallSet))


def generateRooms():
    initializeGrid()
    print("Generating rooms...")
    global wallSet, roomSet, rooms, roomList

    while rooms != roomcount:
        roomwidth = random.randint(2, 4) * 2  # Adjust the range for room width
        roomheight = random.randint(2, 4) * 2
        tempvar = 0
        startTile = [random.randint(0, (width - roomwidth / 2)) * 2, random.randint(0, (height - roomheight / 2)) * 2]
        if startTile in wallSet:
            for x in range(roomwidth + 1):
                for y in range(roomheight + 1):
                    if [startTile[0] - x + 1, startTile[1] - y + 1] in wallSet:
                        tempvar += 1
        if tempvar == (roomwidth + 1) * (roomheight + 1):
            rooms += 1
            print(f'Room {rooms} Finished!')
            for x in range(roomwidth - 1):
                for y in range(roomheight - 1):
                    wallSet.remove([startTile[0] - x, startTile[1] - y])
                    roomSet.append([startTile[0] - x, startTile[1] - y])
            roomList.append([startTile[0], startTile[1], roomwidth, roomheight])
    for i in maze:
        if i in roomSet:
            maze.remove(i)
    print(len(roomSet))


def findNeighbors(cell, range):
    neighbor = []

    directionss = [(range, 0, 'right'), (0, range, 'bottom'), (-1 * range, 0, 'left'), (0, -1 * range, 'top')]

    for dx, dy, direction in directionss:
        newcell = [cell[0] + dx, cell[1] + dy]
        if 0 <= newcell[0] < width - 1 and 0 <= newcell[1] < height - 1 and newcell in maze:
            neighbor.append([newcell[0], newcell[1], direction])
    return neighbor


def generateFrontier(cell):
    global frontier, wallSet

    for dy, dx in directionsR2:
        newcell = [cell[0] + dx, cell[1] + dy]
        if 0 <= newcell[0] < width - 1 and 0 <= newcell[1] < height - 1 and newcell in wallSet:
            wallSet.remove(newcell)
            frontier.append(newcell)


def digTunnels():
    global maze
    maze = []
    initializeGrid()
    print("Digging tunnels...")

    # get tiles
    # start = [random.choice(range(2,width-2,2)),random.choice(range(2,height-2,2))]
    start = [2, 2]
    wallSet.remove(start)
    maze.append(start)

    for dx, dy in directionsR2:
        frontier.append([start[0] + dx, start[1] + dy])
        wallSet.remove([start[0] + dx, start[1] + dy])

    while frontier != []:

        tempvar = frontier[random.randint(0, len(frontier) - 1)]
        neighbors = findNeighbors(tempvar, 2)

        e = random.choice(neighbors)

        if e[2] == 'top':
            maze.append(tempvar)
            maze.append([tempvar[0], tempvar[1] - 1])

        if e[2] == 'bottom':
            maze.append(tempvar)
            maze.append([tempvar[0], tempvar[1] + 1])

        if e[2] == 'right':
            maze.append(tempvar)
            maze.append([tempvar[0] + 1, tempvar[1]])

        if e[2] == 'left':
            maze.append(tempvar)
            maze.append([tempvar[0] - 1, tempvar[1]])

        frontier.remove(tempvar)

        # GENERATE NEW FRONTIER
        generateFrontier(tempvar)
    print(len(maze))


def getRoomPos(x, y, len, wid):
    x += random.randint(0, len)
    y += random.randint(0, wid)
    return [x, y]


def decorateRooms():
    global enemies
    global enemiesCoords
    print("Furnishing rooms...")

    # GENERATE ENEMIES
    enemies = []
    enemiesCoords = []
    for i in roomSet:
        rand = random.randint(0, len(roomSet))
        if rand >= len(roomSet) - 10:
            enemies.append(Enemy(i[0], i[1], 10, 10, 3, 0))
            enemiesCoords.append([i[0], i[1]])


def mouseCheck():
    global mousecoords, mouseover, mouseover1
    x, y = pygame.mouse.get_pos()
    x -= 5
    x /= 20
    y -= 5
    y /= 20
    mousecoords = [math.floor(x), math.floor(y)]

    for enemy in enemies:
        mouseover1 = ''
        if mousecoords == coords:
            mouseover = "You"
        elif mousecoords == enemy.coords:
            mouseover = "Bad Guy"
            mouseover1 = f'HP: {enemy.health}'
            break
        elif mousecoords in roomSet:
            mouseover = "Room"
        elif mousecoords in maze:
            mouseover = 'Tunnel'
        else:
            mouseover = ''
    mouseover = f'{mousecoords}'


def drawDungeon():
    screen.fill((0, 0, 0))  # Clear the surface
    for i in maze:
        pygame.draw.rect(screen, (255, 255, 255), (5 + i[0] * 20, 5 + i[1] * 20, 18, 18))
    for i in roomSet:
        pygame.draw.rect(screen, (200, 200, 255), (5 + i[0] * 20, 5 + i[1] * 20, 18, 18))

    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0), enemy.rect)  # Red for enemies

    pygame.draw.rect(screen, (60, 215, 60) if invisible else (100, 255, 100), player)
    print(invisible)


font = pygame.font.Font(None, 20)

player = pygame.Rect(5 + 20 * coords[0], 5 + 20 * coords[1], 18, 18)
healthBar = pygame.Rect(20, 600, (health * 2), 20)
staminaBar = pygame.Rect(20, 640, stamina, 20)
magicBar = pygame.Rect(20, 680, magic * 2, 20)

# 14 TOTAL ATTACK SLOTS
attackButtons = [
    pygame.Rect(235, 605, 118, 20),
    pygame.Rect(357, 605, 118, 20),
    pygame.Rect(235, 630, 118, 20),
    pygame.Rect(357, 630, 118, 20),
    pygame.Rect(235, 655, 118, 20),
    pygame.Rect(357, 655, 118, 20),
    pygame.Rect(235, 680, 118, 20),
    pygame.Rect(357, 680, 118, 20),
    pygame.Rect(235, 705, 118, 20),
    pygame.Rect(357, 705, 118, 20),
    pygame.Rect(235, 730, 118, 20),
    pygame.Rect(357, 730, 118, 20),
    pygame.Rect(235, 755, 118, 20),
    pygame.Rect(357, 755, 118, 20)]


def drawUI():
    global font

    font = pygame.font.Font(None, 20)
    pygame.draw.rect(screen, (60, 30, 30), (20, 600, 200, 20))
    pygame.draw.rect(screen, (30, 60, 30), (20, 640, 200, 20))
    pygame.draw.rect(screen, (30, 30, 60), (20, 680, 200, 20))
    pygame.draw.rect(screen, (50, 50, 50), (20, 720, 200, 60))
    pygame.draw.rect(screen, (50, 50, 50), (230, 600, 250, 180))

    # STATUS BARS
    pygame.draw.rect(screen, (0, 150, 0), staminaBar)
    pygame.draw.rect(screen, (150, 0, 0), healthBar)
    pygame.draw.rect(screen, (0, 0, 150), magicBar)
    healthLabel = font.render(f"Health: {health}", True, (255, 255, 255))
    staminaLabel = font.render(f"Stamina: {stamina}", True, (255, 255, 255))
    magicLabel = font.render(f"Magic: {magic}", True, (255, 255, 255))
    mouseoverLabel = font.render(f"{mouseover}", True, (255, 255, 255))
    mouseover1Label = font.render(f"{mouseover1}", True, (255, 255, 255))
    screen.blit(healthLabel, (30, 603))
    screen.blit(mouseoverLabel, (30, 730))
    screen.blit(mouseover1Label, (30, 750))
    screen.blit(staminaLabel, (30, 643))
    screen.blit(magicLabel, (30, 683))

    # ATTACK BUTTONS (self-handling)
    font = pygame.font.Font('fonty.ttf', 15)
    for button in attackButtons:
        if attacks[attackButtons.index(button)][0]:
            if attacks[attackButtons.index(button)][3] == 0:
                pygame.draw.rect(screen, (90, 90, 90), button)
                buttonLabel = font.render(attacks[attackButtons.index(button)][1], True, (255, 255, 255))
                screen.blit(buttonLabel, (button.left + 3, button.top + 1))
            else:
                pygame.draw.rect(screen, (80, 80, 80), button)
                buttonLabel = font.render(f"{attacks[attackButtons.index(button)][3]} ticks", True, (255, 255, 255))
                screen.blit(buttonLabel, (button.left + 3, button.top + 1))
        else:
            pygame.draw.rect(screen, (65, 65, 65), button)


def genDungeon():
    digTunnels()
    generateRooms()
    decorateRooms()
    drawDungeon()
    print("Dungeon generated!")


genDungeon()


# HANDLE ATTACKS, STATS, MOVEMENT, ETC
def tick():
    print('tick')
    global stamina, invisible, freezetime
    # Update the position of the player rectangle based on the coordinates
    player.topleft = (5 + 20 * coords[0], 5 + 20 * coords[1])
    enemiestoremove = []
    if freezetime:
        for attack in attacks:
            if attack[3]:
                attack[3] -= 1

        for enemy in enemies:
            if enemy.health <= 0:
                enemiestoremove.append(enemy)
        for i in enemiestoremove:
            enemies.remove(i)
            enemiesCoords.remove(i.coords)
        freezetime -= 1
    else:
        stamina -= 1
        staminaBar.width -= 1
        # Update Stamina

        # Attack cooldown reduction
        for attack in attacks:
            if attack[3]:
                attack[3] -= 1

        # ENEMY MOVEMENT HANDLING
        if invisible:
            invisible -= 1
            for enemy in enemies:
                enemyWander(enemy)
        else:
            for enemy in enemies:
                if enemy.health <= 0:
                    enemiestoremove.append(enemy)
                else:
                    distanceX = abs(enemy.coords[0] - coords[0])
                    distanceY = abs(enemy.coords[1] - coords[1])
                    if distanceY <= enemy.range and distanceX <= enemy.range:
                        enemyTracking(enemy)
                    else:
                        enemyWander(enemy)
                    distanceX = abs(enemy.coords[0] - coords[0])
                    distanceY = abs(enemy.coords[1] - coords[1])
                    if distanceY + distanceX == 1:
                        enemyAttack(enemy)
            for i in enemiestoremove:
                enemies.remove(i)
                enemiesCoords.remove(i.coords)
    drawDungeon()


def handlekeys():
    key = pygame.key.get_pressed()
    movements = {'a': (-1, 0), 'd': (1, 0), 'w': (0, -1), 's': (0, 1), 'LEFT': (-1, 0), 'RIGHT': (1, 0), 'UP': (0, -1),
                 'DOWN': (0, 1)}

    for k, (dx, dy) in movements.items():
        if key[pygame.key.key_code(k)] and (
                [coords[0] + dx, coords[1] + dy] in maze or [coords[0] + dx, coords[1] + dy] in roomSet) and not waitingOnTP:
            if [coords[0] + dx, coords[1] + dy] not in enemiesCoords:
                coords[0] += dx
                coords[1] += dy
                tick()


# HANDLE ATTACK BUTTON CLICKS
def attackClick():
    global waitingOnTP, coords
    if waitingOnTP:
        if mousecoords[0] < 39 and mousecoords[1] < 29 and mousecoords != [38,28]:
            coords = mousecoords
            pygame.draw.rect(screen, (60, 215, 60) if invisible else (100, 255, 100), player)
            waitingOnTP = 0
            tick()
        else:
            for button, attack in zip(attackButtons, attacks):
                if attack[0] and button.collidepoint(pygame.mouse.get_pos()) and not attack[3]:
                    playerAttack(attacks.index(attack))
                    tick()
    else:
        for button, attack in zip(attackButtons, attacks):
            if attack[0] and button.collidepoint(pygame.mouse.get_pos()) and not attack[3]:
                if magic >= attack[4]:
                    playerAttack(attacks.index(attack))
                    tick()


# GAME LOOP
running = True
while running:
    mouseCheck()
    drawUI()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            handlekeys()
        elif event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            attackClick()

    if coords == [38, 28]:
        coords = [0, 0]
        player.top = 5
        player.left = 5
        genDungeon()

    # ATTACK FLASH HANDLING
    if attackpulse[0] > 1:
        for i in attackpulse[1]:
            pygame.draw.rect(screen, (255, 255, 255), i)
        attackpulse[0] -= 1
    elif attackpulse[0] == 1:
        for i in attackpulse[1][:]:
            attackpulse[1].remove(i)
        attackpulse[0] -= 1
        drawDungeon()

    pygame.display.flip()
pygame.quit()

