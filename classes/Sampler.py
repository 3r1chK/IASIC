import os
import time
import urllib.request
from PIL import Image
import datetime
import hashlib
from classes.DbInterface import DbInterface
from classes.InstaInterface import InstaInterface


class Sampler:

    def __init__(self, sample, sampling_id, log_handler, model, conf, run_lock, const):
        self.DISABLE_EXISTENCE_CHECK = const[0]
        self.THREAD_START_AWAITING_TIME = const[1]
        self.lock = run_lock
        self.config = {
            "MIN_PRED_RATIO": conf[0],
            "MIN_PRED_RATIO_TO_STORE": conf[1],
            "MAX_SAMPLING_NUMBER": conf[2]
        }
        self.iterations = 0
        self.samplingExecution(sample, sampling_id, log_handler, model)

    def samplingExecution(self, sample, sampling_id, log_handler, model):

        # Try to acquire the running-lock and once acquired wait THREAD_START_AWAITING_TIME sec
        self.lock.acquire()
        time.sleep(self.THREAD_START_AWAITING_TIME)

        # Begin the real sampling iteration
        self.iterations += 1
        log_handler.write("Thread no." + str(sampling_id) + " begins the execution n." + str(self.iterations) + ".")

        output = "{\n"
        output += " " + str(datetime.datetime.now()) + ": Sampling using " + sample[0] + " as search key\n"

        # Initialize a db interface
        db_interface = DbInterface(log_handler)

        # Get photo info by the Instagram Public Interface
        insta_interface = InstaInterface(sample[0])
        if insta_interface.hasErrors():
            err_mess = ""
            if len(insta_interface.errors) == 1:
                err_mess = "Error occurred trying to query the instagram public interface: "+insta_interface.errors[0]
            else:
                err_mess = "Errors occurred trying to query the instagram public interface: "
                for err in insta_interface.errors:
                    err_mess += "\n- "+str(err)
            log_handler.write(err_mess, 0)
            return False

        # Get binary photos, classify them and store them and the result into the db
        for image_index in range(len(insta_interface.obtainedImages)):

            output += " img n. " + str(image_index) + ":"

            if image_index > len(insta_interface.obtainedImages):
                output += " something strange just happened: the image isn't anymore in memory... skipping this!\n"

            else:
                # Check if the photo has been already processed in the past
                if db_interface.instaUrlAlreadyExists(insta_interface.obtainedImages[image_index]["href"]) \
                        and not self.DISABLE_EXISTENCE_CHECK:
                    output += " image already classified: skipping this!\n"

                else:
                    # TODO(v1.1): you may(be have) to divide the following "processImage()" into two parts:
                    #  - preprocessImage, which will be executed once for each image and...
                    #  - processImages, which will take a list of "db_entry" obtained storing all "preprocessImage()"
                    #    outputs and then it will evaluate and save results of all the images in one time.
                    output = self.processImage(db_interface, image_index, insta_interface, model, output, sample)

        # Make sure that the recursive call will not use the same interfaces
        db_interface.__del__()
        insta_interface.__del__()

        # Greetings before than sleep!
        self.printSamplingOutput(output, sample, log_handler)

        # Release the running-lock
        self.lock.release()

        # Let's sleep!
        time.sleep(int(sample[1])*60)

        # Recursively call my-self
        if self.iterations < self.config["MAX_SAMPLING_NUMBER"]:
            self.samplingExecution(sample, sampling_id, log_handler, model)

    def processImage(self, db_interface, image_index, insta_interface, model, output, sample):
        # Download the binary image using urllib
        im, output = self.downloadImage(db_interface, image_index, insta_interface, output)
        if im is None:
            output += " Ooops! Image already (downloaded and) classified: skipping this!\n"
            return output

        # Generate a name and store the image in the filesystem
        im_new_path, output = self.saveImageBinary(im, output, sample)

        # Evaluate the image
        predictions, output = self.evaluateImage(im_new_path, model, output)
        if len(predictions) == 0:
            output += " Ooops! Error trying to classify this image!\n"
            return output

        # Creating the db entry
        db_entry = self.generateDbEntry(im, im_new_path, image_index, insta_interface)
        if len(db_entry) == 0:
            output += " something strange just happened: the image isn't anymore in memory... skipping! this\n"
            return output

        # Choose which predictions needs to be stored in the db
        pred_to_store = self.choosePredToSave(predictions)

        # Define the correct image status
        output = self.setEntryStatus(db_entry, output, pred_to_store[0][2])

        # Define and store the image location, if available
        output = self.saveImageLocation(db_interface, insta_interface, image_index, db_entry, output)

        # Saving predictions and obtaining the first "prediction_id" available
        self.savePredictions(db_interface, db_entry, pred_to_store)

        # Saving the image entry
        output = self.saveImageEntry(db_interface, db_entry, output)

        return output

    @staticmethod
    def printSamplingOutput(output, sample, log_handler):
        output += " I'll back in " + sample[1] + " minute/s.\n "
        output += str(datetime.datetime.now()) + ": See you!\n"
        output += "}\n"
        log_handler.print(output, 3)

    @staticmethod
    def saveImageEntry(db_interface, db_entry, output):
        db_interface.storeImageEntry(db_entry)
        output += ", saved to the persistent db.\n"
        return output

    @staticmethod
    def savePredictions(db_interface, db_entry, pred_to_store):
        db_entry["prediction_id"] = db_interface.storePredictions(pred_to_store)

    @staticmethod
    def setEntryStatus(db_entry, output, max_predicted_ratio):
        if max_predicted_ratio > .7:
            db_entry["status"] = "VERIFIED"
        elif max_predicted_ratio > .4:
            db_entry["status"] = "PENDING"
        output += " with status " + db_entry["status"]
        return output

    def choosePredToSave(self, predictions):
        # example of decoded_pred:
        # [(u'n02504013', u'Indian_elephant', 0.82658225),
        # (u'n01871265', u'tusker', 0.1122357), (u'n02504458', u'African_elephant', 0.061040461)]
        pred_to_store = []
        tot_ratio = .0
        pred_index = 0
        while tot_ratio < self.config["MIN_PRED_RATIO_TO_STORE"] or pred_index >= len(predictions):
            if predictions[pred_index][2] < self.config["MIN_PRED_RATIO"]:
                break
            pred_to_store.append(predictions[pred_index])
            tot_ratio += predictions[pred_index][2]
            pred_index += 1

        if len(pred_to_store) == 0:
            pred_to_store.append(predictions[0])

        return pred_to_store

    @staticmethod
    def generateDbEntry(im, im_new_path, image_index, insta_interface):
        if image_index > len(insta_interface.obtainedImages):
            return {}
        db_entry = {
            "status": "UNCERTAIN",
            "is_human_verified": False,
            "prediction_id": None,
            "uri": im_new_path,
            "insta_url": insta_interface.obtainedImages[image_index]["href"],
            "sha256_digest": hashlib.sha256(im.tobytes()).hexdigest(),
            "location_id": 0
        }
        return db_entry

    @staticmethod
    def evaluateImage(im_new_path, model, output):
        predictions = model.predict(im_new_path)
        if len(predictions) == 0:
            return [], output
        output += ", classified as \"" + str(predictions[0][1]) + "\" (" + str(predictions[0][2]) + ")"
        return predictions, output

    def saveImageBinary(self, im, output, sample):
        if im is None:
            output += " [NOTHING TO SAVE]!"
            return "", output
        im_new_path = self.generateNewImagePath(sample)
        im.save(im_new_path, "JPEG")
        output += ", saved at " + im_new_path
        return im_new_path, output

    def generateNewImagePath(self, sample):
        rel_dir_name = str(datetime.date.today().isoformat())
        image_name = str(datetime.datetime.now().isoformat()) + "_wk_" + str(sample[0])
        image_extension = "jpeg"
        image_db_path = "db/images"
        directory_name = image_db_path + "/" + rel_dir_name
        self.checkSavageDirectory(directory_name)
        im_new_path = directory_name + "/" + image_name + "." + image_extension
        return im_new_path

    def downloadImage(self, db_interface, image_index, insta_interface, output):
        image = urllib.request.urlretrieve(insta_interface.obtainedImages[image_index]["href"])
        im = Image.open(image[0])
        output += " downloaded"
        if db_interface.fileAlreadyExists(hashlib.sha256(im.tobytes()).hexdigest()) and not self.DISABLE_EXISTENCE_CHECK:
            im = None
        return im, output

    @staticmethod
    def checkSavageDirectory(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def saveImageLocation(db_interface, insta_interface, image_index, db_entry, output):
        # Define and store the image location if available
        l = insta_interface.obtainedImages[image_index]["location"]
        if l != "None" and l is not None:
            print("##########\n\n img " + str(image_index) + " localized at ", l, " \n\n##########")
            db_entry["location_id"] = db_interface.storeLocation(l)
            output += " localized at "+l["name"]+" (lat "+str(l["lat"])+", lng "+str(l["lng"])+")"
        return output
