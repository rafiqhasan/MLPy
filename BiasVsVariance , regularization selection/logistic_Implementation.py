#In this part of the exercise, you will extend the implementation of regularized logistic regression where we predicted, admittance of microchips
#from a fabrication plant passes quality assur-ance (QA). During QA, each microchip goes through various tests to ensure it is functioning correctly.

#Suppose you are the product manager of the factory and you have the test results for some microchips on two dierent tests. From these two tests,
#you would like to determine whether the microchips should be accepted or rejected. To help you make the decision, you have a dataset of test results
# on past microchips, from which you can build a logistic regression model.

#You will have the following objective
#1. Plot learning curve to measure Bias Vs Variance
#1. Model to be used( 1, 2, 3 ... ) 
#2. Regularization parameter estimation
import numpy             as np
import matplotlib.pyplot as plt
import scipy.optimize    as opt

################################# All functions Begin ###############################
#Function computeError for logistic regression ( Error value will be between 0 and 1 )
def computeError(theta, X, y):
    # Training set size and initialize J
    m = y.size
    error = 0
    
    #Reshape theta from any shape to Row vector
    colsX = np.shape(X)[1]
    theta = np.reshape(theta,(colsX,1))

    # Convert to matrices
    X = np.mat(X)
    y = np.mat(y)
    theta = np.mat(theta)

    # Predict output as per theta and X
    ypredict = X*theta

    # Convert cost values to probability values => 1* converts true false to 0 and 1s
    ypredict = 1*( ypredict >= 0 )

    #( Error is the scenario when prediction is 1 but given Y is 0 )
    #( Error is the scenario when prediction is 0 but given Y is 1 )
    # Error is the avg of the whole vector of 0s and 1s
    error = np.sum(1*(ypredict != y),axis=0) / m
    #print("Error",error)
    return error

#Compute Sigmoid
def sigmoid(z):
    # Convert to matrices
    z = np.mat(z)

    # Sigmoid function
    s = np.divide(1,( 1 + np.exp(-1 * z)))
    return s

#Function computeCost( Return statement has to be right aligned to def statement) => Regularized
def computeCost(theta, X, y, lam):
    # Training set size and initialize J
    m = y.size
    J = 0
    
    #Reshape theta from any shape to Row vector
    colsX = np.shape(X)[1]
    theta = np.reshape(theta,(colsX,1))

    # Convert to matrices
    X = np.mat(X)
    y = np.mat(y)
    theta = np.mat(theta)

    # Calculate Cost with Theta ( Axis = 0, sum for values in a column )
    J = np.sum(-1 * (np.multiply(np.log(sigmoid(X*theta)),y) + np.multiply(np.log(1 - sigmoid(X*theta)),1-y)),axis=0 )/ m \
        +  \
        ( np.sum(np.power(theta,2),axis=0) - np.power(theta[0,0],2) ) * (lam / (2 * m)) #Subtract contribution of first element
    return J

#Function computeGradient derivative for Theta => Regularized
def computeGradient(theta, X, y, lam):
    # Training set size
    m = y.size
    
    #print("Gradient Run")
    colsX = np.shape(X)[1]
    theta = np.reshape(theta,(colsX,1))

    # Convert to matrices
    X = np.mat(X)
    y = np.mat(y)
    theta = np.mat(theta)

    # For matrix, '*' means matrix multiplication, and the multiply() function is used for element-wise multiplication.
    grad = np.sum(np.multiply(sigmoid(X*theta) - y,X),axis=0) / m
    reg  = theta.T * lam / m

    # Apply regularization => First element of reg has to be reverted back
    temp     = grad[0,0]
    grad     = grad + reg
    grad[0,0] = temp
    
    # Convert matrix grad to Array
    grad = np.asarray(grad).reshape(-1)
    return grad

#Function calcMinGrad => Run FMINCG to compute minimizing theta
def calcMinGrad(init_theta, X, y, lam):
    theta_min = opt.minimize(computeCost,x0=init_theta,jac=computeGradient,args=(X,y,lam),method='CG')
    return theta_min

