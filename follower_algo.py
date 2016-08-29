
network = {
    'mohamed': {
        'following': ['davinci', 'rms', 'gauss'],
        'followed': ['einstein']
    },
    'davinci': {
        'following': [],
        'followed': ['einstein', 'mohamed']
    },
    
    'rms': {
        'following': ['einstein'],
        'followed': ['mohamed']
    },

    'gates': {
        'following': ['einstein', 'gauss'],
        'followed': ['gauss', 'einstein']
    },
    'einstein': {
        'following': ['mohamed', 'davinci', 'gates', 'euler'],
        'followed': ['rms', 'euler', 'gates']
    },
    'euler': {
        'following': ['einstein', 'gauss'],
        'followed': ['einstein', 'gauss']
    },
    'gauss': {
        'following': ['gates', 'euler', 'einstein'],
        'followed': ['euler', 'gates', 'mohamed']
    }
}

p = 1
depth_allowed = 14

def doMath(x, i=0):
    print x
    raw_input()
    s = 0
    for y in network[x]['followed']:
        s += (1 + p * doMath(y)) / len(network[y]['following'])
    return s

print doMath('mohamed')
