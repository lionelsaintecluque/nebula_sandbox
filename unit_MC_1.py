import math

import numpy as np
import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice.Plot.BodeDiagram import bode_diagram
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

################################################################################
#
# HELPER FUNCTIONS : 
#   for some reasons, I was not able to use numpy to compute STD DEV.
#   for some reasons (too) I failed to used the search function of spice.
#
################################################################################

def moyenne_stdev(vec):
    iterations = len(vec)
    
    moyenne = 0
    for element in vec :
        moyenne += element
    moyenne /=  iterations
    
    variance = 0
    for element in vec :
        variance += (element-moyenne)**2
    variance /=  iterations
    
    return moyenne, variance**0.5    

def search_3db (analysis, node):
    abs_serie = np.absolute(analysis[node])
    #i = np.argmin(np.absolute(np.array(abs_serie)-(2**0.5/2)))

    i = np.argmin(np.absolute(np.array(abs_serie)-target))
    
    x_f = 0
    for h in range (0,i+1):
        if (abs_serie[h] > target > abs_serie[h+1]) :
            x0, x1 = analysis.frequency[h], analysis.frequency[h+1]
            y0, y1 = abs_serie[h], abs_serie[h+1]
            x_f = x0+(x1-x0)*(target-y0)/(y1-y0)
            #print ("Found at h = ", h, "in range 0:", i)
            break
    
    return x_f
    

#Simulation parameters : 

tolerance = 1/100

#iterations = 100
#freq_steps = 10**6/10
#startf = 0.277
#stopf = 0.295

iterations = 100
freq_steps = 10**6/100
startf = 0.1
stopf = 0.5

target = (2**0.5/2)@u_V

out_node = 'out'
in_node = 'in'


################################################################################
#
# Circuit description
#
################################################################################

circuit = Circuit('elliptic filter')

serial = [18, 39, 53, 56] # nH, symetrical
parallel = [2.4, 12, 22, 22] # pF, symetrical

serial_len = len(serial)
#print (serial_len)

if len(parallel) != serial_len:
    exit(-1)

for i, val in enumerate(serial):
    in_ = in_node
    if i != 0 :
        in_ = i+1
    circuit.L(i+1, in_, i+2, val@u_nH)
    
    if i < serial_len-1 :
        out_ = out_node
        j =2*(serial_len)-i-1
        if i != 0 :
            out_ = j+1
        circuit.L(j, j, out_, val@u_nH)

for i, val in enumerate(parallel):
    in_ = in_node
    out_ = out_node
    j =2*serial_len-i
    if i != 0 :
        in_ = i+1
        out_ = j
    circuit.C(i+1, in_, 0, val@u_pF)
    circuit.C(j, out_, circuit.gnd, val@u_pF)

serial_parts = [
    circuit.L1,
    circuit.L2,
    circuit.L3,
    circuit.L4,
    circuit.L5,
    circuit.L6,
    circuit.L7,
    ]

parallel_parts = [
    circuit.C1,
    circuit.C2,
    circuit.C3,
    circuit.C4,
    circuit.C5,
    circuit.C6,
    circuit.C7,
    circuit.C8,
    ]

circuit.SinusoidalVoltageSource('input', in_node, circuit.gnd, amplitude=1@u_V)

################################################################################
#
# Simulation 
#
################################################################################
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
ngspice = simulator.ngspice

#
# Input Impedance
#

analysis = simulator.ac(start_frequency=startf@u_GHz, stop_frequency=stopf@u_GHz, number_of_points=freq_steps,  variation='dec')
imped = np.divide(analysis['in'], analysis['vinput'])

figure, axes = plt.subplots(2, figsize=(20, 10))
plt.title("Impédance d'entrée")

axes[0].loglog(analysis.frequency, np.absolute(imped), base=10, marker='.', color='blue', linestyle='-',)
axes[0].grid(True)
axes[0].grid(True, which='minor')
axes[0].set_xlabel("Frequency [Hz]")
axes[0].set_ylabel("Impedance [Ohm]")

