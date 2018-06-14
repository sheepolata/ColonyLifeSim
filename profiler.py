import colonylife
import profilerConfig as pc

import json
import numpy as np
import time

def writeResJson(file, args={}):
    
    data = {}

    data["parameters"] = args

    mean_total = np.mean(pc.get("TIME_TOTAL"))
    mini_total = min(pc.get("TIME_TOTAL"))
    maxi_total = max(pc.get("TIME_TOTAL"))

    mean_logic = np.mean(pc.get("TIME_LOGIC"))
    mini_logic = min(pc.get("TIME_LOGIC"))
    maxi_logic = max(pc.get("TIME_LOGIC"))

    mean_display = np.mean(pc.get("TIME_DISPLAY"))
    mini_display = min(pc.get("TIME_DISPLAY"))
    maxi_display = max(pc.get("TIME_DISPLAY"))

    data["time"] = {}
    data["time"]["init"] = pc.get("TIME_INIT")
    data["time"]["total"] = {"mean":mean_total, "min":mini_total, "max":maxi_total, "all":pc.get("TIME_TOTAL")}
    data["time"]["logic"] = {"mean":mean_logic, "min":mini_logic, "max":maxi_logic, "all":pc.get("TIME_LOGIC")}
    data["time"]["display"] = {"mean":mean_display, "min":mini_display, "max":maxi_display, "all":pc.get("TIME_DISPLAY")}

    data["entities"] = {}
    data["entities"]["npc"] = {"number":pc.get("NB_NPC"), "mean":np.mean(pc.get("NB_NPC"))}

    json.dump(data, file, sort_keys = True, indent = 4, ensure_ascii = False)

    pass

def writeRes(file, args={}):
    mean_total = np.mean(pc.get("TIME_TOTAL"))
    mini_total = min(pc.get("TIME_TOTAL"))
    maxi_total = max(pc.get("TIME_TOTAL"))

    mean_logic = np.mean(pc.get("TIME_LOGIC"))
    mini_logic = min(pc.get("TIME_LOGIC"))
    maxi_logic = max(pc.get("TIME_LOGIC"))

    mean_display = np.mean(pc.get("TIME_DISPLAY"))
    mini_display = min(pc.get("TIME_DISPLAY"))
    maxi_display = max(pc.get("TIME_DISPLAY"))

    if args:
        stri = "==== PARAMETERS ====\n"
        for k in args.keys():
            stri +=  k + " = " + str(args[k]) + ";"
        file.write( stri[:-1] + "\n")

    file.write("\n===== RESULTS =====\n")
    file.write("========== NPC DATA\n")
    file.write("Number of survivors = " + str(pc.get("NB_NPC")[-1]) + "\n")
    file.write("Mean NPC number = " + str(np.mean(pc.get("NB_NPC"))) + "\n")
    file.write("List NPC count = " + str(pc.get("NB_NPC")) + "\n")
    file.write("\n")
    file.write("======== TIME LOGIC\n")
    file.write( "Mean logic loop = " + str(mean_logic) + "s\n")
    file.write( "Min logic loop = " + str(mini_logic) + "s\n")
    file.write( "Max logic loop = " + str(maxi_logic) + "s\n")
    file.write("\n")
    file.write("====== TIME DISPLAY\n")
    file.write( "Mean display loop = " + str(mean_display) + "s\n")
    file.write( "Min display loop = " + str(mini_display) + "s\n")
    file.write( "Max display loop = " + str(maxi_display) + "s\n")
    file.write("\n")
    file.write("========= TIME INIT\n")
    file.write( "Init time = " + str(pc.get("TIME_INIT")) + "s\n")
    file.write("\n")
    file.write("======== TIME TOTAL\n")
    file.write( "Mean main loop = " + str(mean_total) + "s\n")
    file.write( "Min main loop = " + str(mini_total) + "s\n")
    file.write( "Max main loop = " + str(maxi_total) + "s\n")
    file.write("\n")


def printRes(args={}):
    mean_total = np.mean(pc.get("TIME_TOTAL"))
    mini_total = min(pc.get("TIME_TOTAL"))
    maxi_total = max(pc.get("TIME_TOTAL"))

    mean_logic = np.mean(pc.get("TIME_LOGIC"))
    mini_logic = min(pc.get("TIME_LOGIC"))
    maxi_logic = max(pc.get("TIME_LOGIC"))

    mean_display = np.mean(pc.get("TIME_DISPLAY"))
    mini_display = min(pc.get("TIME_DISPLAY"))
    maxi_display = max(pc.get("TIME_DISPLAY"))

    if args:
        stri = "==== PARAMETERS ====\n"
        for k in args.keys():
            stri +=  k + " = " + str(args[k]) + ";"
        print( stri[:-1] + "\n")

    print("\n===== RESULTS =====\n")
    print("========== NPC DATA\n")
    print("Number of survivors = " + str(pc.get("NB_NPC")[-1]) + "\n")
    print("Mean NPC number = " + str(np.mean(pc.get("NB_NPC"))) + "\n")
    print("List NPC count = " + str(pc.get("NB_NPC")) + "\n")
    print("\n")
    print("======== TIME LOGIC\n")
    print( "Mean logic loop = " + str(mean_logic) + "s\n")
    print( "Min logic loop = " + str(mini_logic) + "s\n")
    print( "Max logic loop = " + str(maxi_logic) + "s\n")
    print("\n")
    print("====== TIME DISPLAY\n")
    print( "Mean display loop = " + str(mean_display) + "s\n")
    print( "Min display loop = " + str(mini_display) + "s\n")
    print( "Max display loop = " + str(maxi_display) + "s\n")
    print("\n")
    print("========= TIME INIT\n")
    print( "Init time = " + str(pc.get("TIME_INIT")) + "s\n")
    print("\n")
    print("======== TIME TOTAL\n")
    print( "Mean main loop = " + str(mean_total) + "s\n")
    print( "Min main loop = " + str(mini_total) + "s\n")
    print( "Max main loop = " + str(maxi_total) + "s\n")
    print("\n")

def main():
    pc.clear()

    f = open("./logs/profile.prof", "w")
    fjson = open("./logs/profile.json", "w")
    
    #Profiler without display
    nbloop = 5
    for i in range(nbloop):
        nb_npc = 10*(i+1)
        nb_obs = 10
        nb_spawner = 2+i
        _profiler = 20000

        DISPLAY = True
        debug_displ = False


        t = time.time()
        colonylife.main(nb_npc=nb_npc, 
                        nb_obs=nb_obs, 
                        nb_spawner=nb_spawner, 
                        _profiler=_profiler, 
                        DISPLAY=DISPLAY, 
                        debug_displ=debug_displ, 
                        number=i, 
                        max_number=nbloop)
        t = time.time() - t

        args = {"number":i,"nb_npc":nb_npc, "nb_obs":nb_obs, "nb_spawner":nb_spawner, "profiler":_profiler, "time_taken":t}
        writeRes(f, args)
        writeResJson(fjson, args)
        printRes(args)
        
        pc.clear() 

    f.close()
    fjson.close()

if __name__ == '__main__':
    main()