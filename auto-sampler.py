# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#     Copyright 2019 Erich Kohmann                                              #
#                                                                               #
#     This file is part of IASIC.                                               #
#                                                                               #
#     IASIC is free software: you can redistribute it and/or modify             #
#     it under the terms of the GNU General Public License as published by      #
#     the Free Software Foundation, either version 3 of the License, or         #
#     (at your option) any later version.                                       #
#                                                                               #
#     IASIC is distributed in the hope that it will be useful,                  #
#     but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#     GNU General Public License for more details.                              #
#                                                                               #
#     You should have received a copy of the GNU General Public License         #
#     along with Foobar.  If not, see <https://www.gnu.org/licenses/>.          #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Package:      IASIC
# File:         auto-sampler-py
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  This is the main script that manages the whole IASIC program


import threading

from classes.Sampler import Sampler
from classes.ConfigLoader import ConfigLoader
from classes.LogHandler import LogHandler
from classes.Model import Model

# Configurations
LOG_LEVEL = 3                       # 0 - Errors; 1 - Warnings; 2 - Notices; 3 - Verbose
IS_DEBUG = True
DISABLE_EXISTENCE_CHECK = False     # If True it will avoid to check whether the image has been already processed or not
THREAD_START_AWAITING_TIME = 2      # The time between threads executions (to avoid concurrent API requests)

# Predictions Constants
MIN_PRED_RATIO = .1                 # The minimum prediction ratio to store a given prediction
MIN_PRED_RATIO_TO_STORE = .7        # The minimum sum of predictions probabilities to store
MAX_PREDICTIONS_TO_STORE = 10       # The maximum number of predictions to store for a single image
MAX_SAMPLING_NUMBER = 1             # The (maximum) number of sampling to perform on each configuration

# TODO(v1.1):
#  - Implement a watcher to don't do too many "near" http requests
#       [to prevent ConnectionResetError(104, 'Connection reset by peer'))]
#  - Implement monitor to avoid simultaneous Insta API uses: wait 2 seconds!?
#  - Implement hashtag-locations handler (user-locations already implemented but to be tested!)
#  - Implement auto-commit in the DbInterface


class AutoSampler:

    def __init__(self):
        print("\n\n")

        print("Opening './log' to store logs...")
        self.logHandler = LogHandler(logging_level=3)

        self.logHandler.print("Loading the sampling-configuration file at './config.txt'...", 3)
        self.configLoader = ConfigLoader()

        self.logHandler.print("Loading the TensorFlow model...", 3)
        self.model = Model(MAX_PREDICTIONS_TO_STORE)

        self.logHandler.print("Initializing sampling-threads...", 3)
        self.samplers = []
        self.initSamplingThreads()

        self.logHandler.print("Starting sampling-threads...", 3)
        for samplingThread in self.samplers:
            samplingThread.start()

        self.logHandler.print("Joining sampling-thread, good bye!\n", 3)
        for samplingThread in self.samplers:
            samplingThread.join()

        self.logHandler.print("Sampling end!\n###########################", 3)

    def initSamplingThreads(self):
        run_lock = threading.Lock()
        config = (
            MIN_PRED_RATIO,
            MIN_PRED_RATIO_TO_STORE,
            MAX_SAMPLING_NUMBER
        )
        sampling_id = 0
        for sample in self.configLoader.samplingConfiguration:
            self.logHandler.print("- Initializing auto-sampler... [search_key=\"" + str(
                sample[0]) + "\", period=" + str(
                sample[1]) + " minutes]", 3)
            t = threading.Thread(
                target=Sampler,
                args=(
                    sample,
                    sampling_id,
                    self.logHandler,
                    self.model,
                    config,
                    run_lock,
                    (DISABLE_EXISTENCE_CHECK, THREAD_START_AWAITING_TIME),
                )
            )
            self.samplers.append(t)
            sampling_id += 1


autoSampler = AutoSampler()
