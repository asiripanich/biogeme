"""File 03scale.py

:author: Michel Bierlaire, EPFL
:date: Thu Sep  6 15:14:39 2018

 Illustrates heteroscedastic specification. A different scale is
 associated with different segments of the sample.
 Three alternatives: Train, Car and Swissmetro
 SP data

"""

import biogeme.biogeme as bio
from biogeme import models
import biogeme.messaging as msg
from biogeme.expressions import Beta
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
    GROUP,
)


# Parameters to be estimated
ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_SM = Beta('ASC_SM', 0, None, None, 1)
B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)
Scale_group3 = Beta('Scale_group3', 1, 0.001, None, 0)

# Definition of the utility functions
V1 = ASC_TRAIN + B_TIME * TRAIN_TT_SCALED + B_COST * TRAIN_COST_SCALED
V2 = ASC_SM + B_TIME * SM_TT_SCALED + B_COST * SM_COST_SCALED
V3 = ASC_CAR + B_TIME * CAR_TT_SCALED + B_COST * CAR_CO_SCALED

# Scale associated with group 3 is estimated
scale = (GROUP != 3) + (GROUP == 3) * Scale_group3

# Scale the utility functions, and associate them with the numbering
# of alternatives
V = {1: scale * V1, 2: scale * V2, 3: scale * V3}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

# Definition of the model. This is the contribution of each
# observation to the log likelihood function.
logprob = models.loglogit(V, av, CHOICE)

# Define level of verbosity
logger = msg.bioMessage()
logger.setSilent()
# logger.setWarning()
# logger.setGeneral()
# logger.setDetailed()

# These notes will be included as such in the report file.
USER_NOTES = (
    'Illustrates heteroscedastic specification. A different scale is'
    ' associated with different segments of the sample.'
)

# Create the Biogeme object
biogeme = bio.BIOGEME(database, logprob, user_notes=USER_NOTES)
biogeme.modelName = '03scale'

# Estimate the parameters
results = biogeme.estimate()
pandasResults = results.getEstimatedParameters()
print(pandasResults)
