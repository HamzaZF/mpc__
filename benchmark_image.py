import time
import matplotlib.pyplot as plt
from mpyc.runtime import mpc    # load MPyC
from mpyc.seclists import seclist
secint = mpc.SecInt()           # 32-bit secure MPyC integers
secflt = mpc.SecFlt()
mpc.run(mpc.start())            # required only when run with multiple parties
import traceback                # to show some suppressed error messages


# Classic computation
def get_intersection_classic(liste_croissante, liste_decroissante, i):
    max = len(liste_decroissante) if len(liste_decroissante) < len(liste_croissante) else len(liste_croissante)

    if i == max:
        #print("pas de solutions !")
        return 0
    elif liste_decroissante[i] == liste_croissante[i]:
        #print("solution (les deux échelons sont constants au meme niveau) ", i)
        return 1
    elif liste_decroissante[i] < liste_croissante[i]:
        #il y a eu une intersection
        switched = True
        #cas 1 : les deux courbes se sont coupées en meme temps
        if i==0:
            #print("pas de solutions")
            return 3
        elif (liste_croissante[i] != liste_croissante[i-1]) and (liste_decroissante[i] != liste_decroissante[i-1]):
            #print("solution (les deux courbes se sont coupées en meme temps) : ", (liste_croissante[i-1] + liste_decroissante[i-1])/2)
            return 4
        #cas 2 : la courbe de l'offre à coupée celle de la demande
        elif (liste_croissante[i] == liste_croissante[i-1]) and (liste_decroissante[i] != liste_decroissante[i-1]):
            #print("solution (la courbe de l'offre à coupée celle de la demande) : ", liste_croissante[i])
            return 5
        #cas 3 : la courbe de la demande à coupée celle de l'offre
        elif (liste_croissante[i] != liste_croissante[i-1]) and (liste_decroissante[i] == liste_decroissante[i-1]):
            #print("solution (la courbe de la demande à coupée celle de l'offre) : ", liste_decroissante[i])
            return 6
    else:
        return 2


def get_intersection_mpc(liste_croissante, liste_decroissante, i):
    max = len(liste_decroissante) if len(liste_decroissante) < len(liste_croissante) else len(liste_croissante)

    ret_if_1 = -2
    ret_if_2 = -2
    ret_if_3 = -2
    ret_if_0 = -2
    ret_2 = -2
    ret_1 = -2

    if i==max:
        return (secint(-55), -1)
        
    ret_if_3_ = mpc.if_else((liste_decroissante[i] == liste_decroissante[i-1]), liste_decroissante[i], -4)

    ret_if_3 = mpc.if_else((liste_croissante[i] != liste_croissante[i-1]), ret_if_3_, -4)
    
    ret_if_2_ = mpc.if_else((liste_decroissante[i] == liste_decroissante[i-1]), liste_croissante[i], ret_if_3)
        
        
    ret_if_2 = mpc.if_else((liste_croissante[i] == liste_croissante[i-1]), ret_if_2_, ret_if_3)
    
    ret_if_1_ = mpc.if_else((liste_decroissante[i] != liste_decroissante[i-1]), (liste_croissante[i-1] + liste_decroissante[i-1])/2, ret_if_2)
    
    ret_if_1 = mpc.if_else((liste_croissante[i] != liste_croissante[i-1]) , ret_if_1_, ret_if_2)
    
    ret_if_2_0 = mpc.if_else(ret_if_1==ret_if_1_, 1, -1)
    ret_if_2_1 = mpc.if_else(ret_if_1_==(liste_croissante[i-1] + liste_decroissante[i-1])/2, 1, -1)
    
    ret_if_0 = mpc.if_else(i==0, -1, ret_if_1)
    
    ret_2 = mpc.if_else(liste_decroissante[i] < liste_croissante[i], ret_if_0, -5) #-5 <=> i+=1
    
    ret_1 = mpc.if_else(liste_decroissante[i] == liste_croissante[i], i, ret_2)
    
    ret_0 = mpc.if_else(i == max, -1, ret_1)
    
    ret__0 = mpc.if_else(ret_0 == -1, -1, 1)
    
    ret__1 = mpc.if_else(i == max, -1, 1)
    
    ret_if_i_max = mpc.if_else(i == max, 1, -1)
    ret_if_croissante_e_decroissante = mpc.if_else(ret_2 == -2, 1, -1)
    ret_if_decroissante_inf_decroissante = mpc.if_else(ret_2 == -5, -1, 1)
    ret_if_e_zero = mpc.if_else(ret_if_1 == -2, 1, -1)

    a = mpc.if_else(ret_if_2_0==1, 1, 0)
    b = mpc.if_else(ret_if_2_1==1, 1, 0)

    #c = a + b # good ?
    c = mpc.add(a,b)
    ret_if_croi_i_diff_croi_i__1_decroi_i_diff_decroi_i_1 = mpc.if_else(c==2, 1, -1)
    
    ret_if_croi_i_e_croi_i__1_decroi_i_diff_decroi_i_1 = mpc.if_else(ret_if_3==-4, 1, -1)
    ret_if_croi_i_diff_croi_i__1_decroi_i_e_decroi_i_1_0 = mpc.if_else(ret_if_3_==-4, 1, -1)
    ret_if_croi_i_diff_croi_i__1_decroi_i_e_decroi_i_1_1 = mpc.if_else(ret_if_3==-4, 1, -1)

    result = mpc.if_else(ret_if_i_max==1, 0, 
                mpc.if_else(ret_if_croissante_e_decroissante==1, 1,
                            mpc.if_else(ret_if_decroissante_inf_decroissante==-1, 2,
                                        mpc.if_else(ret_if_e_zero==1, 3,
                                                    mpc.if_else(ret_if_croi_i_diff_croi_i__1_decroi_i_diff_decroi_i_1==1, 4, 
                                                                mpc.if_else(ret_if_croi_i_e_croi_i__1_decroi_i_diff_decroi_i_1==1, 5,
                                                                            mpc.if_else(ret_if_croi_i_diff_croi_i__1_decroi_i_e_decroi_i_1_0==-1,
                                                                                        mpc.if_else(ret_if_croi_i_diff_croi_i__1_decroi_i_e_decroi_i_1_1==-1, 6, -100), -100)))))))

    final_result = result

    return final_result


