import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

#import matplotlib.pyplot as plt
#import h5py


def sigmoid(Z):
    """
    Implements the sigmoid activation in numpy

    Arguments:
    Z -- numpy array of any shape

    Returns:
    A -- output of sigmoid(z), same shape as Z
    cache -- returns Z as well, useful during backpropagation
    """

    A = 1/(1+np.exp(-Z))
    cache = Z

    return A, cache

def relu(Z):
    """
    Implement the RELU function.
    Arguments:
    Z -- Output of the linear layer, of any shape
    Returns:
    A -- Post-activation parameter, of the same shape as Z
    cache -- a python dictionary containing "A" ; stored for computing the backward pass efficiently
    """

    A = np.maximum(0,Z)

    assert(A.shape == Z.shape)

    cache = Z
    return A, cache


def relu_backward(dA, cache):
    """
    Implement the backward propagation for a single RELU unit.
    Arguments:
    dA -- post-activation gradient, of any shape
    cache -- 'Z' where we store for computing backward propagation efficiently
    Returns:
    dZ -- Gradient of the cost with respect to Z
    """

    Z = cache
    dZ = np.array(dA, copy=True) # just converting dz to a correct object.

    # When z <= 0, you should set dz to 0 as well.
    dZ[Z <= 0] = 0

    assert (dZ.shape == Z.shape)

    return dZ

def sigmoid_backward(dA, cache):
    """
    Implement the backward propagation for a single SIGMOID unit.
    Arguments:
    dA -- post-activation gradient, of any shape
    cache -- 'Z' where we store for computing backward propagation efficiently
    Returns:
    dZ -- Gradient of the cost with respect to Z
    """

    Z = cache

    s = 1/(1+np.exp(-Z))
    dZ = dA * s * (1-s)

    assert (dZ.shape == Z.shape)

    return dZ


def load_data():
    train_dataset = h5py.File('datasets/train_catvnoncat.h5', "r")
    train_set_x_orig = np.array(train_dataset["train_set_x"][:]) # your train set features
    train_set_y_orig = np.array(train_dataset["train_set_y"][:]) # your train set labels

    test_dataset = h5py.File('datasets/test_catvnoncat.h5', "r")
    test_set_x_orig = np.array(test_dataset["test_set_x"][:]) # your test set features
    test_set_y_orig = np.array(test_dataset["test_set_y"][:]) # your test set labels

    classes = np.array(test_dataset["list_classes"][:]) # the list of classes

    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes


def initialize_parameters(n_x, n_h, n_y):
    """
    Argument:
    n_x -- size of the input layer
    n_h -- size of the hidden layer
    n_y -- size of the output layer

    Returns:
    parameters -- python dictionary containing your parameters:
                    W1 -- weight matrix of shape (n_h, n_x)
                    b1 -- bias vector of shape (n_h, 1)
                    W2 -- weight matrix of shape (n_y, n_h)
                    b2 -- bias vector of shape (n_y, 1)
    """

    np.random.seed(1)

    W1 = np.random.randn(n_h, n_x)*0.01
    b1 = np.zeros((n_h, 1))
    W2 = np.random.randn(n_y, n_h)*0.01
    b2 = np.zeros((n_y, 1))

    assert(W1.shape == (n_h, n_x))
    assert(b1.shape == (n_h, 1))
    assert(W2.shape == (n_y, n_h))
    assert(b2.shape == (n_y, 1))

    parameters = {"W1": W1,
                  "b1": b1,
                  "W2": W2,
                  "b2": b2}

    return parameters


def initialize_parameters_deep(layer_dims):
    """
    Arguments:
    layer_dims -- python array (list) containing the dimensions of each layer in our network

    Returns:
    parameters -- python dictionary containing your parameters "W1", "b1", ..., "WL", "bL":
                    Wl -- weight matrix of shape (layer_dims[l], layer_dims[l-1])
                    bl -- bias vector of shape (layer_dims[l], 1)
    """

    np.random.seed(1)
    parameters = {}
    L = len(layer_dims)            # number of layers in the network

    for l in range(1, L):
        parameters['W' + str(l)] = np.random.randn(layer_dims[l], layer_dims[l-1]) / np.sqrt(layer_dims[l-1]) #*0.01
        parameters['b' + str(l)] = np.zeros((layer_dims[l], 1))

        assert(parameters['W' + str(l)].shape == (layer_dims[l], layer_dims[l-1]))
        assert(parameters['b' + str(l)].shape == (layer_dims[l], 1))


    return parameters