#Convert 2 dimension features to multiple features by power factorization; Also add ones column
def mapFeature(xval,degree):
    #Calculate number of columns which will be created
    noc     = np.int((degree+1)*(degree+2)/2) - 1
    m       = np.shape(xval)[0]
    
    #Convert to matrices; extract first and second column
    xval    = np.mat(xval)
    x1      = np.mat(xval[:,0])
    x2      = np.mat(xval[:,1])

    #Initialize empty matrix( row , 27 )
    xout    = np.mat(np.zeros(shape=(m,noc)))
    col     = 0

    #start conversion=> X1, X2, X1.^2, X2.^2, X1*X2, X1*X2.^2, etc..
    for i in range(1,degree+1):
        for j in range(0,i+1):
            #Element wise multiplication => Dot product
            xout[:,col] = np.multiply( np.power(x1,(i-j)) , np.power(x2,j) )
            col = col + 1

    #Insert ones as first column into X
    xout = np.insert(xout,0,values=1,axis=1)

    #Return featurized matrix
    return xout

#Determize Z for plotting contour plot with respect to MIN Theta
def calcZ(u, v, theta, model):
    m_z = np.shape(u)[0]

    #Matrification
    u       = np.mat(u)
    v       = np.mat(v)
    theta   = np.mat(theta).T

    #Calculate Z
    z       = np.zeros(shape=(m_z,m_z))         #To store resultant Z for each combo of X1 and X2
    ztempin = np.mat(np.zeros(shape=(1,2)))     #Temporary matrix to pass value to MapFeature

    #Predict output for dummy values
    ztempin[0,0] = -0.4
    ztempin[0,1] = 0.87
    trial = mapFeature(ztempin,model)*theta
    print("Trial prediction: ",trial)

    #U and V are row vectors
    for i in range(0, np.shape(u)[1]):
        for j in range(0, np.shape(v)[1]):
            #Calculate Z
            ztempin[0,0] = u[0,i]
            ztempin[0,1] = v[0,j]
            z[i,j] = mapFeature(ztempin,model)*theta

    #VERY IMPORTANT => Transpose contour output( Took nearly 2 hrs to figure this out )
    return z.T

# Function to plot Train vs CV error on different lambdas( Validation curve )
def regSelectionPlotter(xt,yt,xc,yc,lv_lamb,lc_model,lv_trial,lv_multiplier):
    print("Running regularization estimation")
    #Number of training set examples
    mt      = np.shape(xt)[0]

    #Empty matrix to store error_train and error_cv values
    error_train  = np.zeros(shape=(lv_trial,2))
    error_cv     = np.zeros(shape=(lv_trial,2))

    #Featurize training set
    Xtraintemp  = mapFeature(xt, lc_model)
    Xcvtemp     = mapFeature(xc, lc_model)

    #For different power sizes compute CV and Train set error
    for i in range(lv_trial):
        lv_lamb = lv_lamb * lv_multiplier
        print("Computing errors for regularization:", lv_lamb)
        colsX       = np.shape(Xtraintemp)[1]
        init_theta  = np.zeros((1,colsX)).reshape(-1)
        theta_min   = calcMinGrad(init_theta, Xtraintemp, yt, lv_lamb)

        #Compute error on Train set using the above min Theta
        error_train[i,0] = lv_lamb
        error_train[i,1] = computeError(theta_min.x, Xtraintemp, yt)

        #Compute error on CV set using the above min Theta
        costcv      = computeError(theta_min.x, Xcvtemp, yc)
        error_cv[i,0] = lv_lamb
        error_cv[i,1] = costcv

    #Show plots for each power
    print(error_train)
    print(error_cv)
    plt.plot(error_train[:,0],error_train[:,1],color='blue',label='Train set error')
    plt.plot(error_cv[:,0],error_cv[:,1],color='green',label='CV set error')
    plt.legend(loc='upper right', numpoints=1, ncol=1, fontsize=8)
    plt.xlabel('Regularization parameter')
    plt.show()

