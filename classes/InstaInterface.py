import time

import requests
import json

from requests.exceptions import ChunkedEncodingError

RESULTS_LIMIT = 9


class InstaInterface:

    config = {}
    errors = []
    reqResponse = None
    reqResult = {}
    obtainedImages = []

    def __init__(self, search_key):

        self.config = {
            "search_key": search_key,
            "res_limit": RESULTS_LIMIT,    # Actually not implemented!
            "type": "",                         # Will belong to { "tag", "user" }
            "search_url": ""
        }

        # Defining the search type and generating the search url
        self.getSearchType(search_key)
        self.generateUrl()
        self.abortOnErrors()

        # Forwarding the request to Instagram
        self.forwardRequest()
        self.abortOnErrors()

        # Cleaning the response
        self.cleanResponse()

    def cleanResponse(self):
        data = []
        if self.config["type"] == "user":
            data = json.loads(self.reqResponse.text.split("window._sharedData = ")[1].split(";</script>")[0])
            data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
            if data == "":
                self.errors.append("Error: the user has a private profile")
            '''# Looking for location...
            print(json.loads(self.reqResponse.text.split("window._sharedData = ")[1].split(";</script>")[0])["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["location"])
            '''
        else:  # if self.config["type"] == "tag":
            self.reqResult = self.reqResponse.json()
            data = self.reqResult["graphql"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]
            '''# Looking for location...
            for k,v in data[0]["node"].items():
                print(k+": [")
                if isinstance(data[0]["node"][k], dict):
                    for p,q in data[0]["node"][k].items():
                        print( "- "+p)
                print("]")
            '''
        self.createImgRef(data)

    def createImgRef(self, data):
        self.obtainedImages.clear()     # otherwise it could be cached!
        for i in range(len(data)):
            d = data[i]["node"]
            # Setup Location
            loc = "None"
            if "location" in d:
                loc = d["location"]
            # Create the ref obj and append it to obtainedImages
            img_ref = {
                "href": d["thumbnail_resources"][1]["src"],
                "short_code": d["shortcode"],
                "location": loc
            }
            self.obtainedImages.append(img_ref)

    def forwardRequest(self):
        try:
            self.reqResponse = requests.get(self.config["search_url"])
        except ChunkedEncodingError:
            print("Error: too many simultaneous requests!!")
            time.sleep(2)
            self.forwardRequest()
        if self.reqResponse.status_code != 200:
            self.errors.append(
                "Error trying to forward the request to Instagram APIs; error no." + str(self.reqResponse.status_code))

    def generateUrl(self):
        if self.config["type"] == "user":
            self.config["search_url"] = 'https://www.instagram.com/' + self.config["search_key"][1:]
        else:
            self.config["search_url"] = 'https://www.instagram.com/explore/tags/' + self.config["search_key"][1:] + "/?__a=1"

    def getSearchType(self, search_key):
        if search_key[:1] == "@":
            self.config["type"] = "user"
        elif search_key[:1] == "#":
            self.config["type"] = "tag"
        else:
            self.errors.append("Unknown search key")

    def printErrors(self):
        if len(self.errors) > 0:
            if len(self.errors) == 1:
                print("An error occurred trying to retrieve photos from Instagram: ")
            else:
                print("Errors occurred trying to retrieve photos from Instagram:")
            for e in self.errors:
                print(e)

    def abortOnErrors(self):
        if len(self.errors) > 0:
            self.printErrors()

    def hasErrors(self):
        return len(self.errors) > 0

    def __del__(self):
        pass