def linear_forward(A, W, b):
    """
    Implement the linear part of a layer's forward propagation.
    Arguments:
    A -- activations from previous layer (or input data): (size of previous layer, number of examples)
    W -- weights matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of the current layer, 1)
    Returns:
    Z -- the input of the activation function, also called pre-activation parameter
    cache -- a python dictionary containing "A", "W" and "b" ; stored for computing the backward pass efficiently
    """

    Z = W.dot(A) + b

    assert(Z.shape == (W.shape[0], A.shape[1]))
    cache = (A, W, b)

    return Z, cache

def linear_activation_forward(A_prev, W, b, activation):
    """
    Implement the forward propagation for the LINEAR->ACTIVATION layer
    Arguments:
    A_prev -- activations from previous layer (or input data): (size of previous layer, number of examples)
    W -- weights matrix: numpy array of shape (size of current layer, size of previous layer)
    b -- bias vector, numpy array of shape (size of the current layer, 1)
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"
    Returns:
    A -- the output of the activation function, also called the post-activation value
    cache -- a python dictionary containing "linear_cache" and "activation_cache";
             stored for computing the backward pass efficiently
    """

    if activation == "sigmoid":
        # Inputs: "A_prev, W, b". Outputs: "A, activation_cache".
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = sigmoid(Z)

    elif activation == "relu":
        # Inputs: "A_prev, W, b". Outputs: "A, activation_cache".
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = relu(Z)

    assert (A.shape == (W.shape[0], A_prev.shape[1]))
    cache = (linear_cache, activation_cache)

    return A, cache

def L_model_forward(X, parameters):
    """
    Implement forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID computation

    Arguments:
    X -- data, numpy array of shape (input size, number of examples)
    parameters -- output of initialize_parameters_deep()

    Returns:
    AL -- last post-activation value
    caches -- list of caches containing:
                every cache of linear_relu_forward() (there are L-1 of them, indexed from 0 to L-2)
                the cache of linear_sigmoid_forward() (there is one, indexed L-1)
    """

    caches = []
    A = X
    L = len(parameters) // 2                  # number of layers in the neural network

    # Implement [LINEAR -> RELU]*(L-1). Add "cache" to the "caches" list.
    for l in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev, parameters['W' + str(l)], parameters['b' + str(l)], activation = "relu")
        caches.append(cache)

    # Implement LINEAR -> SIGMOID. Add "cache" to the "caches" list.
    AL, cache = linear_activation_forward(A, parameters['W' + str(L)], parameters['b' + str(L)], activation = "sigmoid")
    caches.append(cache)

    assert(AL.shape == (1,X.shape[1]))

    return AL, caches

def compute_cost(AL, Y):
    """
    Implement the cost function defined by equation (7).
    Arguments:
    AL -- probability vector corresponding to your label predictions, shape (1, number of examples)
    Y -- true "label" vector (for example: containing 0 if non-cat, 1 if cat), shape (1, number of examples)
    Returns:
    cost -- cross-entropy cost
    """

    m = Y.shape[1]

    # Compute loss from aL and y.
    cost = (1./m) * (-np.dot(Y,np.log(AL).T) - np.dot(1-Y, np.log(1.00000001-AL).T))

    cost = np.squeeze(cost)
    assert(cost.shape == ())

    return cost

def linear_backward(dZ, cache):
    """
    Implement the linear portion of backward propagation for a single layer (layer l)
    Arguments:
    dZ -- Gradient of the cost with respect to the linear output (of current layer l)
    cache -- tuple of values (A_prev, W, b) coming from the forward propagation in the current layer
    Returns:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b
    """
    A_prev, W, b = cache
    m = A_prev.shape[1]

    dW = 1./m * np.dot(dZ,A_prev.T)
    db = 1./m * np.sum(dZ, axis = 1, keepdims = True)
    dA_prev = np.dot(W.T,dZ)

    assert (dA_prev.shape == A_prev.shape)
    assert (dW.shape == W.shape)
    assert (db.shape == b.shape)

    return dA_prev, dW, db

def linear_activation_backward(dA, cache, activation):
    """
    Implement the backward propagation for the LINEAR->ACTIVATION layer.

    Arguments:
    dA -- post-activation gradient for current layer l
    cache -- tuple of values (linear_cache, activation_cache) we store for computing backward propagation efficiently
    activation -- the activation to be used in this layer, stored as a text string: "sigmoid" or "relu"

    Returns:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b
    """
    linear_cache, activation_cache = cache

    if activation == "relu":
        dZ = relu_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)

    elif activation == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)

    return dA_prev, dW, db

