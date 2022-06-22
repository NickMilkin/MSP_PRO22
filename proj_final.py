import pygsheets
#from matplotlib import pyplot
#from matplotlib.animation import FuncAnimation
import numpy as np
from numpy import newaxis
import random
from perlin_noise import PerlinNoise
import pandas as pd
from timeit import default_timer, timeit

#google sheets variables
file_id = '1w17xSO4v-7WH8LX8_0yLnUSIUMR07nOET6M6n80ZiEw' #IMPORTANT! selects file to edit. This is part of the URL of the file.
client = pygsheets.authorize(service_account_file='automaton-project-fcd38a1fd1bf.json') #google sheets authorization JSON name and location. You need to download this from github and it has to be in the same directory as this program.
sheet = client.open_by_key(file_id) #opens file 
page = 0 #sets working page number. IMPORTANT! Set to 0 for ebola, 1 for flu, 2 for covid, 3 for H1N1.

# color values
Color_BG=(60, 60, 60)
Color_Grid = (90, 90, 90)
# Color_Die_Next =(150, 50, 50)     # color of cells that die the next generation
Color_alive_next = (175, 75, 75)    # color of cells that turn alive next generation
Color_immune = (100, 160, 160)      # color of immune cells at max immunity
Color_dead = (5, 5, 5)
Color_text = (50, 255, 50)
Color_incub = (190, 120, 120)       # color of incubating cell
useGrid = False                     # Toggle grid display

defaultNumSteps = 1000
skipInput = True                    # This is here because I was tired of having to type the step number every time
w = 20
h = 20
p = 0.001
timesteps = 10  # int(input())
simulationnr = 5
infectedstart = 49

# _____________________________________________________________________________________________________________________
# # SIMULATION VARIABLES: Change these to tweak infection probabilities and initial conditions
ppi_chance = 0.02                   # chance that each infected neighbor adds to a cell's probability of infection EACH STEP. 1 = 100%. Directly controls infection rate.
infection_range = 1                 # number of cells away that a cell can be infected. Must be an integer. If you're unsure what to set this, make it 1.
infection_length = 20               # number of steps that an infection lasts, on average
infection_dev = 3                   # std. deviation in number of steps an infection lasts
death_chance = 0.01                 # chance that an infected cell dies after infection.
incub_length = 3                    # incubation time before disease is contagious.
incub_dev = 1                       # std. deviation in number of steps incubation lasts
# immunity_strength = 0.90          # Strength of immunity, 1 means impossible to reinfect. [Currently redundant.]
immunization_chance = 0             # Chance that a random uninfected cell will immunize itself (analagous to vaccine availability)
immune_mean = 0.90                  # mean strength of assigned immunization
immune_dev = 0.05                   # std. deviation in number of steps immunization lasts
immune_fade = 0.02                  # amount(as a % of maximum immunity(1), not current immunity) that immunity fades by each step. 0 means permanent immunity
immunity_disp_thresh = 0.5          # Threshold of immunity above which the counter text considers a cell to be "immune". Only affects counter text.
susceptibility_effect = 3           # controls influence of the susceptibility matrix. 0 = no effect.
# ______________________________
#PRESETS
inp = input("Select a preset. Type '1' for ebola, '2' for influenza, '3' for COVID-19, and '4' for H1N1. Other answers will default to current custom parameters.\n>>>")
if inp == '1':
    page = 0
    ppi_chance = 0.0257                   
    infection_range = 1                
    infection_length = 9               
    infection_dev = 5                   
    death_chance = 0.64                 
    incub_length = 9                   
    incub_dev = 6                      
    immunization_chance = 0            
    immune_mean = 0.95                  
    immune_dev = 0.05                   
    immune_fade = 0.000249                 
    immunity_disp_thresh = 0.5          
    susceptibility_effect = 3
    timesteps = 730
    w = 474
    h = 474 #Each cell = 10 people
    infectedstart = 1
    print('Parameters for ebola initialized.')