# Function to measure execution time for classic computation
def measure_time_classic(liste_croissante, liste_decroissante):
    start_time = time.time()
    i = 0
    stop = 0

    while stop != 1:
        result = get_intersection_classic(liste_croissante, liste_decroissante, i)

        if result == 0:
            stop = 1
        elif result == 1:
            stop = 1
        elif result == 2:
            i = i + 1
        elif result == 3:
            stop = 1
        elif result == 4:
            stop = 1
        elif result == 5:
            stop = 1
        elif result == 6:
            stop = 1

    return time.time() - start_time

# Function to measure execution time for MP-computation
def measure_time_mpc(liste_croissante, liste_decroissante):
    start_time = time.time()
    i = 0
    stop = 0

    while stop != 1:
        result = mpc.run(mpc.output(get_intersection_mpc(liste_croissante, liste_decroissante, i)))

        if result == 0:
            stop = 1
        elif result == 1:
            stop = 1
        elif result == 2:
            i = i + 1
        elif result == 3:
            stop = 1
        elif result == 4:
            stop = 1
        elif result == 5:
            stop = 1
        elif result == 6:
            stop = 1

    return time.time() - start_time

# Generating lists of increasing lengths
max_list_size = 1000
step = 5
list_sizes = list(range(step, max_list_size + 1, step))

execution_times_classic = []
execution_times_mpc = []

for size in list_sizes:
    liste_croissante_classic = list(range(1, size + 1))
    liste_decroissante_classic = list(range(size, 0, -1))

    liste_croissante_mpc = list(map(secint, range(1, size + 1)))
    liste_decroissante_mpc = list(map(secint, range(size, 0, -1)))

    time_classic = measure_time_classic(liste_croissante_classic, liste_decroissante_classic)
    time_mpc = measure_time_mpc(liste_croissante_mpc, liste_decroissante_mpc)

    execution_times_classic.append(time_classic)
    execution_times_mpc.append(time_mpc)

"""
# Plotting the graph
plt.plot(list_sizes, execution_times_classic, label="Classic Computation")
plt.plot(list_sizes, execution_times_mpc, label="MP Computation")
plt.xlabel("List Size")
plt.ylabel("Execution Time (s)")
plt.legend()
plt.title("Execution Time Comparison")
plt.grid(True)
plt.show()

mpc.run(mpc.shutdown())
"""

# Plotting the graph (classic version)
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(list_sizes, execution_times_classic, label="Classic Computation")
plt.plot(list_sizes, execution_times_mpc, label="MP Computation")
plt.xlabel("List Size")
plt.ylabel("Execution Time (s)")
plt.legend()
plt.title("Execution Time Comparison (Classic)")

# Plotting the graph (logarithmic scale)
plt.subplot(1, 2, 2)
plt.semilogy(list_sizes, execution_times_classic, label="Classic Computation")
plt.semilogy(list_sizes, execution_times_mpc, label="MP Computation")
plt.xlabel("List Size")
plt.ylabel("Execution Time (s)")
plt.legend()
plt.title("Execution Time Comparison (Logarithmic Scale)")
plt.grid(True)

plt.tight_layout()
plt.show()

# Saving the graph as an image
plt.savefig("execution_time_comparison.png")