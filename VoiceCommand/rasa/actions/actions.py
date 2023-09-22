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
        client = pymongo.MongoClient("mongodb://192.168.12.100:27017/")
        db = client["supermarketDB"]
        collection = db["products"]

        # Get product price from MongoDB
        product_data = collection.find_one({"name": product_name})
        print(f"Product Data from MongoDB: {product_data}")
        
        if product_data and "price" in product_data:
            price = product_data["price"]
            response_text = f"ask_price: The price for {product_name} is {price} THB. , product: {product_name}"
            dispatcher.utter_message(text=response_text)
        else:
            response_text = "ask_price: Sorry, I couldn't fetch the price for that product. , product: None"
            dispatcher.utter_message(text=response_text)
        return []

class ActionGetProductLocation(Action):

    def name(self) -> str:
        return "action_get_product_location"
    
    def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product")
        print(f"Received message with product name: {product_name}")
        print("ask_location")

        # Access to MongoDB
        client = pymongo.MongoClient("mongodb://192.168.12.100:27017/")
        db = client["supermarketDB"]
        collection = db["products"]

        # Get product location from MongoDB
        product_data = collection.find_one({"name": product_name})
        print(f"Product Data from MongoDB: {product_data}")

        if product_data and "location" in product_data:
            location = product_data["location"]
            response_text = f"ask_location: The location of {product_name} is {location} THB. Would you like me to guide you there?, product: {product_name}"
            dispatcher.utter_message(text=response_text)
        else:    
            response_text = "ask_location: Sorry, I couldn't fetch the location of that product. , product: None"
            dispatcher.utter_message(text=response_text)
        return []