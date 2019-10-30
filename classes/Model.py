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

    def __init__(self, max_preditcions_to_store):
        self.MAX_PREDICTIONS_TO_STORE = max_preditcions_to_store
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
