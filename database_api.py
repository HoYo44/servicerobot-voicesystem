from flask import Flask, request, jsonify
from pymongo import MongoClient

# Connection setting
client = MongoClient("localhost", 27017)

# Chose database and collection
db = client["supermarketDB"]
products_collection = db["products"]

# Add Product info
@app.route("/add_product", methods=["POST"])
def add_product():
    # Get product info from POST data
    product_data = {
        "name": request.json["product_name"],
        "location": request.json["product_location"],
        "stock": request.json["stock"]
    }

    # Add product info to database
    result = products_collection.insert_one(product_data)

    # Message
    if result.inserted_id:
        return jsonify({"message": "Product added successfully!"}), 201
    else:
        return jsonify({"message": "Failed to add product."}), 500
    
if __name__ == "__main__":
    app.run(debug=True)


# Get Product info
@app.route("/get_product_info", methods=["GET"])
def get_product_info():
    product_name = request.args.get("product_name")

    # Get product info from database
    product = products_collection.find_one({"name": product_name})

    # Return product info
    if product:
        return jsonify({
            "name": product["name"],
            "location": product["location"],
            "stock": product["stock"]
        }), 200
    else:
        return jsonify({"message": "Product not found."}),404

# Update stock
@app.route('/update_stock', methods=['PUT'])
def update_stock():
    product_name = request.json['product_name']
    new_stock = request.json['new_stock']

    # Update product stock
    result = products_collection.update_one({"name": product_name}, {"$set": {"stock": new_stock}})

    # Return message
    if result.modified_count > 0:
        return jsonify({"message": "Stock updated successfully!"}), 200
    else:
        return jsonify({"message": "Failed to update stock or product not found."}), 500

# Delete product
@app.route('/delete_product', methods=['DELETE'])
def delete_product():
    product_name = request.json['product_name']

    # Delete product from database
    result = products_collection.delete_one({"name": product_name})

    # Return message
    if result.deleted_count > 0:
        return jsonify({"message": "Product deleted successfully!"}), 200
    else:
        return jsonify({"message": "Failed to delete product or product not found."}), 404

# Updata product location
@app.route('/update_location', methods=['PUT'])
def update_location():
    product_name = request.json['product_name']
    new_location = request.json['location']

    # Update product location
    result = products_collection.update_one({"name": product_name}, {"$set": {"location": new_location}})

    # Return message
    if result.modified_count > 0:
        return jsonify({"message": "Location updated successfully!"}), 200
    else:
        return jsonify({"message": "Failed to update location or product not found."}), 404

