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
#     along with IASIC.  If not, see <https://www.gnu.org/licenses/>.          #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Package:      IASIC
# File:         classes/Model.py
# Author:       Erich Kohmann (erich.kohmann@gmail.com)
# Description:  This class handles all about the Keras-mobilenet model,
#               loading it with `imagenet` weights and using such a model
#               to predict instagram sampled images


from tensorflow import keras
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input, decode_predictions
import numpy as np

IMG_HEIGHT = 224
IMG_WIDTH = 224


class Model:

    errors = []
    model = None
    MAX_PREDICTIONS_TO_STORE = 0

    def __init__(self, max_predictions_to_store):
        self.MAX_PREDICTIONS_TO_STORE = max_predictions_to_store
        self.loadModel()

    def predict(self, img_path):
        if self.model is None:
            self.errors.append("Error: no model loaded")
            return False

        x = self.preprocessImage(img_path)
        predictions = self.model.predict(x)

        decoded_pred = decode_predictions(predictions, top=self.MAX_PREDICTIONS_TO_STORE)[0]

        return decoded_pred

    @staticmethod
    def preprocessImage(img_path):
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        return x

    def loadModel(self):
        if self.model is None:
            self.model = keras.applications.mobilenet.MobileNet(input_shape=None, alpha=1.0, depth_multiplier=1, dropout=1e-3, include_top=True, weights='imagenet', input_tensor=None, pooling=None, classes=1000)
