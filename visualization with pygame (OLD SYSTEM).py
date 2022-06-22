import numpy as np
import time
import pygame
import random
from perlin_noise import PerlinNoise

##color values
Color_BG=(60,60,60)
Color_Grid = (90,90,90)
#Color_Die_Next =(150,50,50) #color of cells that die the next generation  
Color_alive_next =(175,75,75) # color of cells that turn alive next generation
Color_immune = (100,160,160) #color of immune cells at max immunity
Color_dead = (5,5,5)
Color_text = (50,255,50)
Color_incub = (190,120,120) #color of incubating cell
Color_swap = (80,175,105)
useGrid = False      #Toggle grid display

defaultNumSteps = -1
skipInput = True #This is here because I was tired of having to type the step number every time

###______________________________________________________________________________________________________________________________________________________________________________________________________________________
###SIMULATION VARIABLES: Change these to tweak infection probabilities and initial conditions                                     
##ppi_chance = 0.034                   #chance that each infected neighbor adds to a cell's probability of infection EACH STEP. 1 = 100%. Directly controls infection rate.
##infection_range = 1                 #number of cells away that a cell can be infected. Must be an integer. If you're unsure what to set this, make it 1.
##infection_length = 10               #number of steps that an infection lasts, on average                                                  
##infection_dev = 4                   #std. deviation in number of steps an infection lasts                                                  
##death_chance = 0.01                 #chance that an infected cell dies after infection.
##incub_length = 7                    #incubation time before disease is contagious.
##incub_dev = 5                       #std. deviation in number of steps incubation lasts
###immunity_strength = 0.90           #Strength of immunity, 1 means impossible to reinfect. [Currently redundant.]
##immunization_chance = 0             #Chance that a random uninfected cell will immunize itself (analagous to vaccine availability)  
##immune_mean = 0                  #mean strength of assigned immunization
##immune_dev = 0                   #std. deviation in number of steps immunization lasts
##immune_fade = 0.000625                  #amount(as a % of maximum immunity(1), not current immunity) that immunity fades by each step. 0 means permanent immunity
##immunity_disp_thresh = 0.5          #Threshold of immunity above which the counter text considers a cell to be "immune". Only affects counter text.
##susceptibility_effect = 2           #controls influence of the susceptibility matrix. 0 = no effect.
migration_chance = 0.001
###______________________________________________________________________________________________________________________________________________________________________________________________________________________
page = 0
ppi_chance = 0.0218                   
infection_range = 1                
infection_length = 8               
infection_dev = 3                   
death_chance = 0.0002                
incub_length = 2                   
incub_dev = 1                      
immunization_chance = 0.0001928            
immune_mean = 0.77                  
immune_dev = 0.01                   
immune_fade = 0.000625

immunity_disp_thresh = 0.5          
susceptibility_effect = 3
timesteps = 730
infectedstart = 1

def infect (row, col, return_matrix, noise): #infects a target cell using the infection counter and updates it to the return matrix  (normally, one of the progress matrices)
    return_matrix[row,col] = round(random.gauss(infection_length, infection_dev)) #decides how long the infection lasts, adds to progress matrix. Gaussian distribution.
    pass


def immunize (row, col, return_matrix): #immunizes a target cell using the immunization counter and updates it to the return matrix (normally, one of the progress matrices)
    return_matrix[row,col] = random.gauss(immune_mean, immune_dev) #decides strength of initial immunization, adds to progress matrix. Gaussian distribution.
    if return_matrix[row,col] > 1:
        return_matrix[row,col] = 1
    pass


def incubate (row, col, return_matrix, noise): #incubates a target cell using the incubation counter and--y'know what, you get it by now
    return_matrix[row,col] = round(random.gauss(incub_length, incub_dev))
    pass


