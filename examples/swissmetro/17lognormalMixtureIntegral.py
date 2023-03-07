"""File 17lognormalMixtureIntegral.py

:author: Michel Bierlaire, EPFL
:date: Mon Sep  9 10:08:21 2019

 Example of a mixture of logit models, using numerical integration.
 The mixing distribution is distributed as a log normal.
 Three alternatives: Train, Car and Swissmetro
 SP data
"""

import biogeme.biogeme as bio
import biogeme.distributions as dist
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import (
    Beta,
    RandomVariable,
    exp,
    log,
    Integrate,
)
from swissmetro import (
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

# Parameters to be estimated
ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_SM = Beta('ASC_SM', 0, None, None, 1)
B_COST = Beta('B_COST', 0, None, None, 0)

# Define a random parameter, normally distributed, designed to be used
# for Monte-Carlo simulation
B_TIME = Beta('B_TIME', 0, None, None, 0)

# It is advised not to use 0 as starting value for the following parameter.
B_TIME_S = Beta('B_TIME_S', 1, None, None, 0)

# Define a random parameter, log normally distributed, designed to be used
# for Monte-Carlo simulation.
omega = RandomVariable('omega')
B_TIME_RND = -exp(B_TIME + B_TIME_S * omega)
density = dist.normalpdf(omega)

# Definition of the utility functions
V1 = ASC_TRAIN + B_TIME_RND * TRAIN_TT_SCALED + B_COST * TRAIN_COST_SCALED
V2 = ASC_SM + B_TIME_RND * SM_TT_SCALED + B_COST * SM_COST_SCALED
V3 = ASC_CAR + B_TIME_RND * CAR_TT_SCALED + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V = {1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

# Conditional to omega, we have a logit model (called the kernel)
condprob = models.logit(V, av, CHOICE)

# We integrate over omega using numerical integration
logprob = log(Integrate(condprob * density, 'omega'))

# Define level of verbosity
logger = msg.bioMessage()
# logger.setSilent()
# logger.setWarning()
logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = '17lognormalMixtureIntegral'

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)
