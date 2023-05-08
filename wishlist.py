from flask import Flask, request, jsonify
from settings import connection, logger, handle_exceptions

app: Flask = Flask(__name__)


"""Admin API"""
@app.route("/app/v1/wishlist/add", methods = ["POST"])
@handle_exceptions
def add_items_to_wishlist():
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in wishlist table")

    # Define a lambda function to extract values from JSON data
    extract_key = lambda key: request.json.get(key)

    # Get values from the user using the lambda function
    user_id = extract_key('userId')
    product_id = extract_key('productId')
    time = extract_key('time')
    # {
    #     "user_id": 1
    #     "product_id": 2
    #     "time": '2021-02-04'
    # }


    query = """INSERT INTO wishlist (user_id, product_id, time) VALUES(%s, %s, %s)"""
    values = (user_id, product_id, time)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Inserting value successful, hence closing the connection")
    return jsonify({"message": "New items added to wishlist", "details": extract_key})


"""Functional API"""
@app.route("/app/v1/wishlist/<int:user_id>", methods = ["GET"], endpoint="get_items_of_user_in_wishlist")
@handle_exceptions
def get_items_of_user_in_wishlist(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to get items of user from wishlist table")

    cur.execute("SELECT w.product_id, p.product_name, p.price, p.description "
                "FROM wishlist w JOIN products p ON w.product_id = p.product_id "
                "WHERE user_id = %s", (user_id, ))
    get_user = cur.fetchone()[0]

    product_id, name, price, desc = get_user

    data = {
        "product_id": product_id,
        "product_name": name,
        "price": price,
        "desc": desc
    }

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found")
        return jsonify({"message": f"User with id.{user_id} not found"})

    logger(__name__).warning(f"Wishlist items of user with id. {user_id} has been displayed")
    return jsonify({"message": f"Wishlist items of user with id. {user_id} has been displayed",
                    "details": data})


"""Admin API"""
@app.route("/app/v1/wishlist/<int:user_id>/remove/<int:product_id>", methods = ["DELETE"], endpoint="delete_items_of_user_in_wishlist")
@handle_exceptions
def delete_items_of_user_in_wishlist(user_id, product_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to deleting items of user in wishlist table")

    cur.execute("SELECT * FROM wishlist WHERE user_id = %s AND product_id = %s", (user_id, product_id ))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found or the product with id. {product_id} is missing")
        return jsonify({"message": f"User with id.{user_id} not found or the product with id. {product_id} is missing"})

    cur.execute("DELETE FROM wishlist WHERE user_id = %s AND product_id = %s")
    logger(__name__).warning(f"Wishlist items of user with id. {user_id} has been deleted")
    return jsonify({"message": f"Wishlist items of user with id. {user_id} has been deleted",
                    "details": get_user})


"""Admin API"""
@app.route("/app/v1/wishlist/<int:user_id>/clear", methods = ["DELETE"], endpoint="delete_items_of_user_in_wishlist")
@handle_exceptions
def clear_wishlist_of_user(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to deleting all items of user in wishlist table")

    cur.execute("SELECT * FROM wishlist WHERE user_id = %s", (user_id, ))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found")
        return jsonify({"message": f"User with id.{user_id} not found"})

    cur.execute("DELETE FROM wishlist WHERE user_id = %s")
    logger(__name__).warning(f"Wishlist of user with id. {user_id} has been cleared")
    return jsonify({"message": f"Wishlist of user with id. {user_id} has been cleared",
                    "details": get_user})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
