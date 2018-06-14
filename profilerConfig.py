
global profiler_config

def clear():
    global profiler_config
    profiler_config = { 
        "TIME_LOGIC" : [],
        "TIME_DISPLAY" : [],
        "TIME_TOTAL" : [],
        "NB_NPC" : [],
        "TIME_INIT": 0
    }
    
def append_to(name, value, _max=-1):
    global profiler_config
    if isinstance(profiler_config[name], list):
        profiler_config[name].append(value)
        if _max != -1 and len(profiler_config[name]) > _max:
            profiler_config[name] = profiler_config[name][1:]

def set(name, value):
    global profiler_config
    print(profiler_config[name], value)
    profiler_config[name] = value

def get(name):
    global profiler_config
    if name in profiler_config.keys():
        return profiler_config[name]
    else:
        return None

def getAll():
    global profiler_config
    return profiler_config