# Function to plot Train vs CV error on different model( Validation curve )
def modelSelectionPlotter(xt,yt,xc,yc,lc_lamb,model_size):
    print("Running model estimation")
    #Number of training set examples
    mt      = np.shape(xt)[0]
    model_size = model_size - 1 

    #Empty matrix to store error_train and error_cv values
    error_train  = np.zeros(shape=(model_size,2))
    error_cv     = np.zeros(shape=(model_size,2))

    #For different power sizes compute CV and Train set error
    for i in range(model_size):
        power       = i + 2
        print("Computing errors for model with power:", power)
        Xtraintemp  = mapFeature(xt, power)
        colsX       = np.shape(Xtraintemp)[1]
        init_theta  = np.zeros((1,colsX)).reshape(-1)
        theta_min   = calcMinGrad(init_theta, Xtraintemp, yt, lc_lamb)
        print(theta_min.message)

        #Compute error on Train set using the above min Theta
        error_train[i,0] = power
        error_train[i,1] = computeError(theta_min.x, Xtraintemp, yt) 

        #Compute error on CV set using the above min Theta
        Xcvtemp     = mapFeature(xc, power)
        costcv      = computeError(theta_min.x, Xcvtemp, yc)
        error_cv[i,0] = power
        error_cv[i,1] = costcv

    #Show plots for each power
    plt.plot(error_train[:,0],error_train[:,1],color='blue',label='Train set error')
    plt.plot(error_cv[:,0],error_cv[:,1],color='green',label='CV set error')
    plt.legend(loc='upper right', numpoints=1, ncol=1, fontsize=8)
    plt.xlabel('Degree of polynomial')
    plt.show()

#Learning curve plotter
def learningCurve(xt,yt,xc,yc,lc_lamb):
    print("Running learning curve plotter")
    #Number of training set examples
    mt      = np.shape(xt)[0]

    #Empty matrix to store error_train and error_cv values
    error_train  = np.zeros(shape=(mt,2))
    error_cv     = np.zeros(shape=(mt,2))

    for i in range(mt):
        xt_temp     = xt[0:i+1,:]
        yt_temp     = yt[0:i+1,:]
        xcv_temp    = xc
        
        #Insert ones as first column into X
        xt_temp = np.insert(xt_temp,0,values=1,axis=1)

        #Initialize variables
        colsX       = np.shape(xt_temp)[1]
        init_theta  = np.zeros((1,colsX)).reshape(-1)

        #Calculate best theta and store in error_train
        theta_min        = calcMinGrad(init_theta, xt_temp, yt_temp, lc_lamb)

        #Compute error on Train set using the above min Theta
        error_train[i,0] = i
        error_train[i,1] = computeError(theta_min.x, xt_temp, yt_temp)

        #Calculate error on full XCV set and store in error_cv
        xcv_temp        = np.insert(xcv_temp,0,values=1,axis=1)
        costcv          = computeError(theta_min.x, xcv_temp, yc)
        error_cv[i,0]   = i
        error_cv[i,1]   = costcv

    plt.plot(error_train[:,1],color='blue',label='Train set error')
    plt.plot(error_cv[:,1],color='green',label='CV set error')
    plt.legend(loc='upper right', numpoints=1, ncol=1, fontsize=8)
    plt.xlabel('Training example size')
    plt.show()
    
################################# All functions End #################################

#Load text file data in "data" as per column size in "usecols"
data = np.loadtxt('ex2data2.txt',delimiter=',',usecols=(0,1,2))

#Get size of loaded Data => [118,2]
print("Load size")
print(np.shape(data))

#Random shuffle training input data
data = np.mat(data)
np.random.shuffle(data)

#Divide data into Train(70) , CV(24) and Test(24) sets
dataTrain   = np.mat(data[0:70,:])
dataCV      = np.mat(data[70:94,:])
dataTest    = np.mat(data[94:119,:])

#Notation np.mat is used to convert array "(118,2)" to matrix "(118,2)"
X       = data[:,0:2]
y       = data[:,2]
Xtrain  = dataTrain[:,0:2]
ytrain  = dataTrain[:,2]
Xcv     = dataCV[:,0:2]
ycv     = dataCV[:,2]
Xtest   = dataTest[:,0:2]
ytest   = dataTest[:,2]

