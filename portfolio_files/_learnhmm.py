# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 11:31:41 2019

Course: Machine Learning 10-601, Carnegie Mellon University School of Computer Science
Assignment 6a

implement an algorithm to learn the hidden Markov model parameters needed to apply the viterbi algorithm. 
There are three sets of parameters that you will need to estimate: the initialization probabilities π, the transition probabilities A, and the emission probabilities B. 
For this assignment, we model each of these probabilities using a multinomial distribution with parameters πj = P(y1 = j), ajk = P(yt = k|yt−1 = j), and bjk = P(xt = k|yt = j). 
These can be estimated using maximum likelihood.

Example command-line execution: 
python3 learnhmm.py data/trainwords.txt data/index_to_word.txt data/index_to_tag.txt data/hmmprior.txt data/hmmemit.txt data/hmmtrans.txt

@author: bjrhindress


"""

import sys
import numpy as np

###########################
######### Methods #########
###########################


# =============================================================================
# Method to read in training sequence/text, and indexed dictionaries of words and labels 
# Args in: (train_input):   path to the training input .txt ﬁle
#          (index_to_tag):   Path to the .txt that speciﬁes the dictionary mapping from tags to indices. 
#                           The tags are ordered by index, with the ﬁrst tag having index of 1, the second tag having index of 2, etc. 
#                           This is the same ﬁle as was described for learnhmm.{py|java|cpp|m}.
                                
#          (index_to_word): Path to the .txt that speciﬁes the dictionary mapping from words to indices. 
#                            The tags are ordered by index, with the ﬁrst word having index of 1, the second word having index of 2, etc. 
#                            This is the same ﬁle as was described for learnhmm.{py|java|cpp|m}.
#    
# Args out: (tags, words, np_text): the dictionaries of tags, words, and the sequence(s) of text stored as a np_array 
# =============================================================================
def read_train_data(train_input, index_to_tag, index_to_word):
    
    with open(train_input, mode='r', newline='\n') as f_in:
            input_text = f_in.readlines()
            text_final = []
            for line in input_text:
                split_sentence = line.split(' ')
                sentence_final = []
                for word in split_sentence:
                    word_tag = word.split('_')
                    word = word_tag[0].strip()
                    tag = word_tag[1].strip()
                    sentence_final.append([word,tag])
                text_final.append(sentence_final)
            np_text = np.array(text_final)
        
    with open(index_to_tag, mode='r', newline='\n') as f_in:
        tags = f_in.readlines()
        for i in range(0,len(tags),1): 
            tags[i] = tags[i].strip()
                
    with open(index_to_word, mode='r', newline='\n') as f_in:
        words = f_in.readlines()
        for i in range(0,len(words),1):
            words[i] = words[i].strip()

    return(tags, words, np_text)

# =============================================================================
# Method to estimate the Hidden Markov Model parameters pi_prior, trans_prob, emiss_prob, given a text sequence, and dictionary of words and tags
# Args in: (text):sequence of words to generate parameters
#          (tags): label dictionary (array)                        
#          (words): word dictionary (array)
#    
# Args out: (tags, words) indexed arrays of tags and words
# =============================================================================
def parameterEstimation(text,tags,words):
    
    #pi - probability of states (Tags) 
    pi_prior= dict()
    for state in tags:
        pi_count = 0
        for sentence in text:
            for word in sentence: 
                if(word[1] == state):
                    pi_count+=1
                break
        
        pi_prior[state] = (pi_count+1)/(len(text)+len(tags))
        
        
    #transition probabilities, states = rows, states cols 
    trans_prob = np.zeros(shape = (len(tags),len(tags)))
    
    for i in range(0,len(tags),1):
        for j in range(0,len(tags),1):
            trans_count = 0
            total_state_trans = 0
            for sentence in text:
                for t in range(1,len(sentence),1):
                    if(sentence[t-1][1]==tags[i]):
                        if(sentence[t][1]==tags[j]):
                            trans_count +=1
                        total_state_trans +=1

            trans_prob[i,j] = (trans_count+1)/(total_state_trans + len(tags))
    
    # emission probabilities, states rows, words cols 
    emiss_prob = np.zeros(shape = (len(tags),len(words)))

    for i in range(0,len(tags),1):
        for j in range(0,len(words),1):
            emiss_count = 0
            total_state_count = 0
            for sentence in text:
                for word in sentence:
                    if(word[1] == tags[i]):
                        if(word[0] == words[j]):
                            emiss_count +=1
                        total_state_count+=1
            emiss_prob[i,j] = (emiss_count+1)/(total_state_count+len(words))

    
    return(pi_prior, trans_prob, emiss_prob)

# =============================================================================
# Method to write HMM parameters to output files
# Args in: (text_len): length of text to read in (hyperparameter)
#          (hmmprior): .txt file to store hmmprior
#          (hmmtrans): .txt file to store hmmtrans
#          (hmmemit):  .txt file to store hmmemit
#          (pi_prior):  probability of prior occurence of the word                                
#          (trans_prob): transition probability of all words --> words
#          (emiss_prob): emission probabilities of all words
#    
# Args out: None - writes to output file
# =============================================================================  
    
def write_hmm_parameters(text_len,hmmprior, hmmtrans, hmmemit, pi_prior, trans_prob, emiss_prob):

        # Uncomment only if varying hyperparameters of number of sequences (text length)
        #hmmprior = hmmprior + 'L' + str(text_len)
        #hmmtrans = hmmtrans + 'L' + str(text_len)
        #hmmemit = hmmemit + 'L' + str(text_len)
    
        with open(hmmprior, mode='w', newline='\n') as f_out:
            for prior in pi_prior.values():
                f_out.write(str(prior) + '\n')
            
        with open(hmmtrans, mode='w', newline='\n') as f_out:
            for row in trans_prob:
                for col in row:
                    f_out.write(str(col) + ' ')    
                f_out.write('\n')
            
        with open(hmmemit, mode='w', newline='\n') as f_out:
            for row in emiss_prob:
                for col in row:
                    f_out.write(str(col) + ' ')
                f_out.write('\n')

###########################
######### Main #########
###########################


if __name__ == '__main__':
    
    # Command-line inputs
    train_input = sys.argv[1]
    index_to_word = sys.argv[2]
    index_to_tag = sys.argv[3]
    hmmprior = sys.argv[4]
    hmmemit = sys.argv[5]
    hmmtrans = sys.argv[6]
    
    # Read in training data
    (tags, words, np_text) = read_train_data(train_input, index_to_tag, index_to_word)
    
    #Vary hyper parameter of text_lengths
    text_lengths = [10] #[10,100,1000,10000]
    for text_len in text_lengths:
        
        # Estimate HMM parameters 
        (pi_prior, trans_prob, emiss_prob) = parameterEstimation(np_text[0:text_len],tags,words)
        
        # Write HMM parameters to files
        write_hmm_parameters(text_len, hmmprior, hmmtrans, hmmemit, pi_prior, trans_prob, emiss_prob)
        