elif inp == '2':
    page = 1
    ppi_chance = 0.0268                   
    infection_range = 1                
    infection_length =   7             
    infection_dev = 1                   
    death_chance = 0.000958                 
    incub_length = 2                   
    incub_dev = 2                      
    immunization_chance = 0.0001            
    immune_mean = 0.70                  
    immune_dev = 0.01                   
    immune_fade = 0.00538                  
    immunity_disp_thresh = 0.5          
    susceptibility_effect = 3
    timesteps = 730
    w = 226
    h = 226 #Each cell = 100 people
    infectedstart = 1
    print('Parameters for influenza initialized.')
elif inp == '3':
    page = 2
    ppi_chance = 0.0 336                  
    infection_range = 1                
    infection_length = 10               
    infection_dev =  4                  
    death_chance = 0.02                 
    incub_length = 7                   
    incub_dev = 5                      
    immunization_chance = 0.00115            
    immune_mean = 0.945                  
    immune_dev = 0.004                   
    immune_fade = 0.000625                  
    immunity_disp_thresh = 0.5          
    susceptibility_effect = 3
    timesteps = 730
    w = 381
    h = 381 #Each cell = 100 people
    infectedstart = 1
    print('Parameters for COVID-19 initialized.')
elif inp == '4':
    page = 3
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
    w = 175
    h = 175 #Each cell = 100 people
    infectedstart = 2
    print('Parameters for H1N1 initialized.')
else:
    page=5
    print('Custom parameters initialized.')



# this is a decorator to measure time taken for a function to execute
def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = default_timer()
        result = func(*args, **kwargs)
        print(f'{func.__name__} function just took {round(default_timer() - start_time, 6)} sec to execute')
        return result
    return wrapper


# infects a target cell using the infection counter and updates it to the return matrix  (normally, one of the progress matrices)
def infect(row, col, return_matrix, noise):
    return_matrix[row, col] = round(random.gauss(infection_length, infection_dev))
    # decides how long the infection lasts, adds to progress matrix. Gaussian distribution.
    pass


# immunizes a target cell using the immunization counter and updates it to the return matrix (normally, one of the progress matrices)
def immunize(row, col, return_matrix):
    return_matrix[row, col] = round(random.gauss(immune_mean, immune_dev))
    # decides strength of initial immunization, adds to progress matrix. Gaussian distribution.
    pass


# incubates a target cell using the incubation counter and--y'know what, you get it by now
def incubate(row, col, return_matrix, noise):
    return_matrix[row,col] = round(random.gauss(incub_length, incub_dev))
    pass


