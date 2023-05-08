from flask import Flask, request, jsonify
from settings import connection, logger, handle_exceptions

app: Flask = Flask(__name__)

#  vendor_id | vendor_name | seller_contact | address
# -----------+-------------+----------------+---------

# id | vendor_id | user_id | ratings | review | time | vendor_feedback | product_id
# ----+-----------+---------+---------+--------+------+-----------------+------------

# to add seller details

"""Admin API"""
@app.route("/app/v1/<int:product_id>/vendor_rating/insert", methods = ["POST"])
@handle_exceptions
def add_new_vendor_ratings_of_product(product_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in vendor ratings table")

    # Get values from the user
    data = request.get_json()
    vendor_id = data.get('vendorId')
    user_id = data.get('userId')
    ratings = data.get('ratings')
    review = data.get("review")
    time = data.get('time')
    feedback = data.get('feedback')

    # {
    #     "vendorId": 101,
    #     "userId": 20,
    #     "ratings": 3.0,
    #     "review": "Nice work",
    #     "time": "2011-08-29",
    #     "feedback": "Thanks for the feedback"
    # }

    if not all([vendor_id, user_id, ratings, review, time, feedback]):
        return jsonify({"error": "Given data is insufficient, check all the values properly"})

    query = """INSERT INTO vendor_ratings (vendor_id, user_id, ratings, review, 
                    time, vendor_feedback, product_id) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
    values = (vendor_id, user_id, ratings, review, time, feedback, product_id)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Inserting value successful, hence closing the connection")
    return jsonify({"message": "New vendor ratings added", "details": data})


"""Admin API"""
# to add vendor details
@app.route("/app/v1/vendor", methods = ["POST"], endpoint="add_new_vendors")
@handle_exceptions
def add_new_vendors():
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to insert values in vendor table")

    # Get values from the user
    data = request.get_json()
    vendor_name = data.get('name')
    contact = data.get('contact')
    address = data.get('address')

    # {
    #     "name": "XYZ Company",
    #     "contact": 90245252,
    #     "address": "402, street, colony"
    # }

    if not all([vendor_name, contact, address]):
        return jsonify({"error": "Given data is insufficient, check all the values properly"})

    query = """INSERT INTO vendor (vendor_name, vendor_contact, address) VALUES(%s, %s, %s)"""
    values = (vendor_name, contact, address)

    # Execute the query using values
    cur.execute(query, values)

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Inserting value successful, hence closing the connection")
    return jsonify({"message": "New vendor added", "details": data})


"""Functional API"""
@app.route("/app/v1/<int:product_id>/vendor_rating/<int:vendor_id>", methods=["GET"], endpoint='checkout')    # Calculate the total price
@handle_exceptions
def vendor_ratings_of_current_product(product_id, vendor_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Starting the db connection to get all vendor")

    cur.execute("SELECT * from vendor_ratings WHERE vendor_id = %s", (vendor_id,))
    get_vendor = cur.fetchone()

    if not get_vendor:
        return jsonify({"message": "Vendor not found"}), 200
        # return jsonify({"message": f"Product ratings with vendor id.{vendor_id} not found"}), 200

    # Execute the query
    cur.execute("""SELECT rating_id, ratings, review, vendor_feedback 
                    FROM vendor_ratings JOIN ON products 
                    WHERE product_id = %s AND vendor_id = %s""", (product_id, vendor_id))
    ratings = cur.fetchone()[0]
    id, ratings, review, vendor_feedback = ratings
    data = {
        "id": id,
        "product_id": product_id,
        "vendor_id": vendor_id,
        "ratings": ratings,
        "review": review,
        "vendor_feedback": vendor_feedback
    }
    print("ratings of a product", ratings, data)

    # Log the details into logger file
    logger(__name__).info(f"Ratings of product with id no. {product_id} are {ratings}")

    # close the database connection
    logger(__name__).warning("Hence checkout done, closing the connection")
    return jsonify({"message": f"Ratings of {product_id} are {ratings}",
                    "details": data}), 200


"""Functional API"""
@app.route("/app/v1/vendor_rating/<int:vendor_id>", methods=["GET"], endpoint='get_all_ratings_of_current_vendor_id')
@handle_exceptions
def get_all_ratings_of_current_vendor_id(vendor_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning(f"Starting the db connection to get ratings of vendor id. {vendor_id}")

    cur.execute("SELECT ratings, review from vendor_ratings WHERE vendor_id = %s", (vendor_id,))
    get_vendor = cur.fetchone()[0]

    if not get_vendor:
        return jsonify({"message": "Vendor not found"}), 200

    cur.execute("SELECT v.vendor_name, v.vendor_contact, v.address, r.ratings, r.review "
                "FROM vendor_ratings r JOIN vendor v ON r.vendor_id = r.vendor_id "
                "WHERE vendor_id = %s", (vendor_id, ))

    get_details = cur.fetchall()[0]

    name, contact, address, ratings, review = get_details

    data = {
        "name": name,
        "contact": contact,
        "address": address,
        "ratings": ratings,
        "review": review
    }

    # Log the details into logger file
    logger(__name__).info(f"Ratings of vendor with id. {vendor_id} has been showed")

    # close the database connection
    logger(__name__).warning("Hence ratings shown, closing the connection")
    return jsonify({"message": f"Ratings of vendor with id. {vendor_id} has been showed",
                    "details": data}), 200


"""Functional API"""
@app.route("/app/v1/vendor_rating/<int:vendor_id>/average", methods=["GET"], endpoint='get_average_ratings_of_current_vendor_id')
@handle_exceptions
def get_average_ratings_of_current_vendor_id(vendor_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning(f"Starting the db connection to get average ratings of vendor id. {vendor_id}")

    cur.execute("SELECT COUNT(*) from vendor_ratings WHERE vendor_id = %s", (vendor_id,))
    get_vendor_ratings_count = cur.fetchone()[0]

    if not get_vendor_ratings_count:
        return jsonify({"message": "Vendor not found"}), 200

    # query = """SELECT vendor_ratings.ratings, vendor.vendor_name, vendor.address,
    #                 vendor.vendor_contact FROM vendor_ratings JOIN vendor
    #                 on vendor.vendor_id = vendor_ratings.vendor_id"""

    query = """SELECT SUM(r.ratings) AS average_ratings, 
                v.vendor_name, v.vendor_contact 
                FROM vendor_ratings r JOIN vendor v 
                ON r.vendor_id = v.vendor_id 
                WHERE vendor_id =  %s"""

    cur.execute(query, (vendor_id, ))
    get_sum_ratings = cur.fetchall()[0]


    avg_ratings, name, contact = get_sum_ratings
    get_average = get_sum_ratings / get_vendor_ratings_count
    print("See", get_sum_ratings, get_vendor_ratings_count, get_average)


    data = {
        "average ratings": get_average,
        "vendor name": name,
        "contact info": contact
    }

    # Log the details into logger file
    logger(__name__).info(f"Ratings of vendor with id. {vendor_id} has been showed")

    # close the database connection
    logger(__name__).warning("Hence checkout done, closing the connection")
    return jsonify({"message": f"Average ratings of vendor with id. {vendor_id} are {get_average}",
                    "details": data}), 200


"""Admin API"""
# to update vendor details
@app.route("/app/v1/vendor/<int:vendor_id>", methods = ["PUT"], endpoint="update_vendor_details")
@handle_exceptions
def update_vendor_details(vendor_id):
    # starting the database connection
    cur, conn = connection()
    # log connection details
    logger(__name__).warning("Start the db connection to update values in vendor table")

    # Get values from the user
    data = request.get_json()
    vendor_name = data.get('name')
    contact = data.get('contact')
    address = data.get('address')

    if vendor_name:
        cur.execute("UPDATE vendor SET vendor_name = %s WHERE vendor_id = %s", (vendor_name, vendor_id))
    elif contact:
        cur.execute("UPDATE vendor SET vendor_contact = %s WHERE vendor_id = %s", (contact, vendor_id))
    elif address:
        cur.execute("UPDATE vendor SET address = %s WHERE vendor_id = %s", (address, vendor_id))

    # Commit the changes to the table
    conn.commit()
    logger(__name__).warning("Updating value successful, hence closing the connection")
    return jsonify({"message": "Vendor details updated", "details": data})


"""Admin API"""
# to delete vendor details
@app.route("/app/v1/<int:product_id>/vendor_rating/<int:vendor_id>", methods = ["DELETE"], endpoint="delete_vendor_details")
@handle_exceptions
def delete_vendor_details(product_id, vendor_id):
    # starting the database connection
    cur, conn = connection()

    # log connection details
    logger(__name__).warning("Start the db connection to delete values in vendor ratings table")

    query = "DELETE FROM vendor_ratings WHERE product_id =%s AND vendor_id = %s"
    cur.execute(query, (product_id, vendor_id))

    # Commit the changes to the table
    conn.commit()

    logger(__name__).warning(f"Deleting ratings with vendor id. {vendor_id} of product with id.{product_id}")
    return jsonify({f"Deleting ratings with vendor id. {vendor_id} of product with id.{product_id}"})



if __name__ == "__main__":
    app.run(debug=True, port=5000)
