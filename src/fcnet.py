import numpy as np

from src.classifiers import softmax
from src.layers import (linear_forward, linear_backward, relu_forward,
                        relu_backward, dropout_forward, dropout_backward)


def random_init(n_in, n_out, weight_scale=5e-2, dtype=np.float32):
    """
    Weights should be initialized from a normal distribution with standard
    deviation equal to weight_scale and biases should be initialized to zero.

    Args:
    - n_in: The number of input nodes into each output.
    - n_out: The number of output nodes for each input.
    """
    W = None
    b = None
    ###########################################################################
    #                           BEGIN OF YOUR CODE                            #
    ###########################################################################
    W = np.random.normal(scale=weight_scale, size=(n_in, n_out))
    b = np.zeros(n_out)
    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################
    return W, b


class FullyConnectedNet(object):
    """
    Implements a fully-connected neural networks with arbitrary size of
    hidden layers. For a network with N hidden layers, the architecture would
    be as follows:
    [linear - relu - (dropout)] x (N - 1) - linear - softmax
    The learnable params are stored in the self.params dictionary and are
    learned with the Solver.
    """
    def __init__(self, hidden_dims, input_dim=32*32*3, num_classes=10,
                 dropout=0, reg=0.0, weight_scale=1e-2, dtype=np.float32,
                 seed=None):
        """
        Initialise the fully-connected neural networks.
        Args:
        - hidden_dims: A list of the size of each hidden layer
        - input_dim: A list giving the size of the input
        - num_classes: Number of classes to classify.
        - dropout: A scalar between 0. and 1. determining the dropout factor.
        If dropout = 0., then dropout is not applied.
        - reg: Regularisation factor.

        """
        self.dtype = dtype
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.use_dropout = True if dropout > 0.0 else False
        if seed:
            np.random.seed(seed)
        self.params = dict()
        """
        TODO: Initialise the weights and bias for all layers and store all in
        self.params. Store the weights and bias of the first layer in keys
        W1 and b1, the weights and bias of the second layer in W2 and b2, etc.
        Weights and bias are to be initialised according to the Xavier
        initialisation (see manual).
        """
        #######################################################################
        #                           BEGIN OF YOUR CODE                        #
        #######################################################################
        nn_dims = [input_dim] + hidden_dims + [num_classes]

        for i in range(0, self.num_layers):
            curr_id = str(i+1)
            W_id = 'W' + curr_id
            b_id = 'b' + curr_id

            self.params[W_id], self.params[b_id] = random_init(nn_dims[i], nn_dims[i+1])
        #######################################################################
        #                            END OF YOUR CODE                         #
        #######################################################################
        # When using dropout we need to pass a dropout_param dictionary to
        # each dropout layer so that the layer knows the dropout probability
        # and the mode (train / test). You can pass the same dropout_param to
        # each dropout layer.
        self.dropout_params = dict()
        if self.use_dropout:
            self.dropout_params = {"train": True, "p": dropout}
            if seed is not None:
                self.dropout_params["seed"] = seed
        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.
        Args:
        - X: Input data, numpy array of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].
        Returns:
        If y is None, then run a test-time forward pass of the model and
        return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.
        If y is not None, then run a training-time forward and backward pass
        and return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping
        parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        X = X.astype(self.dtype)
        linear_cache = dict()
        relu_cache = dict()
        dropout_cache = dict()
        """
        TODO: Implement the forward pass for the fully-connected neural
        network, compute the scores and store them in the scores variable.
        """
        #######################################################################
        #                           BEGIN OF YOUR CODE                        #
        #######################################################################

        linear_cache[0] = relu_cache[0] = dropout_cache[0] = X
        for i in range(1, self.num_layers+1):
            curr_id = str(i)
            W_id = 'W' + curr_id
            b_id = 'b' + curr_id

            # if current layer is not the output layer
            if i < self.num_layers:

                # linear regression
                if not self.use_dropout:
                    prev_layer_output = relu_cache[i-1]
                else:
                    prev_layer_output = dropout_cache[i-1]

                linear_cache[i] = linear_forward(prev_layer_output, self.params[W_id], self.params[b_id])

                # relu activation
                relu_cache[i] = relu_forward(linear_cache[i])

                # dropout regularization
                if self.use_dropout:
                    dropout_cache[i] = dropout_forward(relu_cache[i], self.dropout_params['p'], self.params[W_id], self.params[b_id])
            
            # if current layer is the output layer
            else:

                # output layer outputs the estimate result of nn, scores
                if not self.use_dropout:
                    prev_layer_output = relu_cache[i-1]
                else:
                    prev_layer_output = dropout_cache[i-1]

                scores = linear_forward(prev_layer_output, self.params[W_id], self.params[b_id])

        #######################################################################
        #                            END OF YOUR CODE                         #
        #######################################################################
        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores
        loss, grads = 0, dict()

        """
        TODO: Implement the backward pass for the fully-connected net. Store
        the loss in the loss variable and all gradients in the grads
        dictionary. Compute the loss with softmax. grads[k] has the gradients
        for self.params[k]. Add L2 regularisation to the loss function.
        NOTE: To ensure that your implementation matches ours and you pass the
        automated tests, make sure that your L2 regularization includes a
        factor of 0.5 to simplify the expression for the gradient.
        """
        #######################################################################
        #                           BEGIN OF YOUR CODE                        #
        #######################################################################
        
        # use softmax to produce intermediate results, loss and dlogits
        loss, dlogits = softmax(scores, y)
        
        # iterate backward, output layer to input layer via hidden layers
        for i in range(self.num_layers, 0, -1):

            # set variable names
            curr_id = str(i)
            W_id = 'W' + curr_id
            b_id = 'b' + curr_id

            # L2 regularization
            loss += 0.5 * self.reg * np.sum(self.params[W_id]**2)

            # retrieve the result of upper layer from cache, prev_layer_output
            prev_layer_output = relu_cache[i-1] if not self.use_dropout else dropout_cache[i-1][0]

            # if current layer is the output layer
            if i == self.num_layers:

                # perform linear bacward regression to update grads for W and b
                dX, grads[W_id], grads[b_id] = linear_backward(dlogits, prev_layer_output, self.params[W_id], self.params[b_id])

            # if current layer is not the output layer
            else:

                # dropout
                if self.use_dropout:
                    mask = dropout_cache[i][1]
                    p, train = self.dropout_params['p'], self.dropout_params['train']

                    dX = dropout_backward(relu_cache[i], mask, p, train)

                # relu
                dX = relu_backward(dX, linear_cache[i])

                # linear
                dX, grads[W_id], grads[b_id] = linear_backward(dX, prev_layer_output, self.params[W_id], self.params[b_id])

            # 
            grads[W_id] += self.reg * self.params[W_id]

        #######################################################################
        #                            END OF YOUR CODE                         #
        #######################################################################
        return loss, grads