axes[1].semilogx(analysis.frequency, np.angle(imped, deg=False), base=10, marker='.', color='blue', linestyle='-',)
axes[1].set_ylim(-math.pi, math.pi)
axes[1].grid(True)
axes[1].grid(True, which='minor')
axes[1].set_xlabel("Frequency [Hz]")
axes[1].set_ylabel("Phase [rads]")
plt.yticks((-math.pi, -math.pi/2,0, math.pi/2, math.pi),
        (r"$-\pi$", r"$-\frac{\pi}{2}$", "0", r"$\frac{\pi}{2}$", r"$\pi$"))

plt.show()


# Monte Carlo with all component affected, for two different par tolerance : 1% and 2%
cutoff_1pc = []
cutoff_1pc_values = []
cutoff_2pc = []
cutoff_2pc_values = []

#Save initial part values
l0 = []
c0 = []
for L in serial_parts:
    l0.append(L.inductance)

for C in parallel_parts:
    c0.append(C.capacitance)


for i in range(1, 5*iterations):
    
    #Simulation with 1% parts
    for L, l in zip(serial_parts, l0):
        L.inductance = np.random.normal(l.value, 1/100, 1)[0]@u_nH
    for C, c in zip(parallel_parts, c0):
        C.inductance = np.random.normal(c.value, 1/100, 1)[0]@u_pF
        
    analysis = simulator.ac(start_frequency=startf@u_GHz, stop_frequency=stopf@u_GHz, number_of_points=freq_steps,  variation='dec')
    cutoff_1pc.append(np.absolute(analysis[out_node]))
    cutoff_1pc_values.append(search_3db (analysis, out_node))

    #Simulation with 2% parts
    for L, l in zip(serial_parts, l0):
        L.inductance = np.random.normal(l.value, 2/100, 1)[0]@u_nH
    for C, c in zip(parallel_parts, c0):
        C.inductance = np.random.normal(c.value, 2/100, 1)[0]@u_pF
        
    analysis = simulator.ac(start_frequency=startf@u_GHz, stop_frequency=stopf@u_GHz, number_of_points=freq_steps,  variation='dec')
    cutoff_2pc.append(np.absolute(analysis[out_node]))
    cutoff_2pc_values.append(search_3db (analysis, out_node))
    
    # To save memory
    ngspice.destroy()

# Reset original values
for L, l in zip(serial_parts, l0):
    L.inductance = l  
for C, c in zip(parallel_parts, c0):
    C.capacitance = c

fig, ax = plt.subplots()
centre  = (279.7+279.4)/2
bin  = (279.7-279.4)/6

ax.hist([a.value/1e6 for a in cutoff_2pc_values], bins=10, linewidth=0.5, color="green", edgecolor="white")
ax.hist([a.value/1e6 for a in cutoff_1pc_values], bins=10, linewidth=0.5, color="orange", edgecolor="white")

ax.set(xlim=(centre-5*bin, centre+5*bin), xticks=np.linspace(centre-4*bin, centre+4*bin, 5),
       ylim=(0, 150), yticks=np.linspace(0, 125, 6))

plt.show()
#L0_M, L0_S = moyenne_stdev (cutoff_1pc_values)
#print("1 percent: ", L0_M, " - ", L0_S)
#L0_M, L0_S = moyenne_stdev (cutoff_2pc_values)
#print("2 percent: ", L0_M, " - ", L0_S)


#
# Individual Monte Carlo analysis (one part at a time).
#

