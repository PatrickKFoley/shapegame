Shapegame
By Patrick Kye Foley

Shapegame is a simple collection and spectator-driven game born from a handful of small ideas shared with a good friend. Shapegame is created using Python's Pygame, a low-level SDL wrapper, and is essentially engineless. This allows for ground-up development, not only allowing for total control of mechanics and functionality, but also posing a larger challenge than using something "off the shelf". Currently implemented is the main game play, collection management, and friends system (more details on all implemented features bellow). 

-- GAME PLAY --
    - Shapegame's game play consists of two teams of shapes battling for control of the arena
        - I like to think of this like watching Beyblades in the school yard
    
    - Each team of shapes will consist of a pseudo-random number of shapes
        - last team with living shapes wins! 
    
    - As shapes move in straight lines around the arena, they will collide with other shapes
        - When shapes collide, they mimic elastic 2D collisions (similar to billiards on a pool table)
        - When shapes of a different team collide, one shape will deal damage to the other (see SHAPES for info on how this is determined)
    
    - Additionally, shapes will collect powerups as they move around the arena
        - Some powerups are used on pick-up, hitting another shape, or upon death (see POWERUPS for more information on all powerups)
    
    - By pressing TAB a stats screen will be shown, showcasing some stats for each shape on each team
        - Stats shown include, amount of damage dealt, taken, and healed, powerups used, and shapes killed

    - At all times a killfeed is displayed on the right hand side of the arena, as well as other information
        - Other information includes a headcount for all shapes on each team, as well as a total percent representing the health of the team as a whole
        - The killfeed displays: 
            - When a shape is killed or resurrected
            - When a shape is killed with the special help of a powerup
            - When a shape activates a powerup for it's own benefit (ie, mushroom, healing (see POWERUPS))
    
    - Game play is implemented in two areas, local match and network match
        - In a local match, a player can customize any possible combination of two shapes and watch the battle
            - Alternatively, the game can simply be simulated, presenting the outcome to the player in seconds
        - In a network match, a player can connect to another random player, or a friend directly via invitations, and battle shapes from within their own collections
    

-- SHAPES --
    - Shapes come in 5 different types, each with unique design
        - Each shape has 4 different designs to showcase their current health
    
    - On top of 5 unique designs, each shape can come in a plethora of different colors and gradients
        - Within your collection, the rarity of each shape can be seen across all players collections
    
    - Shapes behave according to the pseudo-random values of different attributes
        - These values start with a base value taken from a pre-set base shape, which then has a random (positive or negative) number added
            - On screens where the stats of a shape are shown, the variance from these base values is displayed with either a green positive number, or a red negative number
    
    - These attributes, and their functionality, are:
        - Luck
            - Luck determines which shape will deal damage and which will take damage when two opposing shapes collide
            - Both shapes roll a D20 and add their luck to their roll; highest number deals damage
        
        - Damage multiplier
            - Damage multiplier is one of the many things that affects how much damage a shape deals
            - DAMAGE DEALT ~= DAMAGE MULTIPLIER * MOMENTUM = DAMAGE MULTIPLIER * VELOCITY * MASS
                - note that mas, and therefore momentum, is determined by following attributes
        
        - Velocity
            - This is the speed that the shapes start the battle with
                - Note that for a given shape, this will change immediately after that shape collides with another
            - Given the above formula for damage dealt, a higher velocity means higher damage dealt
        
        - Density
            - This is used to determine the mass of each shape
            - Currently, a density of 1 is used in most places, and I think it will eventually be removed and be left as this default
        
        - Radius (min) and (max)
            - This range is used to determine the size of each shape on a team
            - All shapes will have a radius somewhere in this range, allowing for some variation across the team
        
        - Team size
            - Team size determines how many shapes strong your team will be

