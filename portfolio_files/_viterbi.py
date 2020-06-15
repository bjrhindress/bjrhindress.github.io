# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 15:53:31 2019

Course: Machine Learning 10-601, Carnegie Mellon University School of Computer Science
Assignment 6b

This is an implementation of the Viterbi algorithm for Hidden Markov Models (HMM).
For a sequence consisting of T words, x1,..., xT,
the Viterbi algorithm finds the most probable label yt 
for t in the set {1, ..., J}. 

Use Dynamic Programming to compute path probabilities:
wt(j) = max y1,...,yt−1
P(x1,...,xt,y1,...,yt−1,yt = sj)
pt(j) = argmax y1,...,yt−1
P(x1,...,xt,y1,...,yt−1,yt = sj)

Example command-line execution: 
python3 viterbi.py data/testwords.txt data/index_to_word.txt data/index_to_tag.txt data/hmmprior.txt data/hmmemit.txt data/hmmtrans.txt data/predicted_file.txt data/metric_file.txt

@author: bjrhindress
"""
import numpy as np
import sys

###########################
######### Methods #########
###########################

# =============================================================================
# Method to return the index of a given word (or tag) observed in the words sequence
# Args in: (index_to_tag):   Path to the .txt that speciﬁes the dictionary mapping from tags to indices. 
#                           The tags are ordered by index, with the ﬁrst tag having index of 1, the second tag having index of 2, etc. 
#                           This is the same ﬁle as was described for learnhmm.{py|java|cpp|m}.
                                
#          (index_to_word): Path to the .txt that speciﬁes the dictionary mapping from words to indices. 
#                            The tags are ordered by index, with the ﬁrst word having index of 1, the second word having index of 2, etc. 
#                            This is the same ﬁle as was described for learnhmm.{py|java|cpp|m}.
#    
# Args out: (tags, words) indexed arrays of tags and words
# =============================================================================
def read_index_mappings(index_to_tag, index_to_word):
    
    ### Read in index to tag and word mappings 
    with open(index_to_tag, mode='r', newline='\n') as f_in:
        tags = f_in.readlines()
        for i in range(0,len(tags),1): 
            tags[i] = tags[i].strip()
        
    with open(index_to_word, mode='r', newline='\n') as f_in:
        words = f_in.readlines()
        for i in range(0,len(words),1):
            words[i] = words[i].strip()
    
    return(tags, words)

# =============================================================================
# Method to read in the pre-computed HMM parameters
# Args in: (hmmprior):  path to input .txt ﬁle which contains the estimated prior (π).                            
#          (hmmemit): path to input .txt ﬁle which contains the emission probabilities (B).
#          (hmmtrans): path to input .txt ﬁle which contains transition probabilities (A).
#    
# Args out: (pi_prior, emiss_prob, trans_prob): prior, emission, and transition probabilities for the pre-computed HMM
# =============================================================================
def read_HMM_parameters(hmmprior, hmmemit, hmmtrans,tags,words):
    
    ### Set empty matrices for Hidden Markov Model (HMM) parameters
    pi_prior = np.zeros(shape = (len(tags)))
    emiss_prob = np.zeros(shape = (len(tags),len(words)))
    trans_prob = np.zeros(shape = (len(tags),len(tags)))

    ### Read in pre-calculated HMM parameters
    with open(hmmprior, mode='r', newline='\n') as f_in:
        priors = f_in.readlines()
        for i in range(0,len(priors),1): 
            pi_prior[i] = priors[i].strip()

    with open(hmmemit, mode='r', newline='\n') as f_in:
        emiss = f_in.readlines()
        for i in range(0,len(emiss),1):
            split_line = emiss[i].split(' ')
            for j in range(0,len(split_line),1):
                emiss_prob[i,j] = float(split_line[j].strip())
  
    with open(hmmtrans, mode='r', newline='\n') as f_in:
        trans = f_in.readlines()
        for i in range(0,len(trans),1):
            split_line = trans[i].split(' ')
            for j in range(0,len(split_line)):
                trans_prob[i,j] = float(split_line[j].strip())
    
    return(pi_prior, emiss_prob, trans_prob)
    
    
# =============================================================================
# Method to read in the test-data
# Args in: (test_input):  path to the test input .txt ﬁle that will be evaluated by your viterbi algorithm                             
#          
# Args out: (observations, labels): arrays of observations (words) and labels (tags)
# =============================================================================
def read_test_data(test_input):
    
    observations = []
    labels = []
        
    with open(test_input, mode='r', newline='\n') as f_in:    
        test = f_in.readlines()
        test_word_tags = test[0].split(' ')
        for i in range(0,len(test_word_tags),1):
            word_tag = test_word_tags[i].split('_')
            observations.append(word_tag[0].strip())
            labels.append(word_tag[1].strip())
    
    return(observations, labels)

# =============================================================================
# Method to return the index of a given word (or tag) observed in the words sequence
# Args in: (word): word of observation to find. 
#           (words): full sequence of observed words
# Args out: (index) of observed word in sequence (int)
# =============================================================================
def get_obs_index(word,words):

    for i in range(0,len(words),1):
        if(word == words[i]):
            return(i)
    
    return None

# =============================================================================
# Method implementing the Viterbi algorithm (dynamic programming) to solve for the max path probabilities wt and backpointers pt
# Args in: (observations): array of observed words
#           (words):dictionary of indexed words from training
#           (tags): dictionary of indexed labels from training
#           (pi_prior): prior probability of HMM
#           (emiss_prob): emission probability of HMM
#           (trans_prob): transition probability of HMM
    
# Args out: (wt, pt) path probabilities wt and backpointers pt of the HMM
# =============================================================================
def Viterbi(observations,words,tags,pi_prior,emiss_prob,trans_prob):
    
    # Initialize empty arrays for path probabilities wt and backpointers pt
    wt = np.zeros(shape = (len(tags),len(observations)))
    pt = np.zeros(shape = (len(tags),len(observations)), dtype = object)
    
    # Viterbi Algorithm 
    #1) for each state in t = 1, 
    #    w1(state) = pistate * emission(state,x1)
    #    p1(state) = state
    for i in range(0,len(tags),1):
        obs_index = get_obs_index(observations[0],words)
        wt[i,0] = pi_prior[i]*emiss_prob[i,obs_index]
        pt[i,0] = tags[i]
    
    #2)for t>1, for each observation ti, for each current state, calculate the max probability path
    #   coming from each previous state
    for i in range(1,len(observations),1):# for each observation, ti
        obs_index = get_obs_index(observations[i],words) # for each current state 
        for j in range(0,len(tags),1): # for each previous state 
            max_wtk = 0
            for k in range(0,len(tags),1):
                prev_obs_index = get_obs_index(observations[i-1],words)
                wtk = emiss_prob[j,obs_index]*trans_prob[k,j]*wt[k,i-1]
                if(wtk>max_wtk):
                    max_wtk = wtk
                    wt[j,i] = wtk
                    pt[j,i] = tags[k]
    return(wt,pt)
        
    
# =============================================================================
# Method predicting the unobserved words that resulted in the tag sequence observed
# Args in: (tags): observed labels
#           (wt):path probabilities
#           (pt): path backpointers
    
# Args out: (predicted_path): output prediction of the most likely HMM sequence
# =============================================================================    
def predict(tags, wt, pt):
    
    # Initialize last observation and empty list of predicted states
    last_obs = True
    predicted_states = np.zeros(shape = (len(observations)),dtype = object)
    
    # For every observation, starting from the last observation and moving backwards:
    for i in range(len(observations)-1,0,-1):
        max_state_prob = 0
        max_state = ''
        
        # Initialization for last observation
        if(last_obs):
            for j in range(0,len(tags),1):
                
                state_prob = wt[j,i]
                
                if (state_prob>max_state_prob):
                    max_state_prob = state_prob
                    predicted_states[i] = tags[j]
                    predicted_states[i-1] = pt[j,i]
            
            last_obs = False
        
        # All other observations
        else:
            predicted_states[i-1] = pt[get_obs_index(predicted_states[i],tags),i]
    
    return(predicted_states)

# =============================================================================
# Method writing the test metrics to a specified file
# Args in: (predicted_file): .txt file name to store predicted word sequence
#           (metric_file): .txt file name to store metrics of prediction
#           (predicted_states): states predicted
    
# Args out: None
# =============================================================================   
def metrics_to_file(predicted_file, metric_file, predicted_states):  
    with open(predicted_file, mode='w', newline='\n') as f_out:
            for i in range(0,len(predicted_states),1):
                f_out.write(observations[i] + '_'+ predicted_states[i] + ' ')
                
    with open(metric_file, mode='w', newline='\n') as f_out:
        incorrect = 0
        for i in range(0,len(predicted_states),1):
            if(predicted_states[i]!=labels[i]):
                incorrect +=1
                            
        f_out.write("Accuracy: " + str(1-incorrect/len(predicted_states)) + '\n')
            
###########################
######### Main ############
###########################

if __name__ == '__main__':
    
    # Command-line inputs
    test_input = sys.argv[1]
    index_to_word = sys.argv[2]
    index_to_tag = sys.argv[3]
    hmmprior = sys.argv[4]
    hmmemit = sys.argv[5]
    hmmtrans = sys.argv[6]
    predicted_file = sys.argv[7]
    metric_file = sys.argv[8]

    ### Generate HMM model  
    (tags, words) = read_index_mappings(index_to_tag, index_to_word)
    (observations, labels) = read_test_data(test_input)
    (pi_prior, emiss_prob, trans_prob) = read_HMM_parameters(hmmprior, hmmemit, hmmtrans, tags, words)
    
    ### Viterbi Algorithm 
    (wt,pt) = Viterbi(observations,words,tags,pi_prior,emiss_prob,trans_prob)

    ### Predict Path using wt and pt from Viterbi    
    predicted_states = predict(tags, wt, pt)
    
    ### Write out test metrics
    metrics_to_file(predicted_file, metric_file, predicted_states)    