cutoff = []
for L in serial_parts:
    l0 = L.inductance
    print (L.name, " initial value : ", l0)
    random_values = np.random.normal(l0.value, tolerance, iterations)
    cutoff_values = []
    max_gain_v = []
    max_gain_f = []
    for j in random_values:
        L.inductance = j@u_nH
        analysis = simulator.ac(start_frequency=startf@u_GHz, stop_frequency=stopf@u_GHz, number_of_points=freq_steps,  variation='dec')
        #abs_serie = np.absolute(analysis['8'])
        #series_L1.append(abs_serie)
    
        # Cutoff : 
        cutoff_values.append(search_3db (analysis, out_node))

        # Peak : 
        index_peak = np.argmax(np.absolute(analysis[out_node])[0:i])
        max_gain_v.append(np.absolute(analysis[out_node][index_peak]))
        max_gain_f.append(analysis.frequency[index_peak])
    
        #simulator.measure('ac', 'cutoff', 'WHEN V(8,gnd)=0.7', 'FALL=1')
        ngspice.destroy()
    # Revert initial value:
    #print (circuit)
    L.inductance = l0
    print ("Control (", L.name, " mean and stdev) :")
    print (np.mean(random_values))
    print (np.std (random_values))
    print ("")

    print ("Peak value (frequency span and amplitude span) :")
    print (np.min(max_gain_f), np.max(max_gain_f))
    print (np.min(max_gain_v), np.max(max_gain_v))
    print ("")

    print ("Cutoff (Span, mean, stdev) :")
    #print (cutoff_values)
    cutoff.append(cutoff_values)
    L1_M, L1_S = moyenne_stdev (cutoff_values)
    print (np.max(cutoff_values) - np.min(cutoff_values))
    print (L1_M)
    print (L1_S)

for C in parallel_parts:
    c0 = C.capacitance
    print (C.name, " initial value : ", c0)
    random_values = np.random.normal(c0.value, tolerance, iterations)
    cutoff_values = []
    max_gain_v = []
    max_gain_f = []
    for j in random_values:
        C.capacitance = j@u_pF
        analysis = simulator.ac(start_frequency=startf@u_GHz, stop_frequency=stopf@u_GHz, number_of_points=freq_steps,  variation='dec')
        #abs_serie = np.absolute(analysis['8'])
        #series_L1.append(abs_serie)
    
        # Cutoff : 
        cutoff_values.append(search_3db (analysis, out_node))

        # Peak : 
        index_peak = np.argmax(np.absolute(analysis[out_node])[0:i])
        max_gain_v.append(np.absolute(analysis[out_node][index_peak]))
        max_gain_f.append(analysis.frequency[index_peak])
    
        #simulator.measure('ac', 'cutoff', 'WHEN V(8,gnd)=0.7', 'FALL=1')
        ngspice.destroy()
    # Revert initial value: 
    C.capacitance = c0
    print ("Control (", C.name, " mean and stdev) :")
    print (np.mean(random_values))
    print (np.std (random_values))
    print ("")

    print ("Peak value (frequency span and amplitude span) :")
    print (np.min(max_gain_f), np.max(max_gain_f))
    print (np.min(max_gain_v), np.max(max_gain_v))
    print ("")

    print ("Cutoff (Span, mean, stdev) :")
    #print (cutoff_values)
    cutoff.append(cutoff_values)
    C_M, C_S = moyenne_stdev (cutoff_values)
    print (np.max(cutoff_values) - np.min(cutoff_values))
    print (C_M)
    print (C_S)

#print (circuit)
print (len(cutoff))
print ("min")
for i in range (1, 7) : 
    print (np.min(cutoff [i]))
print("max")
for i in range (1, 7) : 
    print(np.max(cutoff [i]))
print ("mean")

for i in range (1, len(cutoff)) :
    L0_M, L0_S = moyenne_stdev (cutoff [i])
    print(L0_M, " - ", L0_S)

fig, ax = plt.subplots()
VP = ax.boxplot(cutoff, positions=[2,4,6,8,10,12,14, 17, 19, 21, 23, 25, 27, 29, 31], widths=1.5, patch_artist=True,
                showmeans=False, showfliers=False,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "C0", "edgecolor": "white",
                          "linewidth": 0.5},
                whiskerprops={"color": "C0", "linewidth": 1.5},
                capprops={"color": "C0", "linewidth": 1.5})

#ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
#       ylim=(startf*10**9, stopf*10**9), yticks=np.arange(startf*10**9, stopf*10**9, 10))

plt.show()