def L_model_backward(AL, Y, caches):
    """
    Implement the backward propagation for the [LINEAR->RELU] * (L-1) -> LINEAR -> SIGMOID group

    Arguments:
    AL -- probability vector, output of the forward propagation (L_model_forward())
    Y -- true "label" vector (containing 0 if non-cat, 1 if cat)
    caches -- list of caches containing:
                every cache of linear_activation_forward() with "relu" (there are (L-1) or them, indexes from 0 to L-2)
                the cache of linear_activation_forward() with "sigmoid" (there is one, index L-1)

    Returns:
    grads -- A dictionary with the gradients
             grads["dA" + str(l)] = ...
             grads["dW" + str(l)] = ...
             grads["db" + str(l)] = ...
    """
    grads = {}
    L = len(caches) # the number of layers
    m = AL.shape[1]
    Y = Y.reshape(AL.shape) # after this line, Y is the same shape as AL

    # Initializing the backpropagation
    dAL = - (np.divide(Y, AL) - np.divide(1 - Y, 1 - AL))

    # Lth layer (SIGMOID -> LINEAR) gradients. Inputs: "AL, Y, caches". Outputs: "grads["dAL"], grads["dWL"], grads["dbL"]
    current_cache = caches[L-1]
    grads["dA" + str(L-1)], grads["dW" + str(L)], grads["db" + str(L)] = linear_activation_backward(dAL, current_cache, activation = "sigmoid")

    for l in reversed(range(L-1)):
        # lth layer: (RELU -> LINEAR) gradients.
        current_cache = caches[l]
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA" + str(l + 1)], current_cache, activation = "relu")
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l + 1)] = dW_temp
        grads["db" + str(l + 1)] = db_temp

    return grads

def update_parameters(parameters, grads, learning_rate):
    """
    Update parameters using gradient descent

    Arguments:
    parameters -- python dictionary containing your parameters
    grads -- python dictionary containing your gradients, output of L_model_backward

    Returns:
    parameters -- python dictionary containing your updated parameters
                  parameters["W" + str(l)] = ...
                  parameters["b" + str(l)] = ...
    """

    L = len(parameters) // 2 # number of layers in the neural network

    # Update rule for each parameter. Use a for loop.
    for l in range(L):
        parameters["W" + str(l+1)] = parameters["W" + str(l+1)] - learning_rate * grads["dW" + str(l+1)]
        parameters["b" + str(l+1)] = parameters["b" + str(l+1)] - learning_rate * grads["db" + str(l+1)]

    return parameters

def predict(X, y, parameters):
    """
    This function is used to predict the results of a  L-layer neural network.

    Arguments:
    X -- data set of examples you would like to label
    parameters -- parameters of the trained model

    Returns:
    p -- predictions for the given dataset X
    """

    m = X.shape[1]
    n = len(parameters) // 2 # number of layers in the neural network
    p = np.zeros((1,m))

    # Forward propagation
    probas, caches = L_model_forward(X, parameters)


    # convert probas to 0/1 predictions
    for i in range(0, probas.shape[1]):
        if probas[0,i] > 0.5:
            p[0,i] = 1
        else:
            p[0,i] = 0

    return p
def predict_test(X, parameters):
    """
    This function is used to predict the results of a  L-layer neural network.

    Arguments:
    X -- data set of examples you would like to label
    parameters -- parameters of the trained model

    Returns:
    p -- predictions for the given dataset X
    """

    m = X.shape[1]
    n = len(parameters) // 2 # number of layers in the neural network
    p = np.zeros((1,m))

    # Forward propagation
    probas, caches = L_model_forward(X, parameters)


    # convert probas to 0/1 predictions
    for i in range(0, probas.shape[1]):
        if probas[0,i] > 0.5:
            p[0,i] = 1
        else:
            p[0,i] = 0

    return p

