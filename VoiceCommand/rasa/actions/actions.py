# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# This is a custom action for ServiceRobot

from websocket import create_connection
import json
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import pymongo

class ActionGetProductPrice(Action):
    
    def name(self) -> str:
        return "action_get_product_price"
    
    def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product")
        print(f"Received message with product name: {product_name}")
        print("ask_price")
        # Access to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["supermarketDB"]
        collection = db["products"]

        # Get product price from MongoDB
        product_data = collection.find_one({"name": product_name})
        print(f"Product Data from MongoDB: {product_data}")
        
        if product_data and "price" in product_data:
            price = product_data["price"]
            dispatcher.utter_message(text=f"The price for {product_name} is {price} THB.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't fetch the price for that product.")
        return []

class ActionGetProductLocation(Action):

    def name(self) -> str:
        return "action_get_product_location"
    
    def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product")
        print(f"Received message with product name: {product_name}")
        print("ask_location")

        # Access to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["supermarketDB"]
        collection = db["products"]

        # Get product location from MongoDB
        product_data = collection.find_one({"name": product_name})
        print(f"Product Data from MongoDB: {product_data}")

        if product_data and "location" in product_data:
            location = product_data["location"]

            # Send location data to ROS bridge server
            success = send_to_rosbridge(product_name)
            if success:
                dispatcher.utter_message(text=f"The location of {product_name} is {location}.")
            else:
                dispatcher.utter_message(text=f"The location for {product_name} is {location}, but failed to send to ROS bridge.")
        else:    
            dispatcher.utter_message(text="Sorry, I couldn't fetch the location of that product.")
        return []