-- @block
DROP TABLE IF EXISTS InvoiceItem;
DROP TABLE IF EXISTS Invoice;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Customer;

CREATE TABLE Product (
    importer VARCHAR(255),
    status VARCHAR(50),
    registration_date DATE,
    alteration_date DATE,
    discontinuation_date DATE,
    brand VARCHAR(255),
    product_code VARCHAR(10) PRIMARY KEY,
    reference VARCHAR(255),
    size VARCHAR(20),
    printing_technology VARCHAR(50),
    abrasion_resistance_group INTEGER,
    usage_recommendation VARCHAR(20),
    usage_description VARCHAR(255),
    category VARCHAR(50),
    edge_finishing VARCHAR(50),
    recommended_installation_joint VARCHAR(20),
    shade_variation VARCHAR(20),
    shade_variation_description VARCHAR(255),
    design_faces INTEGER,
    high_releave VARCHAR(20),
    tile_laying VARCHAR(20),
    watermark_resistance VARCHAR(20),
    new_thickness VARCHAR(20),
    room_scene VARCHAR(20),
    has_photo_faces VARCHAR(20),
    kitchen_icon VARCHAR(20),
    living_room_icon VARCHAR(20),
    dormitory_icon VARCHAR(20),
    bathroom_icon VARCHAR(20),
    laundry_room_icon VARCHAR(20),
    garage_icon VARCHAR(20),
    external_area_icon VARCHAR(20),
    common_area_icon VARCHAR(20),
    internal_area_icon VARCHAR(20)
);

CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    country VARCHAR(50)
);

CREATE TABLE Invoice (
    invoice_number VARCHAR(100) PRIMARY KEY,
    issue_date DATE,
    fob DECIMAL(10,2),
    destination_port VARCHAR(255),
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE InvoiceItem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_number VARCHAR(100),
    product_code VARCHAR(10),
    sqm DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2),
    currency VARCHAR(30),
    FOREIGN KEY (invoice_number) REFERENCES Invoice(invoice_number),
    FOREIGN KEY (product_code) REFERENCES Product(product_code),
    UNIQUE (invoice_number, product_code)
);

-- @block
SELECT * FROM product

-- @block
SELECT COUNT(*) FROM invoiceitem;



-- @block
DROP TABLE IF EXISTS InvoiceItem;
DROP TABLE IF EXISTS Invoice;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Customer;



