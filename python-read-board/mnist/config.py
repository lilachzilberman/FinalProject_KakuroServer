import os
BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
isTraining = False
size = 28 # Size for the image to be trained
epochs = 2000  # Set number of epochs
batchSize = 50  # batch size
learningRate = 1e-4 # learning rate
trainPercentage = 0.85