def print_mislabeled_images(classes, X, y, p):
    """
    Plots images where predictions and truth were different.
    X -- dataset
    y -- true labels
    p -- predictions
    """
    a = p + y
    mislabeled_indices = np.asarray(np.where(a == 1))
    plt.rcParams['figure.figsize'] = (40.0, 40.0) # set default size of plots
    num_images = len(mislabeled_indices[0])
    for i in range(num_images):
        index = mislabeled_indices[1][i]

        plt.subplot(2, num_images, i + 1)
        plt.imshow(X[:,index].reshape(64,64,3), interpolation='nearest')
        plt.axis('off')
        plt.title("Prediction: " + classes[int(p[0,index])].decode("utf-8") + " \n Class: " + classes[y[0,index]].decode("utf-8"))


def L_layer_model(X, Y, layers_dims, learning_rate = 0.0075, num_iterations = 300, print_cost=False):#lr was 0.009
    """
    Implements a L-layer neural network: [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID.

    Arguments:
    X -- data, numpy array of shape (num_px * num_px * 3, number of examples)
    Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of shape (1, number of examples)
    layers_dims -- list containing the input size and each layer size, of length (number of layers + 1).
    learning_rate -- learning rate of the gradient descent update rule
    num_iterations -- number of iterations of the optimization loop
    print_cost -- if True, it prints the cost every 100 steps

    Returns:
    parameters -- parameters learnt by the model. They can then be used to predict.
    """

    np.random.seed(1)
    costs = []                         # keep track of cost

    parameters = initialize_parameters_deep(layers_dims)


    # Loop (gradient descent)
    for i in range(0, num_iterations):

        # Forward propagation: [LINEAR -> RELU]*(L-1) -> LINEAR -> SIGMOID.

        AL, caches = L_model_forward(X, parameters)

        # Compute cost.

        cost = compute_cost(AL, Y)

        # Backward propagation.

        grads = L_model_backward(AL, Y, caches)

        # Update parameters.

        parameters = update_parameters(parameters, grads, learning_rate)

        # Print the cost every 100 training example
        if print_cost and i % 100 == 0:
            print ("Cost after iteration %i: %f" %(i, cost))
        if print_cost and i % 100 == 0:
            costs.append(cost)

    # plot the cost

    return parameters

def find_layers():
    train_x, train_y, test_x, test_data = set_data()
    maxa=0
    maxi=0
    maxj = 0
    maxk = 0
    for i in range(38, 50):
        for j in range(0, 50):
            print(i, j)
            for k in range(0, 50):
                layers_dims = [7, i,j,k, 1]
                parameters = L_layer_model(np.transpose(np.array(train_x)[700:]), np.transpose(np.array(train_y)[700:]),layers_dims, num_iterations = 400)
                a = (200 - np.abs(pd.DataFrame((predict(np.transpose(np.array(train_x)[:200]), np.transpose(np.array(train_y)[:200]), parameters)).T)[0] - train_y.reset_index()['Survived']).sum())/200
                if maxa < a:
                    maxa = a
                    maxi = i
                    maxj = j
                    maxk = k
                    print(maxa,maxi, maxj, maxk)

    return maxa,maxi, maxj, maxk

def NN():
    train_x, train_y, test_x, test_data = set_data()
    '25 35 40'
    '26 12 8'
    '27, 36, 14'
    layers_dims = [7, 47, 30, 23, 1]
    parameters = L_layer_model(np.transpose(np.array(train_x)), np.transpose(np.array(train_y)),layers_dims, num_iterations = 4000)
    print('accuracy to the training on NN')
    Y_pred = predict_test(np.transpose(np.array(test_x)), parameters).T
    output=pd.DataFrame(data= {'Survived': Y_pred.T[0].astype(int), 'PassengerId': test_data['PassengerId']})
    output.to_csv('my_submission.csv', index=False)
    return (891 - np.abs(pd.DataFrame((predict(np.transpose(np.array(train_x)), np.transpose(np.array(train_y)), parameters)).T)[0] - train_y.reset_index()['Survived']).sum())/891

