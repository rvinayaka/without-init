import datetime
from flask import Flask, request, jsonify, flash, redirect, url_for
from settings import connection, logger, handle_exceptions

app: Flask = Flask(__name__)


"""Admin API"""
@app.route("/app/v1/users/<int:user_id>/recently_viewed/add", methods = ["POST"])
@handle_exceptions
def adding_views_in_recently_viewed_list(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in recently viewed table")

    # Define a lambda function to extract values from JSON data
    extract_key = lambda key: request.json.get(key)

    # Insert new values taken from the user using the lambda function
    user_id = extract_key('userId')
    product_id = extract_key('productId')
    reviews_count = extract_key('reviewsCount')
    time = datetime.datetime.now()

    # {
    #     "user_id": 1,
    #     "product_id": 93,
    #     "time": '1993-07-21'
    # }
    cur.execute("SELECT  FROM recently_viewed WHERE user_id =%s", (user_id, ))
    user_already_exists = cur.fetchone()

    if user_already_exists:
        flash(f"User with id {user_id} already exists")
        return redirect(url_for("update_details_of_user_in_recently_viewed", user_id=user_id, product_id=product_id, reviews_count = reviews_count))


    query = """INSERT INTO recently_viewed (user_id, product_id, reviews_count, time_stamp) VALUES(%s, %s, %s, %s)"""
    values = (user_id, product_id, reviews_count, time)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Inserting views successful, hence closing the connection")
    return jsonify({"message": "Views has been added",
                    "details": extract_key})


"""Functional API"""
@app.route("/app/v1/users/<int:user_id>/recently_viewed/add", methods = ["GET"], endpoint="get_views_of_user_in_recently_viewed")
@handle_exceptions
def get_views_of_user_in_recently_viewed(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in recently viewed table")

    cur.execute("SELECT u.user_name, r.email, r.reviews_count, "
                "FROM recently_viewed r JOIN users u ON r.user_id = u.user_id"
                "WHERE user_id = %s", (user_id, ))
    get_user = cur.fetchone()[0]
    user_name, email, count = get_user

    data = {
        "userName": user_name,
        "email": email,
        "viewsCount": count
    }

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found")
        return jsonify({"message": "User not found in recently viewed list"})

    logger(__name__).debug(f"Views of user id. {user_id} displayed")

    logger(__name__).warning("User views shown, closing the connection")
    return jsonify({"message": f"Views of user id. {user_id} displayed",
                    "details": data})


"""Admin API"""
@app.route("/app/v1/<int:user_id>/recently_viewed/<int:product_id>/counts", methods = ["PUT"], endpoint="update_details_of_user_in_recently_viewed")
@handle_exceptions
def update_details_of_user_in_recently_viewed(user_id, product_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in recently viewed table")

    # Fetch count of recently viewed products for current user
    cur.execute("SELECT COUNT(*) FROM recently_viewed WHERE user_id = %s", (user_id, ))
    count = cur.fetchone()[0][0]

    if not count:
        return jsonify({"message": "User doesn't exist"})

    # If count is greater than or equal to max, delete oldest record
    if count >= 10:
        cur.execute("SELECT MIN(time_stamp) FROM recently_viewed WHERE user_id = %s", (user_id, ))
        oldest_time = cur.fetchone()[0]
        cur.execute("DELETE FROM recently_viewed WHERE user_id = %s AND time_stamp = %s", (user_id, oldest_time))

    # Define a lambda function to extract values from JSON data
    extract_key = lambda key: request.json.get(key)

    # Insert new values taken from the user using the lambda function
    reviews_count = extract_key('reviewsCount')
    time = datetime.datetime.now()

    query = """UPDATE recently_viewed SET product_id = %s, reviews_count = %s, time_stamp = %s WHERE user_id = %s"""
    values = (product_id, reviews_count, time, user_id)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Updating views count successful, hence closing the connection")
    return jsonify({"message": "Views has been updated",
                    "details": extract_key})


"""Admin API"""
@app.route("/app/v1/<int:user_id>/recently_viewed/remove/<int:product_id>", methods = ["DELETE"], endpoint="deleting_views_of_user")
@handle_exceptions
def deleting_views_of_user(user_id, product_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to deleting items of user in wishlist table")

    cur.execute("SELECT * FROM recently_viewed WHERE user_id = %s AND product_id = %s", (user_id, product_id ))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found or the product with id. {product_id} is missing")
        return jsonify({"message": f"User with id.{user_id} not found or the product with id. {product_id} is missing"})

    cur.execute("DELETE FROM recently_viewed WHERE user_id = %s AND product_id = %s")
    logger(__name__).warning(f"Views of user with id. {user_id} has been deleted")
    return jsonify({"message": f"Views of user with id. {user_id} has been deleted"})


"""Admin API"""
@app.route("/app/v1/wishlist/<int:user_id>/clear", methods = ["DELETE"], endpoint="clearing_views_of_user")
@handle_exceptions
def clearing_views_of_user(user_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to deleting all items of user in wishlist table")

    cur.execute("SELECT * FROM recently_viewed WHERE user_id = %s", (user_id, ))
    get_user = cur.fetchone()[0]

    if not get_user:
        logger(__name__).warning(f"User with id.{user_id} not found")
        return jsonify({"message": f"User with id.{user_id} not found"})

    cur.execute("DELETE FROM recently_viewed WHERE user_id = %s")
    logger(__name__).warning(f"Clearing all views of user with id. {user_id}")
    return jsonify({"message": f"Clearing all views of user with id. {user_id}"})




if __name__ == "__main__":
    app.run(debug=True, port=5000)
