
import numpy as np
import time
import pygame
import random

# parameters

n_infects = 2
days_incub = 3
days_infected = 5
days_immunized = 15


#color values

Color_healthy=(255, 255, 255)
Color_Grid = (40,40,40)
Color_Die_Next =(170,170,170) #color of cells that die the next generation  
Color_alive_next =(255,255,255) # color of cells that turn alive next generation
Color_incub = (100, 100, 0)
Color_sick = (255, 0, 0)
Color_immune = (0, 0, 255)

# healthy = 0
# incubation = 1
# sick = 2
# immunized = 3

def update (screen, cells, size, with_progress=False): # rules and stuff to update
    updated_cells = np.zeros((cells.shape[0],cells.shape[1]))
    #goes through each cell and updates the state
    for row, col in np.ndindex(cells.shape):

           # if the cell is healthy
           if cells[row, col] == 0:
               color = Color_healthy

            # if the cell is in incubation
           if cells[row, col] in range(1, days_incub + 1):
               updated_cells[row, col] = cells[row, col] + 1
               color = Color_incub

            # if the cell is sick
           elif cells[row, col] in range(days_incub + 1, days_incub + days_infected + 1):
               updated_cells[row, col] = cells[row, col] + 1
               color = Color_sick
               for i in range(n_infects):
                   x = random.randint(-1, 1)
                   y = random.randint(-1, 1)
                   if updated_cells[(row + x) % cells.shape[0], (col + y) % cells.shape[1]] == 0:
                      updated_cells[(row + x) % cells.shape[0], (col + y) % cells.shape[1]] = 1

            # if the cell is immunized
           elif cells[row, col] in range(days_incub + days_infected + 1, days_incub+days_infected+days_immunized + 1):
               if cells[row, col] == days_incub + days_immunized + days_infected:
                  updated_cells[row, col] = 0
               else:
                   updated_cells[row, col] = cells[row, col] + 1
               color = Color_immune

           # if cells [row,col] == 1: #if the cell is alive do the following
           #     if alive < 2 or alive > 3: #dies when less than 2 or more than 3 are around it
           #         if with_progress:
           #             color = Color_Die_Next
           #     elif 2<= alive or alive<=3: #turns/stays alive when 2 or 3 cells around it are alive
           #          updated_cells[row,col] = 1
           #          if with_progress:
           #              color = Color_alive_next
           # else: # if cell is dead do the following
           #     if alive == 3:
           #         updated_cells[row,col] = 1
           #         if with_progress:
           #             color= Color_alive_next
           pygame.draw.rect(screen,color,(col*size,row*size, size-1, size-1)) # makes a grid the size of a matrix
    return updated_cells


def main ():
    pygame.init() # initiates the visual part
    height= 1000 # some
    width = 800 # variables to determine size of our field
    size= 10
    h= int(height/size)
    w= int(width/size)
    screen = pygame.display.set_mode((height,width))

    cells = np.zeros((w,h))
    #cells = np.random.choice([1,0], h*w, p=[0.15, 1-0.15]).reshape(w, h)
    screen.fill(Color_Grid)
    update(screen,cells,size)
    running = False
  
    pygame.display.update()
    #function to make a matrix with specific numbers of cells alive at random locations
    def start_with_x (x):
        REPLACE_COUNT = int(x)
        REPLACE_WITH = 1
        cells = np.zeros((w,h))
        cells.flat[np.random.choice((h*w), REPLACE_COUNT, replace=False)] = REPLACE_WITH
        return cells
    
    # the following allows us only let the game go on for a specific amount of time
    print ("please enter the number of timesteps")
    timesteps= int(input())
    x=timesteps
    c=0 #counter to keep track of at what step we are
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
                    update (screen, cells, size)
                    pygame.display.update()
                    if running == True:
                        print ("running.")
                    elif running == False:
                        print ("paused.")


               #when you click on a cell turns it into the opposite state
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if cells [pos[1]//size,pos[0]//size]==0:
                    cells [pos[1]//size,pos[0]//size]=1
                    update (screen,cells,size)
                    pygame.display.update()
                    
                else: 
                    cells [pos[1]//size,pos[0]//size]=0
                    update (screen,cells,size)
                    pygame.display.update()
              
            elif event.type == pygame.KEYDOWN: #resets matrix and fills random spots with one, when pressing esc 
                if event.key == pygame.K_ESCAPE:
                    running = False
                    x = timesteps
                    c = 0
                    cells = np.random.choice([1,0], w*h, p=[0.15, 1-0.15]).reshape(w, h) # chance for a field to be alive is 15%
                    update (screen, cells, size)
                    pygame.display.update()
                    print("reset random start")
                    
                elif event.type == pygame.KEYDOWN:#resets whole matrix to 0(dead) when pressing R
                    if event.key == pygame.K_r:
                        running = False
                        c=0
                        x= timesteps
                        cells = np.zeros((w,h))
                        update (screen, cells, size)
                        pygame.display.update()
                        print ("cleared field")
                        #random start with 500 cells alive
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            running = False
                            cells= start_with_x(500)
                            update (screen, cells, size)
                            pygame.display.update()
                            
                            print("random start with x")
        screen.fill(Color_Grid)
        if running and x>0:
            x -= 1
            c+=1 #counter to keep track of at what step we are
            cells= update (screen, cells,size, with_progress=True)
            pygame.display.update()
        #once all timesteps done it stops so you can look at the end
        elif x == 0:
            running = False
            update (screen, cells, size, with_progress=True)
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
                    if event.key == pygame.K_SPACE:
                        running = not running
                        update (screen, cells, size)
                        pygame.display.update()
                        x = timesteps
                        if running == True:
                            print ("running.")
                        elif running == False:
                            print ("paused.")
                            break
                    elif event.key == pygame.K_r:
                        running = False
                        c=0
                        x= timesteps
                        cells = np.zeros((w,h))
                        update (screen, cells, size)
                        pygame.display.update()
                        print ("cleared field")
                        break
            continue
        
                    
            

        time.sleep(0.2)
       
if __name__== '__main__':
    main()