def set_data():
    train_data = pd.read_csv("train.csv")
    test_data = pd.read_csv("test.csv")
    answer=pd.read_csv("gender_submission.csv")
    train_data.loc[train_data.Age.isnull(), 'Age'] = train_data.groupby("Pclass").Age.transform('median')
    test_data.loc[test_data.Age.isnull(), 'Age'] = test_data.groupby("Pclass").Age.transform('median')
    train_x=train_data.set_index('PassengerId')

    train_x=train_x.drop(['Name','Ticket','Cabin'], axis=1)

    train_x=train_x.dropna()

    train_y=pd.DataFrame(train_x.get('Survived'))

    train_x=train_x.drop(['Survived'], axis=1)

    train_x["Sex"]= train_x["Sex"].replace('male', 1).replace('female', 0)

    train_x["Embarked"]= train_x["Embarked"].replace('S', 1).replace('C', 2).replace('Q', )
    test_x=test_data.set_index('PassengerId')

    test_x=test_x.drop(['Name','Ticket','Cabin'], axis=1)

    #test_data=test_data.dropna()

    #test_x['Fare'] = test_x.Fare.round(2)
    test_x["Sex"]= test_x["Sex"].replace('male', 1).replace('female', 0)
    test_x["Embarked"]= test_x["Embarked"].replace('S', 1).replace('C', 2).replace('Q', 3)
    test_x = test_x.fillna((test_x['Fare'].mean()))

    # create a scaler object
    std_scaler = StandardScaler()
    std_scaler
    # fit and transform the data
    train_x = pd.DataFrame(std_scaler.fit_transform(train_x), columns=train_x.columns, index= train_x.index)
    test_x = pd.DataFrame(std_scaler.fit_transform(test_x), columns=test_x.columns, index= test_x.index)#.set_index(np.array(range(892,1310)))
    return train_x, train_y, test_x, test_data


from sklearn.base import BaseEstimator, TransformerMixin


class titanic_NN(BaseEstimator, TransformerMixin):

    def __init__(self, Layers_dim= [7, 25, 35, 40, 1], num_it = 100):
        self.layers_dims = Layers_dim
        self.num_iterations = num_it

    def fit(self, X, y):

        self.parameters = L_layer_model(np.transpose(np.array(X)), np.transpose(y),layers_dims = self.layers_dims, num_iterations = self.num_iterations)

        return self

    def predict(self, X, y=None):

        return predict_test(np.transpose(np.array(X)), self.parameters).T

    def score(self, X, y):
        return np.abs((self.predict(X) - np.transpose(y))[0]).sum() / len(y)
def titanic_ColumnTransformer(titanic):

    def gettitle(name):
        return np.array(name.Name.str.split().str.get(0).apply(helper)).reshape(-1,1)

    def helper(title):
        if title in ['Mr.', 'Miss.', 'Mrs.', 'Master.', 'Dr.', 'Rev.']:
            return title
        if title in ['Ms.', 'Lady.']:
            return 'Miss.'
        else:
            return 'Mr.'

    title = FunctionTransformer(gettitle)
    getitle = Pipeline(steps=[
        ('title', title),
        ('cat', OneHotEncoder())
    ])
    ohe = OneHotEncoder(drop='first')

    std = StandardScaler()
    preproc = ColumnTransformer(
        transformers=[
            ('title', getitle, ['Name']),
            ('sex', ohe, ['Sex']),
            ('num', std, ['Age', 'SibSp', 'Parch', 'Fare']),
            ('cat', OneHotEncoder(), ['Pclass'])
        ])
    return preproc.fit_transform(titanic)


def find_NN_layers():
    data = pd.read_csv("train.csv")
    data = data.drop(columns = ['Ticket', 'Cabin', 'Embarked']).set_index('PassengerId')
    data = data.dropna()
    y = data['Survived']
    data = data.drop(columns = ['Survived'])
    X_train, X_test, y_train, y_test = train_test_split(titanic_ColumnTransformer(data), y)
    maxa=0
    maxi=0
    maxj = 0
    maxk = 0
    for i in range(20, 50):
        for j in range(0, 50):
            print(i, j)
            for k in range(0, 50):
                layers_dims = [9, i,j,k, 1]
                a = titanic_NN(layers_dims, 100)
                a.fit(X_train,(np.array(y_train)).reshape(len(y_train),1))
                score = a.score(X_test,(np.array(y_test)).reshape(len(y_test),1))

                if maxa < score:
                    X_train1, X_test1, y_train1, y_test1 = train_test_split(titanic_ColumnTransformer(data), y)
                    a = titanic_NN(layers_dims, 100)
                    a.fit(X_train1,(np.array(y_train1)).reshape(len(y_train1),1))
                    score = a.score(X_test1,(np.array(y_test1)).reshape(len(y_test1),1))
                    if maxa < score:

                        maxa = score
                        maxi = i
                        maxj = j
                        maxk = k
                        print(maxa,maxi, maxj, maxk)

    return maxa,maxi, maxj, maxk

'''

0.825 29 35 33
0.83 30 28 20
0.83 30 29 1
0.825 33 7 38
0.835 34 5 30
0.84 35 29 34



'''
