#!/usr/bin/env python

import pygame
import math
import random
import pathlib
from noiseengine import NoiseEngine1D
from vector import Vector2
  

# get the path that this script is running from
FILEPATH = str(pathlib.Path().absolute()) 
  
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
ORIGINX = SCREEN_WIDTH // 2
ORIGINY = SCREEN_HEIGHT // 2
COLOUR_BLACK = [0,0,0]
COLOUR_WHITE = [255,255,255]
COLOUR_STARS = [100,50,255]

# ======================================================================
# setup pygame
# ======================================================================

# set mixer to 512 value to stop buffering causing sound delay
# this must be called before anything else using mixer.pre_init()

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.display.set_caption("Pong 2020")
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()

# ======================================================================
# initialise sound effects
# ======================================================================

pygame.mixer.init()
sound_blip = pygame.mixer.Sound(FILEPATH + '/sounds/blip.ogg')
sound_blip2 = pygame.mixer.Sound(FILEPATH + '/sounds/blip2.ogg')
sound_score = pygame.mixer.Sound(FILEPATH + '/sounds/score.ogg')


# ======================================================================
# load images 
# ======================================================================

# pngs are saved with a black background layer in gimp with no transparency
# note - use convert() and not convert_alpha()
# instead I use set_colorkey to make black pixels transparent
# and now I can set the alpha value of each image

image_pong_title   = pygame.image.load(FILEPATH + '/png/pong_title.png').convert()
image_pong_numbers = pygame.image.load(FILEPATH + '/png/pong_numbers.png').convert()
image_pong_game    = pygame.image.load(FILEPATH + '/png/pong_game.png').convert()
image_pong_over    = pygame.image.load(FILEPATH + '/png/pong_over.png').convert()
image_pong_you     = pygame.image.load(FILEPATH + '/png/pong_you.png').convert()
image_pong_won     = pygame.image.load(FILEPATH + '/png/pong_won.png').convert()

# set the transparent colour, in my case black
image_pong_title.set_colorkey(COLOUR_BLACK)
image_pong_numbers.set_colorkey(COLOUR_BLACK)
image_pong_game.set_colorkey(COLOUR_BLACK)
image_pong_over.set_colorkey(COLOUR_BLACK)
image_pong_you.set_colorkey(COLOUR_BLACK)
image_pong_won.set_colorkey(COLOUR_BLACK)

# ======================================================================
# chop the scoreboard numbers into individual surfaces
# ======================================================================

# set the alpha value
image_pong_numbers.set_alpha(100)

# the numbers are all stored as a single image. 
# I use subsurface() to create a new image for each number
# and store them in a list for later use
image_offsets = [(0   ,0 ,110, 96),
                 (130 ,0 ,90 , 96),
                 (215 ,0 ,110, 96),
                 (340 ,0 ,110, 96),
                 (460 ,0 ,110, 96),
                 (580 ,0 ,110, 96),
                 (705 ,0 ,110, 96),
                 (825 ,0 ,110, 96),
                 (938 ,0 ,110, 96),
                 (1063,0 ,110, 96)]

image_numbers = []

for loc in image_offsets:
    img = image_pong_numbers.subsurface(loc)
    image_numbers.append(img)
    

# ======================================================================
# gamestate constants to help code readability
# ======================================================================

GAME_INTRO = 0
GAME_IN_PROGRESS = 1
GAME_OVER = 2

#=======================================================================
# some utility functions
#=======================================================================

def maprange( a, b, val):
    # map val from range a to range b
    (a1, a2), (b1, b2) = a, b
    return  b1 + ((val - a1) * (b2 - b1) / (a2 - a1)) 
        
        
def clamp(n, minn, maxn):
        
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n

#=======================================================================

# Star class

#=======================================================================