def update (screen, cells, size, cell_infprogress, c, noise, with_progress=False, is_running=True): # rules and stuff to update
    updated_cells = np.zeros((cells.shape[0],cells.shape[1]))
    updated_infprogress = cell_infprogress
    #goes through each cell and updates the state
    for row, col in np.ndindex(cells.shape):
        if showNoise:
            color = (2*max(0,127-noise[row,col]),2*max(0,127-noise[row,col]),2*max(0,127-noise[row,col]))
        else:
            #if cell_infprogress[row,col] > 1 and cells[row,col] == 2:
                #cell_infprogress[row,col] = 1
            alive =  0
            for irows in range(-infection_range,infection_range+1):
                for icols in range(-infection_range,infection_range+1):
                    if cells[(row+irows)%cells.shape[0], (col+icols)%cells.shape[1]]%2 == 1:
                        alive+=1
            if cells[row,col]%2 == 1:
                alive-=1
            #alive = np.sum(np.mod(cells[(row - infection_range)%cells.shape[0]: (row + 1 + infection_range)%cells.shape[0],(col - infection_range)%cells.shape[1]: (col + 1 + infection_range)%cells.shape[1]], 2)) - cells[row,col] % 2 # checks cells around the cell. The modulo operator makes sure immune cells aren't counted.
            if cells[row, col] == 0:
                color = Color_BG
            elif cells[row, col] == 2:#nightmare equation sets the color for the cell based on immunity
                color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
            elif cells[row, col] == 4: #death state is 4 because making it 3 would screw up the modulo. The 'alive' counter will only count ones with odd numbers.
                color = Color_dead #Note: words alive/dead frequently interchangeable with infected/uninfected. Should fix that sometime for clarity.
            elif cells[row,col] == 6:
                color = Color_incub
            else:
                color = Color_alive_next
            if cells [row,col] == 1: #if the cell is infected do the following
                if cell_infprogress[row, col] == 0:
                    if random.random() > death_chance:
                        updated_cells[row,col] = 2
                        immunize(row,col,updated_infprogress) #immunize it if it passes the death check
                        if with_progress:
                            color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
                    else:
                        updated_cells[row,col] = 4 #kill it if it doesn't pass death check
                        if with_progress:
                            color = Color_dead
                elif cell_infprogress[row, col] > 0: #stays infected if progress matrix still has time left
                    updated_cells[row,col] = 1
                    if is_running:
                        updated_infprogress[row,col]-=1
                    if with_progress: 
                        color = Color_alive_next

            elif cells[row,col] == 0: # if cell is uninfected do the following
                if random.random() <= (10**(susceptibility_effect*(((255-noise[row,col])/255)-0.5)))*alive*ppi_chance:#higher number of active neighbors = higher chance of infection
                    updated_cells[row,col] = 6                                                                      #Also adds the effect of the susceptibility array
                    incubate(row, col, updated_infprogress, noise) #incubates cell to infprogress matrix
                    if with_progress:
                        color= Color_incub
                else:
                    if random.random() < immunization_chance:
                        updated_cells[row, col] = 2
                        immunize(row,col,updated_infprogress)
                        if with_progress:#same horrible equation
                            color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))

            elif cells[row,col] == 2: #if cell is immune do the following
                if random.random() <= (1-cell_infprogress[row,col]) * alive * ppi_chance: #small chance that immunized cells can be reinfected
                    updated_cells[row,col] = 6
                    incubate(row, col, updated_infprogress, noise) #infects cell to infprogress matrix
                    if with_progress:
                        color= Color_incub
                else:
                    updated_cells[row,col] = 2
                    if cell_infprogress[row,col] > 0:
                        if is_running:
                            updated_infprogress[row,col]-=immune_fade #fade immunity
                            if updated_infprogress[row,col] >1:
                                updated_infprogress[row,col] = updated_infprogress[row,col]%1 #This line fixes a large bug but causes an insane impact to runtime. I have no idea why.
                        if with_progress:
                            color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
                    else:
                        updated_infprogress[row,col] = 0
                if updated_infprogress[row,col] > 1 and cells[row,col]:
                    if updated_cells[row,col] ==2:
                        print()
                        print(cell_infprogress[row,col])
                        print(updated_infprogress[row,col])
            elif cells[row,col] == 6:
                if cell_infprogress[row,col] > 0:
                        updated_cells[row,col] = 6
                        if is_running:
                            updated_infprogress[row,col]-=1
                        if with_progress:
                            color= Color_incub
                else:
                    updated_cells[row,col] = 1
                    infect(row, col, updated_infprogress, noise)
                    color = Color_alive_next
            else:
                updated_cells[row,col] = 4 #Dead cells stay dead. Also, deals with any weird values that might somehow pop up in the array by killing them.
                if with_progress:
                    color = Color_dead
             
            if cells[row,col] != 4 and random.random() < migration_chance: #check for migration
                migrow,migcol = random.randint(0,cells.shape[0]-1),random.randint(0,cells.shape[1]-1) #pick random cell
                celltemp = updated_cells[row,col]
                progtemp = updated_infprogress[row,col]
                updated_cells[row,col] = updated_cells[migrow,migcol]
                updated_cells[migrow,migcol] = celltemp #swap cell states
                updated_infprogress[row,col] = updated_infprogress[migrow,migcol]
                updated_infprogress[migrow,migcol] = progtemp
                pygame.draw.aaline(screen, Color_swap, (row*size,col*size), (migrow*size,migcol*size))


                
        
        try:
            pygame.draw.rect(screen,color,(col*size,row*size, size-int(useGrid), size-int(useGrid)))
        except:         # makes a grid the size of a matrix
            pass
            print("Noise value at "+str([row,col])+": "+str(noise[row,col]))
            print(color)
            print(min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
            print(cell_infprogress[row,col])
            print(cells[row,col])
                
    w, h = pygame.display.get_surface().get_size()
    text_inf = pygame.font.SysFont(None, 30).render("Infected: "+str(np.count_nonzero(cells == 1)).center(6), True, Color_text) #all of this displays text counter
    text_inf_rect = text_inf.get_rect(center=(round(w*0.9), round(h*0.06)))

    # calculating number of immune cells larger than the threshold to display
    n_of_imm = 0
    for row, col in np.ndindex(cells.shape):
        if cells[row, col] == 2 and cell_infprogress[row, col] >= immunity_disp_thresh:
            n_of_imm += 1

    text_imm = pygame.font.SysFont(None, 30).render("Immune:     " + str(n_of_imm).center(6), True, Color_text)
    text_imm_rect = text_imm.get_rect(center=(round(w*0.9), round(h*0.09)))
    #text_imm = pygame.font.SysFont(None, 30).render("Immune:   "+str(np.count_nonzero(cell_infprogress >= immunity_disp_thresh)).center(6), True, Color_text) #the w and h scalars are positions as % across the screen
    text_dead = pygame.font.SysFont(None, 30).render("Dead:     "+str(np.count_nonzero(cells == 4)).center(6), True, Color_text)
    text_dead_rect = text_dead.get_rect(center=(round(w*0.9), round(h*0.12)))
    text_c = pygame.font.SysFont(None, 30).render("Step:     "+str(c).center(6), True, Color_text) 
    text_c_rect = text_c.get_rect(center=(round(w*0.1), round(h*0.94)))
    if not showNoise:
        screen.blit(text_inf, text_inf_rect)
        screen.blit(text_c, text_c_rect)
        screen.blit(text_inf, text_inf_rect) #draws all the text to the screen
        screen.blit(text_imm, text_imm_rect)
        screen.blit(text_dead, text_dead_rect)
    return updated_cells,updated_infprogress

def normalize(array):
    norm_array = []
    diff_array = np.max(array) - np.min(array)    
    for i in array:
        temp = (((i - np.min(array))*255)/diff_array)
        norm_array.append(temp)
    return norm_array

def main ():
    random.seed()
    seed = random.random()
    noise1 = PerlinNoise(octaves = 4, seed = seed)
    noise2 = PerlinNoise(octaves = 8, seed = seed)
    noise3 = PerlinNoise(octaves = 16, seed = seed)
    noise4 = PerlinNoise(octaves = 32, seed = seed)
    
    pygame.init() # initiates the visual part
    height= 1200 # some
    width = 800 # variables to determine size of our field
    size= 10
    h= int(height/size)
    w= int(width/size)
    screen = pygame.display.set_mode((height,width))

    global showNoise
    showNoise = False
    noiseList= []
    for i in range(w):
        row = []
        for j in range(h):
            noise_val = noise1([i/w, j/h])
            noise_val += 0.5 * noise2([i/w, j/h])
            noise_val += 0.25 * noise3([i/w, j/h])
            noise_val += 0.125 * noise4([i/w, j/h])

            row.append(noise_val)
        noiseList.append(row)
    noiseArray = np.array(normalize(np.array(noiseList)))
    cells = np.zeros((w,h))
    cell_infprogress = np.zeros((w,h)) #adds new array to track cell sub-state, meaning progress of the infection and strength of immunization.
    c=0 #counter to keep track of at what step we are
    #noiseArray = np.array([[noise([i/h, j/w]) for j in range(h)] for i in range(w)])
    screen.fill(Color_Grid)
    update(screen,cells,size, cell_infprogress, c, noiseArray)

    gridWidth = 1
    running = False
  
    pygame.display.update()
    #function to make a matrix with specific numbers of cells alive at random locations
    def start_with_x (num_inf,num_imm = 0):
        REPLACE_COUNT_INF = int(num_inf)
        REPLACE_COUNT_IMM = int(num_imm)
        REPLACE_WITH_INF = 1
        REPLACE_WITH_IMM = 1
        cells = np.zeros((w,h))
        cell_infprogress = np.zeros((w,h))
        cells.flat[np.random.choice((h*w), REPLACE_COUNT_INF, replace=False)] = REPLACE_WITH_INF #randomly assigns cells to be 1
        if num_imm > 0:
            cells.flat[np.random.choice((h*w), REPLACE_COUNT_IMM, replace=False)] = REPLACE_WITH_IMM #randomly assigns cells to be 2 if num_imm is defined
            for row,col in np.ndindex(cells.shape):
                if cells[row,col] == 2:
                    immunize(row,col,cell_infprogress)
        for row, col in np.ndindex(cells.shape):
            if cells[row,col] == 1:
                infect(row, col, cell_infprogress, noiseArray)
        return cells,cell_infprogress
    
    # the following allows us only let the game go on for a specific amount of time
    if not skipInput:
        print ("please enter the number of timesteps")
        timesteps= int(input())
    else:
        timesteps=defaultNumSteps
        x=timesteps
    running = False
    cells = np.zeros((w,h))                 #This is clearly redundant, but for some reason it prevents the program from trying to run while you assign cells.
    cell_infprogress = np.zeros((w,h))
    
    
    #game initiating loop
    while True:
        
        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT: #makes us able to close the game
                pygame.quit()
                return
           #pauses when pressing space, continues when pressing it again
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = not running
                    update (screen, cells, size, cell_infprogress, c, noiseArray)
                    pygame.display.update()
                    if running == True:
                        print("Beginning with " +str(np.count_nonzero(cells == 1))+" infected cells, "+str(np.count_nonzero(cells == 2))+" immune cells, and "+str(np.count_nonzero(cells == 4))+" dead cells.")
                        print ("running.") #Above statement prints current population
                    elif running == False:
                        print ("paused.")
                elif event.key == pygame.K_ESCAPE: #resets matrix and fills random spots with one, when pressing esc
                    running = False
                    x = timesteps
                    c = 0
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        cells = np.random.choice([2,1,0], w*h, p=[0.05, 0.15, 0.8]).reshape(w, h)#when pressing shift, 15% chance for cell to be active and 5% chance for immunized
                        for row, col in np.ndindex(cells.shape):
                            if cells[row,col] == 2:
                                immunize(row,col,cell_infprogress)
                    else:
                        cells = np.random.choice([1,0], w*h, p=[0.15, 1-0.15]).reshape(w, h)# chance for a field to be alive is 15%
                    for row, col in np.ndindex(cells.shape):
                        if cells[row,col] == 1:
                            infect(row, col, cell_infprogress, noiseArray)
                    update (screen, cells, size, cell_infprogress, c, noiseArray)
                    pygame.display.update()
                    print("reset random start")
                elif event.key == pygame.K_q: #toggle susceptibility view
                    running = False
                    showNoise = not showNoise
                    update (screen,cells,size,cell_infprogress, c, noiseArray)
                    pygame.display.update()
                elif event.key == pygame.K_r: #resets whole matrix to 0(dead) when pressing R
                    running = False
                    c=0
                    x= timesteps
                    cells = np.zeros((w,h))
                    cell_infprogress = np.zeros((w,h))
                    update(screen, cells, size, cell_infprogress, c, noiseArray)
                    pygame.display.update()
                    print("cleared field")
                if event.key == pygame.K_w:#random start with 500 cells alive
                    running = False
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]: #pressing shift will do this but also randomly immunize 500 cells
                        cells, cell_infprogress = start_with_x(500,500)
                    else:
                        cells, cell_infprogress = start_with_x(10)
                    update (screen, cells, size, cell_infprogress, c, noiseArray)
                    pygame.display.update()  
                    print("random start with x")


               #manual cell assignment 
            if pygame.mouse.get_pressed()[0]:
                keys = pygame.key.get_pressed()
                pos = pygame.mouse.get_pos()
                if keys[pygame.K_LSHIFT]:   #Shift-left-click makes a cell immune
                    cells [pos[1]//size,pos[0]//size]=2
                    immunize(pos[1]//size,pos[0]//size,cell_infprogress, noiseArray)
                    update (screen,cells,size,cell_infprogress, c, noiseArray, False, False)
                    pygame.display.update()
                    
                elif keys[pygame.K_LCTRL]:     #Control-left-click kills a cell
                    cells [pos[1]//size,pos[0]//size]=4
                    cell_infprogress[pos[1]//size,pos[0]//size]=0
                    update (screen,cells,size,cell_infprogress, c, noiseArray, False, False)
                    pygame.display.update()
                else:   #Regular left click infects a cell
                    cells [pos[1]//size,pos[0]//size]=1
                    infect(pos[1]//size,pos[0]//size,cell_infprogress, noiseArray)
                    update (screen,cells,size,cell_infprogress, c, noiseArray, False, False)
                    pygame.display.update()
            if pygame.mouse.get_pressed()[2]:   #Right click returns a cell to normal. 
                pos = pygame.mouse.get_pos()
                cells [pos[1]//size,pos[0]//size]=0
                cell_infprogress[pos[1]//size,pos[0]//size]=0
                update (screen,cells,size,cell_infprogress, c, noiseArray, False, False)
                pygame.display.update()

        if np.count_nonzero(cells == 1)+np.count_nonzero(cells == 6)==0 and c > 1:
            x = 0
            print("There are no more infected cells.")
        screen.fill(Color_Grid)
        if running and x!=0:
            x -= 1
            c+=1 #counter to keep track of at what step we are
            #check = 0
            #for row, col in np.ndindex(cells.shape):
                #if cells[row,col] == 2 and cell_infprogress[row,col] > 1:
                    #check +=1
            #print()
            #print(check)    
            cells, cell_infprogress = update(screen, cells,size, cell_infprogress, c, noiseArray, with_progress=True)
            #check = 0
            #for row, col in np.ndindex(cells.shape):
                #if cells[row,col] == 2 and cell_infprogress[row,col] > 1:
                    #check +=1
            #print(check)
            #print()
            pygame.display.update()
        #once all timesteps done it stops so you can look at the end
        elif x == 0:
            running = False
            update (screen, cells, size, cell_infprogress, c, noiseArray, with_progress=True)
            pygame.display.update()
            if c == timesteps: 
                print(" total timesteps done:", c)
            elif c > timesteps:
                print ("another "+ str(timesteps) + " timesteps done")
                print(" total timesteps done:", c)
            print("stopped.")
            #loop to "stop" the thing to look at current state after time steps
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: #press space to start
                        running = not running
                        update (screen, cells, size, cell_infprogress, c, noiseArray)
                        pygame.display.update()
                        x = timesteps
                        if running == True:
                            print ("running.")
                        elif running == False:
                            print ("paused.")
                            break
                    if event.key == pygame.K_r: #press R to clear field
                        running = False
                        c=0
                        x= timesteps
                        cells = np.zeros((w,h))
                        cell_infprogress = np.zeros((w,h))
                        update (screen, cells, size, cell_infprogress, c, noiseArray)
                        pygame.display.update()
                        print ("cleared field")
                        break
            continue
        
                    
            

        #time.sleep(0.05)
       
if __name__== '__main__':
    main()
