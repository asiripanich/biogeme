"""File 07discreteMixture.py

:author: Michel Bierlaire, EPFL
:date: Sun Sep  8 00:06:20 2019

 Example of a discrete mixture of logit (or latent class model)
 Three alternatives: Train, Car and Swissmetro
 SP data
"""

import biogeme.biogeme as bio
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import Beta, log

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
B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)

PROB_CLASS1 = Beta('PROB_CLASS1', 0.5, 0, 1, 0)
PROB_CLASS2 = 1 - PROB_CLASS1

# Definition of the utility functions for latent class 1, where the
# time coefficient is zero
V11 = ASC_TRAIN + B_COST * TRAIN_COST_SCALED
V12 = ASC_SM + B_COST * SM_COST_SCALED
V13 = ASC_CAR + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V1 = {1: V11, 2: V12, 3: V13}

# Definition of the utility functions for latent class 2, whete the
# time coefficient is estimated
V21 = ASC_TRAIN + B_TIME * TRAIN_TT_SCALED + B_COST * TRAIN_COST_SCALED
V22 = ASC_SM + B_TIME * SM_TT_SCALED + B_COST * SM_COST_SCALED
V23 = ASC_CAR + B_TIME * CAR_TT_SCALED + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V2 = {1: V21, 2: V22, 3: V23}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}


# The choice model is a discrete mixture of logit, with availability conditions
prob1 = models.logit(V1, av, CHOICE)
prob2 = models.logit(V2, av, CHOICE)
prob = PROB_CLASS1 * prob1 + PROB_CLASS2 * prob2
logprob = log(prob)

# Define level of verbosity
logger = msg.bioMessage()
logger.setSilent()
# logger.setWarning()
# logger.setGeneral()
# logger.setDetailed()

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob)
biogeme.modelName = '07discreteMixture'

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)
