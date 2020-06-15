# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 07:30:40 2019

Course: Machine Learning 10-601, Carnegie Mellon University School of Computer Science
Assignment 5: Neural Networks

The following program implements an optical character recognizer
using a one hidden layer neural network with sigmoid activations. 

Requirements: 
    - Sigmoid activation function on hidden layers
    - Softmax on output layers
    - # Hidden units determined by command line flag
    - Use Stochastic gradient Descent (SGD) to optimize parameters for one hidden layer
    - # Epochs specified as command flag
    - Learning rate set via command flag
    - Assumes input data always has same # of features

Example command-line execution: 
python3 neuralnet.py data/smalltrain.csv data/smalltest.csv data/model1train_out.labels data/model1test_out.labels data/model1metrics_out.txt 2 4 2 0.1

@author: bjrhi
"""

import numpy
import sys

# =============================================================================
# Method to convert command_line arguments to the proper data types
# Args in: (num_epoch): number of epochs
#          (hidden_units): number of hidden units per layer
#          (init_flag): random vs. zero initilization for weights
#          (learning_rate):  learning rate for SGD
#    
# Args out: (epochs, hidden_units_int, init_flag_int, learning_rate_num): cleaned versions of each argument
# ============================================================================= 

def clean_command_line(num_epoch, hidden_units, init_flag, learning_rate):
    
    try:
        epochs = int(num_epoch)
    except: 
        epochs = 10
    try: 
        hidden_units_int = int(hidden_units)
    except:
        hidden_units_int = 4
    try:
        init_flag_int = int(init_flag)
    except:
        init_flag_int = 0
    try: 
        learning_rate_num = float(learning_rate)
    except:
        learning_rate_num = 1.0
    
    return(epochs, hidden_units_int, init_flag_int, learning_rate_num)
    

# =============================================================================
# Method to read in train/test data
# Args in: (input): a file of train or test data, formatted as a matrix with observations in i rows, with multiclass labels in column j
#    
# Args out: (y_onehot,x): observation labels in a one-hot format, x data in matrix
# ============================================================================= 
def read_input(input):
    
    with open(input, mode='r', newline='\n') as file_input:
        a = numpy.loadtxt(file_input,delimiter = ',')
    
    # Extract labels from first column    
    y = a[:,0].astype(int)
    
    # Create one-hot label matrix   
    num_observations = len(y)
    num_classes = len(set(y))
    y_onehot = numpy.zeros((num_observations,num_classes))
    
    for i in range(0,num_observations,1):
        y_onehot[i,y[i]] = 1    
    
    # Extract features and add bias term
    x = a[:,1:]
    bias_terms = [1 for i in range(0,len(x[:,1]))]
    x = numpy.insert(x,0,bias_terms,axis=1)
    
    return(y_onehot,x)
    
    
    
# =============================================================================
# Method to initialize A and B parameters 
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (hidden_units): number of hidden units per layer
#          (init_flag_int): random vs. zero initilization for weights

# Args out: (A,B): Neural Network parameters, initialized and sized correctly
# ============================================================================= 
    
def initializeAB(x,y,hidden_units_int,init_flag_int):
    
    #Alpha initialization
    Acols = hidden_units_int
    Arows = len(x[1,])
    
    #Beta  initialization
    Bcols = len(y[0,:])
    Brows = 1 + hidden_units_int


    # Randomize or zero with init_flag
    if(init_flag_int == 1):
        #randomize from -0.1 to 0.1
        A =  numpy.random.rand(Acols,Arows)
        B = numpy.random.rand(Brows,Bcols)
        
        A = (A*2-1)*0.1
        B = (B*2-1)*0.1
        
        A = numpy.transpose(A)

    elif(init_flag_int == 2):
        A = numpy.zeros((Arows,Acols))
        B = numpy.zeros((Brows,Bcols))
    

    return(A,B)
    
# =============================================================================
# Method to perform stochastic gradient descent (SGD) to optimize the neural network, while running 
# error analysis on train and test data for each epoch (hyperparameter tuning)
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#          (num_epoch): num epochs to run entire SGD process 
#          (learning_rate): how quickly to learn from SGD 
#          (x_test): x data 
#          (y_test): y data 
    
# Args out: (A,B,Jtrain,Jtest): Optimized Neural Network parameters (A,B), train and test error 
# =============================================================================     
def SGD(x,y,A,B,num_epoch,learning_rate,xtest,ytest):
    
    Jtrain = numpy.zeros(num_epoch)
    Jtest = numpy.zeros(num_epoch)

    for i in range(0,num_epoch,1):
        
        for j in range(0,len(x[:,1])):
            
            # Neural Network Forward Propagation Algorithm
            (a,b,z,yhat,J) = NNFORWARD(x[j],y[j],A,B)
            
            # Neural Network Backward Propagation Algorithm
            (ga,gb) =  NNBACKWARD(x[j],y[j],A,B,a,b,z,yhat,J)
           
            # SGD update on A, B
            A = A - learning_rate*ga
            B = B - learning_rate*gb
            
            # Neural Network prediction using forward propagation, and updated A,B parameters
            (an,bn,zn,yhatn,Jtr) = NNFORWARD(x[j],y[j],A,B)

        # Calculate error J on training data
        meanJtrain = get_mean_error(x,y,A,B)      
        meanJtest = get_mean_error(xtest,ytest,A,B)
        
        # Store errors for each epoch for hyperparameter tuning purposes
        Jtrain[i] = meanJtrain
        Jtest[i] = meanJtest
    
    return(A,B,Jtrain,Jtest)
            
# =============================================================================
# Method to get the error J of a feature-label observation set for training or test data
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#              
# Args out: (meanJtrain): mean error (J) for training OR test data
# =============================================================================   
    
def get_mean_error(x, y, A, B):
    
    meanJtrain = 0
    
    for h in range(0,len(x[:,1]),1):
        (atest,btest,zstartest,yhattest,J0) = NNFORWARD(x[h], y[h], A, B)
        meanJtrain = meanJtrain + J0
        
    meanJtrain = meanJtrain/len(x[:,1])
    
    return(meanJtrain)
    
# =============================================================================
# Method to implement the Neural Network Forward Propagation Model
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#              
# Args out: (a,b,zstar,yhat,J): intermediate parameters a,b,zstar, predicted class yhat, error J
# =============================================================================   
def NNFORWARD(x,y,A,B):
    
    # Linear combination at first hidden layer
    a = numpy.matmul(x,A)
       
    # Sigmoid activation at first hidden layer
    z = 1/(1+numpy.exp(-a))
       

    # Add bias term after first hidden layer       
    zstar = numpy.insert(z,0,1)
      
    # Linear combination at second hidden layer
    b = numpy.matmul(numpy.transpose(zstar[:,None]),B)
       
    # Softmax (multi-class classification) output at second hidden layer
    exp_bk = numpy.exp(b)
    sum_exp_bk = numpy.sum(exp_bk)
    yhat = exp_bk/sum_exp_bk
       
    # Cross-entropy loss function
    log_yhat = numpy.log(yhat)
    log_yhat_y = numpy.multiply(log_yhat,y)
    J = -(1)*numpy.sum(log_yhat_y)
       
    return (a,b,zstar,yhat,J)
    
# =============================================================================
# Method to implement the neural network backpropagation algorithm 
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#          (a): intermediate params for first hidden layer generated by NNNForward
#          (b): intermediate params for second hidden layer generated by NNNForward
#          (z): activated first hidden layer generated by NNNForward
#          (yhat): softmax-generated outputs generated by NNNForward
#          (J): loss generated by NNNForward
#              
# Args out: (a,b,zstar,yhat,J): intermediate parameters a,b,zstar, predicted class yhat, error J
# =============================================================================   
def NNBACKWARD(x,y,A,B,a,b,z,yhat,J):
    
    ### Calculate backpropagation partial derivative dl/dA using the chain rule
    dl_db = -(y - yhat)
    db_dz = B[1:,:]
    dz_da = z[1:]*(1-z[1:])
    da_dalpha = x[:,None]
    dl_dz = numpy.matmul(dl_db,numpy.transpose(db_dz))
    dl_da = numpy.multiply(dl_dz,dz_da)
    dl_dalpha = numpy.matmul(da_dalpha,dl_da)
        
    ### Calculate backpropagation partial derivative dl/dB using the chain rule 
    dl_db = -(y - yhat) 
    db_dB = z 
    dl_dB = numpy.matmul(db_dB[:,None],dl_db)
  
    return(dl_dalpha,dl_dB)

# =============================================================================
# Method to write metrics of training error, test error, epoch tuning to file 
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#          (train_out): file location of training metrics
#          (test_out): file location of test metrics
#          (metrics_out): file location of metrics
#          (Jtrain): softmax-generated outputs generated by NNNForward
#          (Jtest): loss generated by NNNForward
#              
# Args out: None - write to file
# =============================================================================   
def write_metrics(x,y,A,B,train_out,test_out,metrics_out, Jtrain, Jtest):
    
    # Write train and test error
    train_error = write_outputs(x,y,A,B,train_out)
    test_error = write_outputs(x,y,A,B,test_out)
    
    with open(metrics_out, mode='w', newline='\n') as f_out:
        for i in range(0,len(Jtrain),1):
            f_out.write("epoch=" + str(i+1) + " crossentropy(train): " + str(Jtrain[i]) + "\n")
            f_out.write("epoch=" + str(i+1) + " crossentropy(test): " + str(Jtest[i]) + "\n")
            
        f_out.write("error(train):" + str(train_error) + "\n")
        f_out.write("error(test):" + str(test_error))
        
# =============================================================================
# Method to write metrics of training error, test error, epoch tuning to file 
# Args in: (x): x data in matrix format
# Args in: (y): y data in one-hot format
# Args in: (A): parameters for first layer
#          (B): parameters for second layer
#          (train_out): file location of training metrics
#          
# Args out: (train_error) - pass train_error back to metrics file for writing
# =============================================================================  
def write_outputs(x,y,A,B,train_out):
    errors_train = 0
    train_error = 0
    with open(train_out, mode='w', newline='\n') as f_out:
        for i in range(0,len(x[:,1])):
            
            (a,b,zstar,yhat,J0) = NNFORWARD(x[i], y[i], A, B)
            
            y_pred = int(numpy.argmax(yhat))
            y_real = int(numpy.argmax(y[i]))
            
            f_out.write(str(y_pred) + '\n')
            if(y_pred!=y_real):
                errors_train+=1
        train_error = errors_train/len(x[:,1])
    return(train_error)
    
###########################
######### Main #########
###########################

if __name__ == '__main__':
    
    # Command-line inputs
    train_input = sys.argv[1]
    test_input = sys.argv[2]
    train_out = sys.argv[3]
    test_out = sys.argv[4]
    metrics_out = sys.argv[5]
    num_epoch = sys.argv[6]
    hidden_units = sys.argv[7]
    init_flag = sys.argv[8]
    learning_rate = sys.argv[9]
    
    # Clean Data
    (num_epochs, hidden_units_int, init_flag_int, learning_rate_num) = clean_command_line(num_epoch, hidden_units, init_flag, learning_rate)
        
    # Read Train & Test
    (y,x) = read_input(train_input)
    (ytest,xtest) = read_input(test_input)

    # Initialize neural network model
    (A,B) = initializeAB(x,y,hidden_units_int,init_flag_int)
    
    # Consolidated for training + testing
    (A,B,Jtrain,Jtest) = SGD(x,y,A,B,num_epochs,learning_rate_num,xtest,ytest)
    
    # Write train and test error
    write_metrics(x,y,A,B,train_out,test_out,metrics_out, Jtrain, Jtest)
    