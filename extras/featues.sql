CREATE TABLE Products (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  sku VARCHAR(255) UNIQUE,
  description TEXT NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  discount_price DECIMAL(10, 2) NULL,
  capacity INTEGER NOT NULL,
  units INTEGER NOT NULL,
  available_qty INTEGER NOT NULL,
  featured BOOLEAN NOT NULL,
  is_active BOOLEAN NOT NULL,
  vendor_id INTEGER REFERENCES vendor(vendor_id),
  in_order INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP NULL,
  image_urls TEXT[] NULL,
  tags TEXT[] NULL
);

CREATE TABLE Filter (
  filter_id SERIAL PRIMARY KEY,
  filter_name VARCHAR NOT NULL,
  category_id INT REFERENCES Category(category_id),
  filter_type VARCHAR NOT NULL,
  filter_options TEXT NOT NULL
);

CREATE TABLE Category (
  category_id SERIAL PRIMARY KEY,
  category_name VARCHAR NOT NULL,
  description TEXT,
  parent_category_id INT REFERENCES Category(category_id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP
);

CREATE TABLE subcategory (
  subcategory_id SERIAL PRIMARY KEY,
  subcategory_name VARCHAR NOT NULL,
  description TEXT NULL,
  parent_category_id INT NOT NULL REFERENCES category(category_id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP NULL
);

CREATE TABLE User (
  user_id BIGINT PRIMARY KEY,
  user_name VARCHAR NOT NULL,
  email VARCHAR UNIQUE NOT NULL,
  phone VARCHAR,
  country_code VARCHAR,
  email_verified BOOLEAN NOT NULL,
  password VARCHAR NOT NULL,
  language VARCHAR NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP,
  shipping_address TEXT,
  billing_address TEXT,
  points_balance INT NOT NULL DEFAULT 0,
  points_redeemed INT NOT NULL DEFAULT 0
);

CREATE TABLE filter_product (
  filter_id INT REFERENCES filter(filter_id),
  product_id INT REFERENCES product(product_id),
  PRIMARY KEY (filter_id, product_id)
);

CREATE TABLE Points (
  id SERIAL PRIMARY KEY,
  customer_id INT NOT NULL,
  transaction_id INT NOT NULL,
  points_earned INT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT fk_points_customer
    FOREIGN KEY (customer_id)
    REFERENCES User(user_id),
  CONSTRAINT fk_points_transaction
    FOREIGN KEY (transaction_id)
    REFERENCES Transaction(id),
  CONSTRAINT ck_points_points_earned
    CHECK (points_earned >= 0)
);

