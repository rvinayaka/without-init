CREATE TABLE vendor(
    vendor_id SERIAL PRIMARY KEY,
    name VARCHAR(400) NOT NULL,
    vendor_contact NUMERIC NOT NULL,
    address VARCHAR(600) NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW(),
);


CREATE TABLE vendor_ratings (
    rating_id INT SERIAL PRIMARY KEY, 
    vendor_id INT REFERENCES vendor(vendor_id), 
    product_id REFERENCES product(product_id),
    user_id INT REFERENCES users(user_id), 
    ratings numeric DEFAULT 1, 
    review varchar(600),
    time TIMESTAMP NOT NULL DEFAULT NOW(),
    vendor_feedback varchar(600),
);


CREATE TABLE wishlist (
    wishlist_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id), 
    product_id INT REFERENCES products(product_id),
    time TIMESTAMP NOT NULL DEFAULT NOW(), 
);


CREATE TABLE recently_reviewed (
    recently_reviewed_id INT PRIMARY KEY, 
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    reviews_count NUMERIC DEFAULT 1,
    time_stamp TIMESTAMP NOT NULL DEFAULT NOW(),
);


CREATE TABLE ecart (
    cart_id INT PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    price NUMERIC,      -- fetch price from products table manually and input in it
    quantity NUMERIC,
    subtotal NUMERIC,		-- calculate (price * quantity) manually and input in it
    time_stamp TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE order_table (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id), 
    order_total NUMERIC NOT NULL,
    shipping_address TEXT REFERENCES users(shipping_address), -- first make unique constraint in users table
    time_stamp TIMESTAMP NOT NULL DEFAULT NOW()
);