#Segrate positive and negative examples
#NONZERO operator in Python works similar to FIND in Octave
posindex = np.nonzero(y[:,0]==1)
negindex = np.nonzero(y[:,0]==0)
pos = X[posindex[0],:]
neg = X[negindex[0],:]

#Scatter Plot Positive and Negative examples
if ( 1 == 2 ):
    #Plot positive negative examples
    plt.scatter(pos[:,0],pos[:,1],marker='+',color='black',label='y = 1')
    plt.scatter(neg[:,0],neg[:,1],marker='o',color='y',label='y = 0')
    plt.xlabel('Microchip Test 1')
    plt.ylabel('Microchip Test 2')
    plt.legend(loc='upper right', numpoints=1, ncol=1, fontsize=8)
    plt.show()

############## Learning curve plot: Bias Vs Variance ##############
# Analyze whether there is a bias or variance
# Important notes:
# 1. Learning curve should always be run for Lambda = 0 or very small and no extra featurization
# 2. Theta should be estimated on Training set for different train sizes
# 3. Estimated theta should be used to compute error(J) on Train and CV set
# 4. Training set error will be computed on training subset train(0:m,:)
# 5. However, CV set error will be computed on full CV set

if 1 == 2:
    learningCurve(Xtrain,ytrain,Xcv,ycv,0.001)
    #Result => High bias plot

###################### End learning curve #########################

################ Model selection: Validation curve ################
# Analyze using plots, which model(power) to chose
# Important notes:
# 1. Since the current model has high bias we need to featurize X
# 2. Use validation curve logic
# 3. Estimated theta should be used to compute error(J) on Train and CV set
# 4. We will run it for 15 power models

if 1 == 2:
    modelSelectionPlotter(Xtrain,ytrain,Xcv,ycv,0.00005,10)
    #Result => Chose model with power = 4

###################### End model selection #########################

###### Regularization parameter selection: Validation curve ########
# Analyze using plots, which value of regularization param to chose
# Important notes:
# 1. Since the current model has high bias we need to featurize X
# 2. Use validation curve logic
# 3. Estimated theta should be used to compute error(J) on Train and CV set
# 4. We will run it on multiples of 0.001 = 0.001 * 5(multiplier)

if 1 == 2:
    #Initialize starting lambda & model to use
    start_lamb  = 0.001
    optim_model = 4
    trials      = 8
    multiplier  = 3

    #Run selection plotter
    regSelectionPlotter(Xtrain,ytrain,Xcv,ycv,start_lamb,optim_model,trials,multiplier)
    #Result => Chose regularization parameter = 0.225

################### End regularization selection #####################

#Featurize input X with degree as estimated(model) and Add ones column too
model   = 4         #As estimated
regulz  = 0.225     #As estimated

X = mapFeature(X,model)
print("Size of X after featurizing: ",np.shape(X))
colsX = np.shape(X)[1]

#Run OPTIMIZE to calculate best theta
init_theta = np.zeros((1,colsX)).reshape(-1)
init_lamb  = regulz
theta_min = calcMinGrad(init_theta, X, y, init_lamb)
print("Minimum found Theta")
print(theta_min)

#Plot computed decision boundary as per THETA
if ( 1 == 1 ):
    print("Plotting contour")
    #Prepare Contour plot grid
    u = np.arange(-1, 1.5, 0.05)
    v = np.arange(-1, 1.5, 0.05)
    z = calcZ(u, v, theta_min.x,model)
    
    #Plot positive negative examples along with computed Contour
    plt.figure()
    plt.scatter(pos[:,0],pos[:,1],marker='+',color='black',label='y = 1')
    plt.scatter(neg[:,0],neg[:,1],marker='o',color='y',label='y = 0')
    cont = plt.contour(u, v, z, levels=[0],legend="Decision boundary")
    plt.xlabel('Microchip Test 1')
    plt.ylabel('Microchip Test 2')
    plt.legend(loc='upper right', numpoints=1, ncol=1, fontsize=8)    
    plt.show()