class Star():
    
    def __init__(self):
        
        self.position = Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.velocity = Vector2(0.0, 1 + random.random() * 10)
        self.size = random.randint(1,4)
        self.image = pygame.Surface([self.size, self.size])
        self.rect = self.image.get_rect()
        self.image.fill(COLOUR_STARS)

        
    def reset(self):
        
        self.position.y = 0
        self.position.x = random.randint(0, SCREEN_WIDTH)
        self.velocity.y = 1 + random.random() * 10
        
        
    def update(self):
        
        # add a little to vel each frame to make it look a bit 
        # like gravity is pulling it down like rain
        # reset() will set vel back to a baseline
        
        self.velocity.y += 0.05
        self.position.add(self.velocity)
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        
        
    def draw(self):
        
        screen.blit(self.image, self.rect)


#=======================================================================

# Starfield class

#=======================================================================

class StarField():
    
    def __init__(self):
        
        self.stars = []
        self.max_stars = 40
        
        for i in range(0, self.max_stars):
            star = Star()
            self.stars.append(star)
            
        
    def update(self):
        
        for star in self.stars:
            star.update()
            
            if star.position.y > SCREEN_HEIGHT:
                star.reset()
                
 
    def draw(self):
        
        for star in self.stars:
            star.draw()


#=======================================================================

# Player class

#=======================================================================

class Player():
    
    def __init__(self, x, y, w, h, maxspeed):
        
        self.width = w
        self.height = h
        self.maxspeedy = maxspeed
        self.maxposition_y = SCREEN_HEIGHT - self.height
        self.start_position = Vector2(x, y)
        self.position = Vector2(self.start_position.x, self.start_position.y)
        self.velocity = Vector2(0,0)
        self.acceleration = Vector2(0,0)
        self.acceleration_step = 1.5
        self.rect = pygame.Rect([self.position.x, self.position.y, self.width, self.height])
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(COLOUR_WHITE)
        
        
    def reset(self):
        
        self.position = Vector2(self.start_position.x, self.start_position.y)
        self.velocity.mult(0)
        self.acceleration.mult(0)
        
        
    def up(self):
        
        self.acceleration.y -= self.acceleration_step
        
        
    def down(self):
        
        self.acceleration.y += self.acceleration_step
        
        
    def constrain(self):
        
        # constrain movement to screen bounds
        if self.position.y < 0:
            self.position.y = 0
            self.velocity.y = 0
        elif self.position.y > self.maxposition_y:
            self.position.y = self.maxposition_y
            self.velocity.y = 0


    def update(self):
        
        self.velocity.add(self.acceleration)
        
        # limit the speed
        self.velocity.y = clamp(self.velocity.y, -self.maxspeedy, self.maxspeedy)

        # add velocity to position   
        self.position.add(self.velocity)
        # clear out the accumulated acceleration 
        self.acceleration.mult(0)
        
        self.constrain()
            
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        
    def draw(self):
        
        screen.blit(self.image, self.rect)

        


#=======================================================================

# Balltrail class

#=======================================================================

class Balltrail():
    
    def __init__(self, size):
        
        self.size = size
        self.pad = self.size // 2
        self.current_frame = 0
        self.last_frame = 0
        self.max_length = 30
        self.trail = []
        
        
    def reset(self):
        
        self.trail.clear()
        
        
    def update(self, x, y):
        
        self.current_frame += 1
        
        # record a ball position every 3 frames
        if self.current_frame - self.last_frame > 2:
            
            self.last_frame = self.current_frame
            
            if len(self.trail) > self.max_length:
                # remove the oldest item
                self.trail.pop(0)
            
            # and add the current position of the ball    
            self.trail.append( (x, y) )
        
        
    def draw(self):
        
        alpha = 0

        for r in self.trail:
            pygame.draw.rect(screen, [100, alpha, 100 + alpha], [r[0] + self.pad,r[1] + self.pad, 1 , 1])
            alpha += 2
        


#=======================================================================

# Ball class

#=======================================================================