@time_it  # decorate any function in this way to print out its time to execute
def update(cells, cell_infprogress, noise, is_running=1, show_noise=0):
    
    updated_cells = np.zeros((cells.shape[0], cells.shape[1]))
    updated_infprogress = cell_infprogress
    for row, col in np.ndindex(cells.shape):
        if show_noise:
            print()
        else:
            alive =  0
            for irows in range(-infection_range,infection_range+1):
                for icols in range(-infection_range,infection_range+1):
                    if cells[(row+irows)%cells.shape[0], (col+icols)%cells.shape[1]]%2 == 1:
                        alive+=1
            if cells[row,col]%2 == 1:
                alive-=1
            #alive = np.sum(np.mod(cells[row - infection_range: row + 1 + infection_range, col - infection_range: col + 1 + infection_range], 2)) - cells[row, col] % 2 # checks cells around the cell. The modulo operator makes sure immune cells aren't counted.
            if cells[row, col] == 0:
                color = Color_BG
            elif cells[row, col] == 2:      # nightmare equation sets the color for the cell based on immunity
                color= (min(Color_BG[0], Color_immune[0]) + cell_infprogress[row, col] * abs(Color_BG[0] - Color_immune[0]), min(Color_BG[1], Color_immune[1]) + cell_infprogress[row, col] * abs(Color_BG[1] - Color_immune[1]), min(Color_BG[2], Color_immune[2]) + cell_infprogress[row, col]*abs(Color_BG[2] - Color_immune[2]))
            elif cells[row, col] == 4:      # death state is 4 because making it 3 would screw up the modulo. The 'alive' counter will only count ones with odd numbers.
                color = Color_dead          # Note: words alive/dead frequently interchangeable with infected/uninfected. Should fix that sometime for clarity.
            elif cells[row,col] == 6:
                color = Color_incub
            else:
                color = Color_alive_next

            if cells[row, col] == 1:        # if the cell is infected do the following
                if cell_infprogress[row, col] == 0:
                    if random.random() > death_chance:
                        updated_cells[row, col] = 2
                        immunize(row, col, updated_infprogress)     # immunize it if it passes the death check
                        # if with_progress:
                            # color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
                    else:
                        updated_cells[row, col] = 4     # kill it if it doesn't pass death check
                        # if with_progress:
                            # color = Color_dead
                elif cell_infprogress[row, col] > 0:    # stays infected if progress matrix still has time left
                    updated_cells[row,col] = 1
                    if is_running:
                        updated_infprogress[row, col] -= 1
                    # if with_progress:
                        # color = Color_alive_next
            elif cells[row, col] == 0:                  # if cell is uninfected do the following
                if random.random() <= (10**(susceptibility_effect*(((255-noise[row,col])/255)-0.5)))*alive*ppi_chance:  # higher number of active neighbors = higher chance of infection
                    updated_cells[row,col] = 6                                                                          # Also adds the effect of the susceptibility array
                    incubate(row, col, updated_infprogress, noise)  # incubates cell to infprogress matrix
                    # if with_progress:
                       # color= Color_incub
                else:
                    if random.random() <= immunization_chance:
                        updated_cells[row, col] = 2
                        immunize(row, col, updated_infprogress)
                        # if with_progress: # same horrible equation
                            # color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
            elif cells[row, col] == 2:       # if cell is immune do the following
                if random.random() <= (1-cell_infprogress[row, col]) * alive * ppi_chance:   # small chance that immunized cells can be reinfected
                    updated_cells[row, col] = 6
                    incubate(row, col, updated_infprogress, noise)                              # infects cell to infprogress matrix
                    # if with_progress:
                        # color= Color_incub
                else:
                    updated_cells[row, col] = 2
                    if cell_infprogress[row, col] > 0:
                        if is_running:
                            updated_infprogress[row, col] -= immune_fade    # fade immunity
                            if updated_infprogress[row,col] >1:
                                updated_infprogress[row,col] = updated_infprogress[row,col]%1
                        # if with_progress:
                            # color= (min(Color_BG[0],Color_immune[0])+cell_infprogress[row,col]*abs(Color_BG[0]-Color_immune[0]),min(Color_BG[1],Color_immune[1])+cell_infprogress[row,col]*abs(Color_BG[1]-Color_immune[1]),min(Color_BG[2],Color_immune[2])+cell_infprogress[row,col]*abs(Color_BG[2]-Color_immune[2]))
                    else:
                        updated_infprogress[row, col] = 0
            elif cells[row, col] == 6:
                if cell_infprogress[row, col] > 0:
                        updated_cells[row, col] = 6
                        if is_running:
                           updated_infprogress[row, col] -= 1
                #       if with_progress:
                #           color= Color_incub
                else:
                    updated_cells[row,col] = 1
                    infect(row, col, updated_infprogress, noise)
                    # color = Color_alive_next
            else:
                updated_cells[row,col] = 4 # Dead cells stay dead. Also, deals with any weird values that might somehow pop up in the array by killing them.
                # if with_progress:
                    # color = Color_dead

    return updated_cells


# _________________________________________________________________________


@time_it
def start_with_x(x):    # function that generates a grid with specific number of infected
        REPLACE_COUNT = int(x)
        REPLACE_WITH = 1
        cells = np.zeros((w, h))
        cells.flat[np.random.choice((h*w), REPLACE_COUNT, replace=False)] = REPLACE_WITH

        return cells


@time_it
def count(array):       # counts different states

    incubated = np.count_nonzero((array == 6))  
    immune = np.count_nonzero((array == 2))
    infected = np.count_nonzero((array == 1))
    dead = np.count_nonzero((array == 4))
    susceptible = (array.shape[0] * array.shape[1]) - (incubated + immune + infected + dead)
    data = [susceptible, incubated, infected, immune, dead]

    return data


@time_it
def get_graphable_data():  # gives you this whole thing as a string
    gdata = '' 
    for i in range(arraylist.shape[2]):
        x = count(arraylist[:, :, i])
        
        gdata = gdata + str(x) + ','
    gdata = gdata.rstrip(gdata[-1])  # gets rid of the last , in the string
    return gdata 


