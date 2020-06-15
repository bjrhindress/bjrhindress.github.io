from environment import MountainCar
import sys
import numpy as np 


#Implement: 
def policy(wa,b,mc):
    
    state = mc.state
    s = getState(state,wa)
    done = False
    
    while(not done):
        (qv, a) = getMaxAction(s,wa,b)
        (state,reward,done) = mc.step(a)
        s = getState(state,wa)
        #mc.render()
    
    print("done!")
    
def train(episodes, max_iterations,mc,mode,learning_rate,gamma,epsilon):

    # Initialize wa 
    if(mode=="raw"):
        params = 2
    else:
        params = 2048
    wa = np.zeros((3,params))
    b = 0
    returns = np.zeros(episodes)
    #Initial state 
    #(state,reward,done) = mc.step(0)
    
    state = mc.state
    s = getState(state,wa)
    
    for i in range(0,episodes,1):
        
        reward_sum = 0

        for j in range(0,max_iterations,1):
            
            ## Decide what to do based on epsilons 
            ### For epsilon probability, choose randomly
            

            if(np.random.sample()<epsilon):
                a = np.floor(np.random.sample()*3)
                a = int(a)
                qsa = q(s, a, wa,b)
                
            else: ### for 1-epsilon, choose optimally 
                # Get max of current state action choices 
                (qsa,a) = getMaxAction(s,wa,b) 
            
            #Get next state
            (next_state,r,done) = mc.step(a)
            s_next = getState(next_state,wa)
            #print(a)
            #print(r)
            #Get max of next state action choices
            (qnexta, anew) = getMaxAction(s_next, wa,b)
            
            # gradient of wq given a: just the state, s
            wa[a,:] = wa[a,:] - learning_rate*(qsa - (r + gamma*qnexta))*s
            b = b - learning_rate*(qsa - (r + gamma*qnexta))*1 #bias
            #print(wa)
            s = s_next
                        
            if(j == 100):
                mc.render(mode="human")
            
            reward_sum += r
        
            if(done):
                break
        returns[i] = reward_sum
        mc.reset()
        print(reward_sum)
                 
                # q(s,a;w) =sTwa+b
    # w←w−α(q(s,a;w)−(r+γmax a′ |  q(s′,a′;w))∇wq(s,a;w)
            #qsa = q(s,0,wa)
            
    return (wa,b,returns)
    # state vector ?? --> get from environment?
    # w vector --> create: 3 actions x # features
    # b is just a scalar. 

def getState(state,wa):
    
    s = np.zeros(len(wa[0,:]))

    if(isinstance(state,dict)):
    #indecies = [int(i) for i in list(state.keys())]
        for i in state.keys():
            s[i] = state[i]
    else:
        for i in range(0,len(state),1):
            s[i] = state[i]
    #s[indecies] = state.values()
    
    return s
    
def q(s, a, wa,b):
    
    qa = np.dot(np.transpose(s),wa[a,:]) + b
    
    return qa

def getMaxAction(s,wa,b):
    
    maxq = 0
    maxa = 0
    for a in range(0,3,1):
        
        qa = q(s,a,wa,b)
        if(a == 0):
            maxq = qa
            maxa = 0
        if (qa>maxq):
            maxq = qa
            maxa = a

    return(maxq, maxa)
    
    # q(s,a;w) =sTwa+b
    # w←w−α(q(s,a;w)−(r+γmax a′ |  q(s′,a′;w))∇wq(s,a;w)
    # incorporate e and 1-e greedy algorithms 
    
    
    # for episodes
        # for max iterations within episode 
    
def parse_arguments(self):
    mode = sys.argv[1]
    weight_out = sys.argv[2]
    returns_out = sys.argv[3]
    episodes = sys.argv[4]
    max_iterations = sys.argv[5]
    epsilon = sys.argv[6]
    gamma = sys.argv[7]
    learning_rate = sys.argv[8]

    try:
        if(mode != "raw" and mode != "tile"):
            mode = "raw"
    except:
        print("Mode issue ")
    
    try:
        episodes = int(episodes)
    except:
        print("episode issue ")
    
    try:
       max_iterations = int(max_iterations)
        
    except:
        print("max_iteration issue ")
    
    try:
        epsilon = float(epsilon)
    except:
        print("epsilon issue ")

    try:
        gamma = float(gamma)
    except:
        print("gamma issue ")

    try:
        learning_rate = float(learning_rate)
    except:
        print("learning_rate issue ")
    
    return(mode,weight_out,returns_out,episodes,
           max_iterations, epsilon,gamma,learning_rate)
        
   
    
    
def main(args):
    
    np.random.seed(np.int64(10601))
    (mode,weight_out,returns_out,episodes,
           max_iterations, epsilon,gamma,
           learning_rate) = parse_arguments(args)

    mc = MountainCar(mode)
    #mc.render(mode='human')
    
    
    (wa,b, returns) = train(episodes, max_iterations,mc,mode,learning_rate,gamma,epsilon)
    
    
    print(b)
    for i in np.transpose(wa):
        print(i)
    
    with open(weight_out, mode='w', newline='\n') as f_out:
        f_out.write(str(b) + "\n")
        for i in np.transpose(wa):
            for j in i:
                f_out.write(str(j) + "\n")
    
    with open(returns_out, mode='w', newline='\n') as f_out:
        for i in returns:
            f_out.write(str(i) + "\n")        
     
    #policy(wa,b,mc)
    
if __name__ == "__main__":
    main(sys.argv)
    

#Mountaincar methods: 
#    init
#    reset
#    step
#    render