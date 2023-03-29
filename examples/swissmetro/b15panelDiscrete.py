"""File 15panelDiscrete.py

:author: Michel Bierlaire, EPFL
:date: Tue Dec  6 18:05:51 2022

 Example of a discrete mixture of logit models, also called latent class model.
 The datafile is organized as panel data.
 Three alternatives: Train, Car and Swissmetro
 SP data
"""

import biogeme.biogeme as bio
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import (
    Beta,
    bioDraws,
    PanelLikelihoodTrajectory,
    MonteCarlo,
    log,
)
from swissmetro_panel import (
    database,
    CHOICE,
    SM_AV,
    CAR_AV_SP,
    TRAIN_AV_SP,
    TRAIN_TT_SCALED,
    TRAIN_COST_SCALED,
    SM_TT_SCALED,
    SM_COST_SCALED,
    CAR_TT_SCALED,
    CAR_CO_SCALED,
)
# Parameters to be estimated. One version for each latent class.
NUMBER_OF_CLASSES = 2
B_COST = [
    Beta(f'B_COST_class{i}', 0, None, None, 0) for i in range(NUMBER_OF_CLASSES)
]

# Define a random parameter, normally distributed across individuals,
# designed to be used for Monte-Carlo simulation
B_TIME = [
    Beta(f'B_TIME_class{i}', 0, None, None, 0) for i in range(NUMBER_OF_CLASSES)
]

# It is advised not to use 0 as starting value for the following parameter.
B_TIME_S = [
    Beta(f'B_TIME_S_class{i}', 1, None, None, 0)
    for i in range(NUMBER_OF_CLASSES)
]
B_TIME_RND = [
    B_TIME[i] + B_TIME_S[i] * bioDraws(f'B_TIME_RND_class{i}', 'NORMAL_ANTI')
    for i in range(NUMBER_OF_CLASSES)
]

# We do the same for the constants, to address serial correlation.
ASC_CAR = [
    Beta(f'ASC_CAR_class{i}', 0, None, None, 0) for i in range(NUMBER_OF_CLASSES)
]
ASC_CAR_S = [
    Beta(f'ASC_CAR_S_class{i}', 1, None, None, 0)
    for i in range(NUMBER_OF_CLASSES)
]
ASC_CAR_RND = [
    ASC_CAR[i]
    + ASC_CAR_S[i] * bioDraws(f'ASC_CAR_RND_class{i}', 'NORMAL_ANTI')
    for i in range(NUMBER_OF_CLASSES)
]

ASC_TRAIN = [
    Beta(f'ASC_TRAIN_class{i}', 0, None, None, 0)
    for i in range(NUMBER_OF_CLASSES)
]
ASC_TRAIN_S = [
    Beta(f'ASC_TRAIN_S_class{i}', 1, None, None, 0)
    for i in range(NUMBER_OF_CLASSES)
]
ASC_TRAIN_RND = [
    ASC_TRAIN[i]
    + ASC_TRAIN_S[i] * bioDraws(f'ASC_TRAIN_RND_class{i}', 'NORMAL_ANTI')
    for i in range(NUMBER_OF_CLASSES)
]

ASC_SM = [
    Beta(f'ASC_SM_class{i}', 0, None, None, 1) for i in range(NUMBER_OF_CLASSES)
]
ASC_SM_S = [
    Beta(f'ASC_SM_S_class{i}', 1, None, None, 0)
    for i in range(NUMBER_OF_CLASSES)
]
ASC_SM_RND = [
    ASC_SM[i] + ASC_SM_S[i] * bioDraws(f'ASC_SM_RND_class{i}', 'NORMAL_ANTI')
    for i in range(NUMBER_OF_CLASSES)
]

# Class memebership probability
PROB_class0 = Beta('PROB_class0', 0.5, 0, 1, 0)
PROB_class1 = 1 - PROB_class0

# In class 0, it is assumed that the time coefficient is zero
B_TIME_RND[0] = 0

# Utility functions
V1 = [
    ASC_TRAIN_RND[i]
    + B_TIME_RND[i] * TRAIN_TT_SCALED
    + B_COST[i] * TRAIN_COST_SCALED
    for i in range(NUMBER_OF_CLASSES)
]
V2 = [
    ASC_SM_RND[i] + B_TIME_RND[i] * SM_TT_SCALED + B_COST[i] * SM_COST_SCALED
    for i in range(NUMBER_OF_CLASSES)
]
V3 = [
    ASC_CAR_RND[i] + B_TIME_RND[i] * CAR_TT_SCALED + B_COST[i] * CAR_CO_SCALED
    for i in range(NUMBER_OF_CLASSES)
]
V = [{1: V1[i], 2: V2[i], 3: V3[i]} for i in range(NUMBER_OF_CLASSES)]

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

# The choice model is a discrete mixture of logit, with availability conditions
# We calculate the conditional probability for each class
prob = [
    PanelLikelihoodTrajectory(models.logit(V[i], av, CHOICE))
    for i in range(NUMBER_OF_CLASSES)
]

# Conditional to the random variables, likelihood for the individual.
probIndiv = PROB_class0 * prob[0] + PROB_class1 * prob[1]

# We integrate over the random variables using Monte-Carlo
logprob = log(MonteCarlo(probIndiv))

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob, parameter_file='draws.toml')

biogeme.modelName = '15panelDiscrete'

# Estimate the parameters.
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)