@time_it
def get_graphable_data_array(array):  # gives you this whole thing as a string
    gdata = np.array([])
    # gdata = gdata[:,newaxis]
    
    for i in range(array.shape[2]):
        x = np.array(count(arraylist[:, :, i]))
        # x = x[:,newaxis]
        gdata = np.append(gdata, x)

    gdata = gdata.reshape((array.shape[2], 5))
    return gdata


@time_it
def x_values(matrix, i): # function takes a column of matrix and turns it into list
    xlist = matrix[:, i]
    return xlist.flatten()


@time_it
def average_value (array, timestep, state): # gives you the array with averaged values
    value = 0
    for numbers_of_simulation in range(1, simc):
        value += array[numbers_of_simulation, timestep, state]
    value /= (simc-1)
    return value
    

# _____________________________________________________________________


@time_it
def normalize(array):
    norm_array = []
    diff_array = np.max(array) - np.min(array)    
    for i in array:
        temp = (((i - np.min(array)) * 255) / diff_array)
        norm_array.append(temp)
    return norm_array


random.seed()
seed = 10
noise1 = PerlinNoise(octaves=4, seed=seed)
noise2 = PerlinNoise(octaves=8, seed=seed)
noise3 = PerlinNoise(octaves=16, seed=seed)
noise4 = PerlinNoise(octaves=32, seed=seed)
np.set_printoptions(suppress=True, formatter={'all': lambda x: str(x)})  # makes values not gettinng printed in scientific notation

noiseList = []

for i in range(w):
    row = []
    for j in range(h):
        noise_val = noise1([i / w, j / h])
        noise_val += 0.5 * noise2([i / w, j / h])
        noise_val += 0.25 * noise3([i / w, j / h])
        noise_val += 0.125 * noise4([i / w, j / h])

        row.append(noise_val)
    noiseList.append(row)

noiseArray = np.array(normalize(np.array(noiseList)))

print('enter number of timesteps')

simc = 1




while simulationnr > 0:
    print("Simulation #"+str(simc) + " running", end="\r")
    # cells = np.random.choice([1,0], h*w, p=[p, 1-p]).reshape(w, h)
    cells = start_with_x(infectedstart)
    cell_infprogress = np.zeros((w, h))
    arraylist = cells[:, :, newaxis]
    datalist = count(cells)
    n_1 = cells
    c = 0
    ts = timesteps
    while ts > 0:
        n_1 = update(n_1, cell_infprogress, noiseArray)
        d = n_1[:, :, newaxis]
        arraylist = np.concatenate((arraylist, d), 2)
        ts -= 1
        print ("Simulation #" + str(simc) + " running step: " + str(c+1))
        c += 1
    print ("saving...")
    Graph = np.array([get_graphable_data_array(arraylist)])
    sheet[page].refresh() #refreshes sheet to minimize overwrite chance
    sheet[page].append_table(Graph[0,:,:].tolist(), start='A2', end=None, dimension='ROWS', overwrite=False,)
    print ("saved to page "+str(page)+" of file \'"+ sheet.title+"\' with id=\'"+file_id+"\'")
    
    simulationnr -= 1
    simc += 1




print ("done.")

# reminder for the columns [susceptible,incubated, infected, immune, dead]


#_______________Animation part
'''
fig, ax = pyplot.subplots()

def update(frames):
    
    pyplot.imshow(arraylist [:,:,frames])
    pyplot.pause(0.1)
    

anim = FuncAnimation(fig, update, frames=c, interval=100) 
'''
#________________________________

#_______________________________ graph plotting part
'''
Slist = x_values(final_data,0) #this gets the list of integers to graph
Inclist = x_values(final_data,1)
Inflist = x_values(final_data,2)
Imlist = x_values(final_data,3)
Dlist = x_values(final_data,4)
t = [x for x in range (c+1)] 



pyplot.plot(t,Slist, label = "Susceptible", linestyle ="-")
pyplot.plot(t,Inclist, label = "Incubated", linestyle ="-")
pyplot.plot(t,Inflist, label = "Infected", linestyle ="-")
pyplot.plot(t,Imlist, label = "Immune", linestyle ="-")
pyplot.plot(t,Dlist, label = "Dead", linestyle ="-")
pyplot.legend()
pyplot.show()
'''
