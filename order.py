import datetime
from flask import Flask, request, jsonify, flash
from settings import connection, logger, handle_exceptions

app: Flask = Flask(__name__)


"""Admin API"""     # add new values to order_items table
@app.route("/app/v1/<int:user_id>/orders/order_items/add_items ", methods = ["POST"])
@handle_exceptions
def add_new_items_to_order_items_table(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to add new items to cart(order_items) table")

    # Define a lambda function to extract values from JSON data
    extract_key = lambda key: request.json.get(key)

    # Insert new values taken from the user using the lambda function
    user_id = extract_key('userId')
    product_id = extract_key('productId')
    quantity = extract_key('quantity')
    time = datetime.datetime.now()

    # Execute the query to fetch the price of the product with the given
    cur.execute("SELECT price FROM products WHERE product_id = %s", (product_id, ))
    price = cur.fetchone()[0][0]
    subtotal = price * quantity

    # {
    #     "id": user_id,
    #     "product_id": product_id,
    #     "price": price,
    #     "subtotal": subtotal,
    #     "quantity": quantity,
    #     "time_stamp": time,
    # }

    query = """INSERT INTO order_items (user_id, product_id, price, quantity, subtotal, time_stamp) VALUES(%s, %s, %s, %s, %s, %s)"""
    values = (user_id, product_id, price, quantity, subtotal, time)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("New items had been added to cart, hence closing the connection")
    return jsonify({"message": "New items had been added to cart",
                    "details": extract_key})


"""Admin API"""     # add new values to order_table
@app.route("/app/v1/<int:user_id>/orders/add_order", methods = ["POST"], endpoint="add_new_order_to_order_table")
@handle_exceptions
def add_new_order_to_order_table(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to add new orders to order table")

    # Get shipping & billing address from the user table
    cur.execute("SELECT shipping_address, billing_address FROM user WHERE user_id = %s", (user_id, ))
    get_address = cur.fetchone()[0]

    shipping_address = get_address[0]
    billing_address = get_address[1]
    time = datetime.datetime.now()

    # Execute the query to fetch total amount of the cart of given user
    cur.execute("SELECT SUM(subtotal) FROM order_items WHERE user_id = %s", (user_id, ))
    order_total = cur.fetchone()[0][0]

    # {
    #     "order_total": order_total,
    #     "shipping_address": shipping_address,
    #     "billing_address": billing_address,
    #     "time": time,
    # }

    query = """INSERT INTO order_table (user_id, order_total, shipping_address, billing_address, time_stamp) VALUES(%s, %s, %s, %s, %s)"""
    values = (user_id, order_total, shipping_address, billing_address, time)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("New orders has been added, hence closing the connection")
    return jsonify({"message": "New orders has been added"})


"""Admin API"""     # updating values to order_items table
@app.route("/app/v1/<int:user_id>/orders/update_items", methods = ["PUT"], endpoint="updating_details_in_order_items_table")
@handle_exceptions
def updating_details_in_order_items_table(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Starting the db connection to updating items in cart(order_items) table")

    # Check whether the user exists in the table or not
    cur.execute("SELECT * FROM order_items WHERE user_id = %s", (user_id, ))
    get_user = cur.fetchone()[0]
    time = datetime.datetime.now()
    data = request.get_json()

    # if exists check whether product is given or not
    if get_user:
        # Check which product user wants to update accordingly update that product details
        product_id = data.get('productId')

        if product_id:
            cur.execute("UPDATE order_items SET product_id = %s, time_stamp = %s AND user_id = %s", (product_id, time))

            # Execute the query to fetch the price from the product table
            cur.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            price = cur.fetchone()[0][0]
            quantity = data.get('quantity')

            if price:
                cur.execute("UPDATE order_items SET price = %s, time_stamp = %s WHERE product_id = %s AND user_id = %s", (price, product_id, user_id, time))
            if quantity:
                cur.execute("UPDATE order_items SET quantity, time_stamp = %s = %s WHERE product_id = %s AND user_id = %s", (quantity, product_id, user_id, time))

            if price and quantity:
                subtotal = price * quantity
                cur.execute("UPDATE order_items SET subtotal, time_stamp = %s = %s WHERE product_id = %s AND user_id = %s", (subtotal, product_id, user_id, time))

            else:
                return jsonify({"error": "Please provided valid quantity to update subtotal"})
        else:
            return jsonify({"error": "Product doesn't exists please provided valid product id"})

        logger(__name__).warning(f"Details of user with id. {user_id} has been updated in the order_items table, hence closing connection")
        return jsonify({f"Details of user with id. {user_id} has been updated in the order_items table"})

    else:
        logger(__name__).warning(f"User with id. {user_id} not found")
        return jsonify({"message": f"User with id. {user_id} not found"})


"""Admin API"""     # updating values to order table
@app.route("/app/v1/<int:user_id>/orders/<int:order_id> ", methods = ["PUT"], endpoint="updating_details_in_order_table")
@handle_exceptions
def updating_details_in_order_table(user_id, order_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Starting the db connection to update order table")

    # Check whether the user exists in the table or not
    cur.execute("SELECT * FROM order_table WHERE user_id = %s AND order_id = %s", (user_id, order_id))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id. {user_id} not found")
        return jsonify({"message": f"User with id. {user_id} not found"})

    data = request.get_json()

    # Execute the query to fetch total amount of the cart of given user
    cur.execute("SELECT SUM(subtotal) FROM order_items WHERE user_id = %s", (user_id, ))
    order_total = cur.fetchone()[0][0]

    # Get shipping & billing address from the user table
    cur.execute("SELECT shipping_address, billing_address FROM users WHERE user_id = %s", (user_id, ))
    get_address = cur.fetchone()[0]

    shipping_address = get_address[0]
    billing_address = get_address[1]
    time = datetime.datetime.now()

    get_data = {
        "order_total": order_total,
        "shipping_address": shipping_address,
        "billing_address": billing_address,
        "updated at": time
    }

    query = "UPDATE order_table SET (order_total = %s, shipping_address = %s, billing_address = %s) WHERE user_id = %s AND order_id = %s"
    values = (order_total, shipping_address, billing_address, user_id, order_id)

    logger(__name__).warning(f"Details of user id. {user_id} updated, hence closing the connection")
    return jsonify({"message": f"Details of user id. {user_id} updated",
                    "details": get_data})


"Functional API"
@app.route("/app/v1/<int:user_id>/orders/", methods = ["GET"], endpoint="get_order_details_of_user")
@handle_exceptions
def get_order_details_of_user(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Starting the db connection to update order table")

    cur.execute("""SELECT u.user_name, u.phone, u.email,
                o.order_id, o.order_total,
                u.shipping_address, u.billing_address, o.time_stamp 
                FROM order_table o JOIN users u 
                ON order_table.user_id = users.user_id
                WHERE user_id = %s""", (user_id, ))
    get_order = cur.fetchone()[0]
    user_name, phone, email, order_id, order_total, shipping_addr, billing_addr, time = get_order
    data = {
        "id": order_id,
        "user_name": user_name,
        "mobile": phone,
        "email": email,
        "total amt": order_total,
        "shipping_addr": shipping_addr,
        "billing_addr": billing_addr,
        "updated at": time
    }
    logger(__name__).warning(f"Order details of user id. {user_id} displayed, hence closing the connection")
    return jsonify({"message": f"Order details of user id. {user_id} displayed",
                    "details": data})


"Functional API"
@app.route("/app/v1/orders/<int:order_id>", methods = ["GET"], endpoint="get_order_details_of_user")
@handle_exceptions
def get_order_details_of_order_id(order_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Starting the db connection to update order table")

    cur.execute("""SELECT u.user_name, u.phone, u.email, 
            o.order_id, o.order_total,
            o.shipping_address AS ship_addr,
            o.billing_address AS bill_addr, o.time_stamp 
            FROM order_table o JOIN users u ON o.user_id = u.user_id 
            WHERE o.order_id = %s""", (order_id, ))

    get_order = cur.fetchone()[0]
    user_name, phone, email, order_id, order_total, shipping_addr, billing_addr, time = get_order

    data = {
        "id": order_id,
        "user_name": user_name,
        "mobile": phone,
        "email": email,
        "total amt": order_total,
        "shipping_addr": shipping_addr,
        "billing_addr": billing_addr,
        "updated at": time
    }
    logger(__name__).warning(f"Order details of id. {order_id} displayed, hence closing the connection")
    return jsonify({"message": f"Order details of id. {order_id} displayed",
                    "details": data})


"""Admin API"""
@app.route("/app/v1/<int:user_id>/items/<int:product_id>", methods = ["DELETE"], endpoint="deleting_products_from_cart_of_user")
@handle_exceptions
def deleting_products_from_cart_of_user(user_id, product_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to deleting items of user in wishlist table")

    cur.execute("SELECT * FROM order_items WHERE user_id = %s AND product_id = %s", (user_id, product_id ))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found or the product with id. {product_id} is missing")
        return jsonify({"message": f"User with id.{user_id} not found or the product with id. {product_id} is missing"})

    cur.execute("DELETE FROM order_items WHERE user_id = %s AND product_id = %s")
    logger(__name__).warning(f"Products from the cart has been deleted of user id. {user_id}")
    return jsonify({"message": f"Products from the cart has been deleted of user id. {user_id}"})



if __name__ == "__main__":
    app.run(debug=True, port=5000)