class Ball():
    
    def __init__(self, size):
        
        self.mass = 8
        self.width = size
        self.height = size
        self.position = Vector2(SCREEN_WIDTH // 2 - self.width // 2, SCREEN_HEIGHT // 2 - self.height // 2)
        self.velocity = Vector2(-5,0)
        self.acceleration = Vector2(0,0)
        self.rect = pygame.Rect([self.position.x,self.position.y, self.width, self.height])
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(COLOUR_WHITE)
        self.balltrail = Balltrail(size)

    
    def reset(self):
        
        self.balltrail.reset()
        
        bally = random.randint(-1,1)
        ballx = 4
        
        if game.playerserve:
            ballx = -ballx
        
        self.position = Vector2(SCREEN_WIDTH // 2 - self.width // 2, SCREEN_HEIGHT // 2 - self.height // 2)
        self.velocity = Vector2(ballx,bally) 
        

    def applyForce(self, f):
        
        # make a copy to preserve the original vector values
        fcopy = f.getCopy()
        # divide the force by our mass
        fcopy.div(self.mass)
        self.acceleration.add(fcopy)

        
    def update(self):
        
        # add acceleration to velocity
        self.velocity.add(self.acceleration)
        
        # add it to our position vector and we move a bit towards target
        self.position.add(self.velocity)
        
        # important to clear out the accumulated acceleration each frame
        self.acceleration.mult(0)
        
        self.rect.x = self.position.x
        self.rect.y = self.position.y
    
        self.balltrail.update(self.position.x,self.position.y)

        
    def draw(self):
        
        self.balltrail.draw()
        screen.blit(self.image, self.rect)
        

#=======================================================================

# Arena class draws the game borders and scoreboard

#=======================================================================

class Arena():
    
    def __init__(self):
        
        self.width = 2
        self.height = SCREEN_HEIGHT
        self.position = Vector2(SCREEN_WIDTH // 2 - self.width // 2, 0)
        self.player_score_position = Vector2((SCREEN_WIDTH // 2) - 300, (SCREEN_HEIGHT // 2)-52)
        self.opponent_score_position = Vector2((SCREEN_WIDTH // 2) + 180, (SCREEN_HEIGHT // 2)-52)


        
    def update(self):
        
        pass
        
        
    def draw(self):
        
        pygame.draw.rect(screen,[100,100,100],[self.position.x,self.position.y, self.width, self.height])
        
        screen.blit(image_numbers[game.player_score % 10 ], (self.player_score_position.x, self.player_score_position.y))
        screen.blit(image_numbers[game.opponent_score % 10 ], (self.opponent_score_position.x, self.opponent_score_position.y))




#=======================================================================

# Game class 

# Handles collisions and constraints and player movement

#=======================================================================

class Game():

    def __init__(self):
        
        # player size and limits
        playerwidth = 20
        playerheight = 80
        playerspeed = 3.0
        opponentspeed = 2.8
        ballsize = 8
        player_edge_offset = 10
        
        # ball limits
        self.ball_max_speed_x = 8.0
        self.ball_max_speed_y = 8.0
        self.ball_speed_step = 1.05
        
        # these are the x positions that the ball is reset to following
        # a rectscollide with either bat to prevent ball going through bat
        self.ball_rebound_player_x = player_edge_offset + playerwidth + ballsize
        self.ball_rebound_opponent_x = SCREEN_WIDTH - (player_edge_offset + playerwidth) - ballsize
        
        self.playerserve = True # this toggles who serves
        
        self.gamestate = GAME_INTRO
        
        self.player = Player(player_edge_offset, (SCREEN_HEIGHT // 2) - playerheight // 2, playerwidth, playerheight, playerspeed)
        self.opponent = Player(SCREEN_WIDTH - (player_edge_offset + playerwidth), (SCREEN_HEIGHT // 2) - playerheight // 2, playerwidth, playerheight, opponentspeed)
        self.ball = Ball(ballsize)
        self.arena = Arena()
        self.noiseengine = NoiseEngine1D(random.randint(1,100))
        self.starfield = StarField()
        
        self.player_score = 0
        self.opponent_score = 0
        
        self.wind = Vector2(0,0)
        self.wind_strength = 0.4
        

        
    def checkcollisionBallEdges(self):
        
        # if the ball is at or past either the top or bottom edges of
        # the court, reverse the y velocity and bring its position back
        # within the bounds of the court. This 'bounces' the ball
        # back off the edges
        
        if self.ball.position.y < 0:
            
            self.ball.position.y = 0
            self.ball.velocity.y = -self.ball.velocity.y
            sound_blip2.play()
            
        elif self.ball.position.y > SCREEN_HEIGHT-self.ball.height:
            
            self.ball.position.y = SCREEN_HEIGHT-self.ball.height
            self.ball.velocity.y = -self.ball.velocity.y
            sound_blip2.play()
            
            
    def checkcollisionBats(self):
        
        # check if ball is colliding with either bat. 
        # if true reflect ball velocity x
        # use the reflectAngle function to work out how much
        # to add to the y velocity.

        if self.ball.rect.colliderect(self.player.rect):
            
            # work out where on the bat the ball hit here
            self.ball.velocity.y = self.reflectAngle(self.player)
            self.ball.velocity.x = -self.ball.velocity.x 
            
            # a fudge to stop ball penetrating bat at higher ball speeds
            self.ball.position.x = self.ball_rebound_player_x
            self.batHit()
            
        elif self.ball.rect.colliderect(self.opponent.rect):
            
            self.ball.velocity.y = self.reflectAngle(self.opponent)
            self.ball.velocity.x = -self.ball.velocity.x
            
            # a fudge to stop ball penetrating bat at higher ball speeds
            self.ball.position.x = self.ball_rebound_opponent_x
            self.batHit()

            
    def batHit(self):
        
        # called when the ball has hit either bat
        sound_blip.play()
        self.setWind()
        
        # increase the ball x velocity each hit
        # but keep it limited to x max speed
        if self.ball.velocity.x < self.ball_max_speed_x:
            self.ball.velocity.x *= self.ball_speed_step
        else:
            self.ball.velocity.x = self.ball_max_speed_x
            
        # reflectangle has already been applied so just
        # keep vel y within bounds
        if self.ball.velocity.y > self.ball_max_speed_y:
            self.ball.velocity.y = self.ball_max_speed_y

            

    def setWind(self):
        
        # gets a random direction and strength for the wind effect
        # the effect is mostly on the balls vertical movement
        # called when the ball hits a bat
        self.wind.x = self.noiseengine.next(100) * (self.wind_strength / 4)
        self.wind.y = self.noiseengine.next() * self.wind_strength
        

    def reflectAngle(self, player):
        
        # returns an y velocity to reflect the ball at. 
        # subtract paddle y pos from ball y pos to get the position that
        # the ball is on the paddle 
        # then / by player height to get a normalised 0 to 1.0 value
        # then add -0.5 to shift the range from -0.5 to 0.5 which
        # can then be multiplied to produce a y velocity for the ball
        
        return (((self.ball.position.y - player.position.y) / player.height) + -0.5) * 8
        
        
    def moveOpponent(self):
        
        # TODO:
        # Make the enemy more intelligent.
        # seek to position towards one end of bat for more angle
        
        if self.opponent.position.y < self.ball.position.y - self.opponent.height // 2:
            self.opponent.down()
            
        if self.opponent.position.y > self.ball.position.y - self.opponent.height // 2:
            self.opponent.up()
            
        
    def checkBallInScorePosition(self):
    
        # if true score and reset game
    
        if self.ball.position.x < 0:
            self.opponent_score += 1
            self.resetFromScore()
            
        if self.ball.position.x > SCREEN_WIDTH:
            self.player_score += 1
            self.resetFromScore()
            
            
    def resetFromScore(self):
        
        # called after a score has been made
        # reset the player positions and 
        # zero the wind effect and
        # toggle the server
        
        self.playerserve = not self.playerserve
    
        sound_score.play()
        self.resetPositions()
        
        # check if either player has won the game
        # and switch the gamestate to gameover if it has
        
        if self.player_score == 5 or self.opponent_score == 5:
            self.gamestate = GAME_OVER
            
    def resetFromWin(self):
        
        # called after a game win
        # resets score and positions etc
        self.player_score = 0
        self.opponent_score = 0
        self.resetPositions()
            

    def resetPositions(self):
        
        self.ball.reset()
        self.player.reset()
        self.opponent.reset()
        self.wind.mult(0)
        
        
    def switchGameState(self):
        
        if self.gamestate == GAME_INTRO:
            
            self.gamestate = GAME_IN_PROGRESS
            image_pong_title.set_alpha(75)
            
        elif self.gamestate == GAME_OVER:
            
            self.resetFromWin()
            self.gamestate = GAME_INTRO
            
            
    def drawGameOver(self):
        
        randoff1 = self.noiseengine.next()
        randoff2 = self.noiseengine.next(1000)
        jitter = 10
        
        image_pong_game.set_alpha(150 + randoff1 * 50)
        image_pong_over.set_alpha(150 + randoff2 * 50)
        
        screen.blit(image_pong_game, (200 + randoff1 * jitter, 150 + randoff2 * jitter))
        screen.blit(image_pong_over, (400 + randoff2 * jitter, 250 + randoff1 * jitter))
        
        
    def drawGameWon(self):
        
        randoff1 = self.noiseengine.next()
        randoff2 = self.noiseengine.next(1000)
        jitter = 10
        
        image_pong_you.set_alpha(100 + randoff1 * 50)
        image_pong_won.set_alpha(100 + randoff2 * 50)
        
        screen.blit(image_pong_you, (200 + randoff1 * jitter, 150 + randoff2 * jitter))
        screen.blit(image_pong_won, (400 + randoff2 * jitter, 250 + randoff1 * jitter))
        
        
    def drawGameIntro(self):
        
        randoff1 = self.noiseengine.next()
        randoff2 = self.noiseengine.next(1000)
        jitter = 10
        
        image_pong_title.set_alpha(200 + randoff1 * 50)
        
        screen.blit(image_pong_title, (200 + randoff1 * jitter, 200 + randoff2 * jitter))

        

    def draw(self):
        
        if self.gamestate == GAME_INTRO:
            
            self.starfield.update()
            self.starfield.draw()
            self.drawGameIntro()
            
        elif self.gamestate == GAME_IN_PROGRESS:
            
            self.checkcollisionBallEdges()
            self.checkcollisionBats()
            self.moveOpponent()
            self.checkBallInScorePosition()
            self.arena.update()
            self.ball.applyForce(self.wind)
            self.ball.update()
            self.player.update()
            self.opponent.update()
            self.starfield.update()
            self.starfield.draw()
            self.arena.draw()
            self.player.draw()
            self.opponent.draw()
            self.ball.draw()
            
        elif self.gamestate == GAME_OVER:
            
            self.starfield.update()
            self.starfield.draw()
            
            if self.player_score > self.opponent_score:
                self.drawGameWon()
            else:
                self.drawGameOver()


    def run(self):
        
        done = False
        
        while not done:
    
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT:  
                    done = True
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE):
                        done = True
                    elif (event.key == pygame.K_SPACE):
                        game.switchGameState()
                    elif (event.key == pygame.K_UP):
                        game.player.up()
                    elif (event.key == pygame.K_DOWN):
                        game.player.down()
                        
            screen.fill(COLOUR_BLACK)
            game.draw()
            clock.tick(60)
            pygame.display.flip()
        
        

game = Game()
game.run()
pygame.quit()