-- POWERUPS --
    - Powerups spawn at random coordinates in the arena at set time intervals
    - The shape that first collides with a powerup has that powerup added to their inventory
        - As mentioned above, some powerups are used on pick-up, hitting another shape, or upon death
    
    - A full list of powerups and their uses is as follows:
        - Insta-kill (skull and crossbones)
            - The insta-kill powerup guarantees that the holding shape will win their next collision, and kill their opponent no matter their health
        
        - Resurrect (red cross)
            - The resurrect powerup spawns a new friendly shape in two scenarios:
                - If the holding shape dies, it will be resurrected
                - If the holding shape kills and opponent, a friendly shape with the dead opponent's attributes will be resurrected
        
        - Luck Bonus (yellow star)
            - When a shape has a yellow star, it gains a +5 to luck
                - this effect is held until the shape next takes damage
        
        - Strength (white & black muscle)
            - When a shape has a strength powerup, it's damage multiplier is multiplied by 3
                - this effect is held until the shape next deals damage
        
        - Speed (running person)
            - When a shape collects a speed powerup, their speed is doubled and their damage multiplier is increased by 1.5x
                - The effect to damage multiplier is held until the shape next deals damage
        
        - Health (green cross)
            - When a shape wielding a Health powerup damages another shape, they will heal for 50% their maximum health 
        
        - Bomb
            - 3 Seconds after a bomb is collected, an explosion will damage all shapes within a circle centered on the detonating shape
                - Damage taken by other shape is determined as follows:
                    - IF shape is within 200px of center of detonating shape THEN damage taken = 200 - distance to center of detonating shape
                    - OTHERWISE damage taken = 0
            - If the detonation kills both the detonating shape as well as at least one any other shape, the detonating shape is resurrected
            - The detonation of bombs will also activate the Resurrect powerup in its normal circumstances
                - If the detonation only kills the detonating shape (which has a resurrect), the detonating shape will be resurrected
                - If the detonating shape kills the detonating shape (which has a resurrect) as well as at least one other shape, both the detonating shape and the killed shape will be resurrected (onto the detonating shape's team)
        
        - Red laser (red circle)
            - When a shape holding a Red laser damages another shape, it will unleash a red laser on the arena
                - A red laser moves in the same direction as the unleashing shape with twice it's speed
                - The laser spends 5 seconds bouncing off the walls of the arena, dealing 25 damage to any opponent shape it touches, at most once
        
        - Black laser (black circle)
            - When a shape holding a Black laser damages another shape, it will unleash 8 black lasers on the arena
                - Each black laser moves in a different cardinal or ordinal direction with a set speed
                - Each laser disappears once reaching the bounds of the arena, dealing 10 damage to any opponent shape it touches, at most once
        
        - Mushroom
            - When a shape collects a mushroom, it will temporarily increase in size, heal slightly, and gain a massive increase to damage multiplier
                - The amount healed is 100hp
                - Damage multiplier is increased by a factor of 5
                - The duration of these effects is 10 seconds

-- COLLECTION -- 
    - Each player has a collection of SHAPES
        - The COLLECTION menu is used to browse a player's shapes
        - The CREATE SHAPE menu is used to add new shapes to the player's collection (using a SHAPE TOKEN)
    
    - Each player has a favorite shape, which acts as their profile pic
        - A player's favorite shape can be changed
   
    - When playing against other players, players can choose to PLAY FOR KEEPS, in which case the winner keeps loser's shape
        - If a player's favorite shape is lost, a random shape from their collection is reassigned as their favorite
        - If a player's last shape is lost, they earn a SHAPE TOKEN

-- FOLLOWING/FOLLOWERS & NOTIFICATIONS -- 
    - From the main menu, players can see their following list and notifications inbox
        - Players can be added to and removed from this list
            - A player appears here with an icon of their current favorite shape
        - From a player's following list, they can challenge another player to a network match
            - Having this direct-matchmaking and open-matchmaking work at the same time is something I am very proud of
            - When a player is challenged to a network match, they will receive a notification where they can accept or deny the challenge


Like all eventually great things, Shapegame is a work in progress. Currently, here is my todo list.

-- TODO --
    - User experience
        - user account
            - alter username, password
            - games played record
                - win/loss ratio, win streak, num games played, num games won...
                - arch nemesis, best shape
        
        - following system
            - stop following

        - notifications system
            - add messaging?

        - information access
            - add viewing and understanding different shapes/attributes to powerup playground area
            
    - Collection experience
        - manage collection
            - scrap shapes for shape tokens
            - allow for a showcase of shapes as well as a favorite shape (for proper account viewing)

        - manage shapes
            - should players be allowed to name their shapes?

    - Shape experience
        - shape leveling system

    - Game functionality
        - bridge gap between shape objects in menu -> in game
        - rewrite entire game I guess (add detail as I go)
        - automate dependency installation
        - rewrite script responsible for shape stats

    - PER MENU BASIS -
        - Login
            - thread user retrieval pause

-- GOOD TO KNOWS --

- SERVER -
    - Connection refused: try restarting postgresql service ('service postgresql restart) 

