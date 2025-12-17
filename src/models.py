CREATE TABLE sales_transactions (
    id SERIAL PRIMARY KEY,

    -- Distributor hierarchy
    master_distributor TEXT,
    distributor TEXT,

    -- Business structure
    line_of_business TEXT,
    supplier TEXT,
    agency TEXT,

    -- Product hierarchy
    category TEXT,
    segment TEXT,
    brand TEXT,
    sub_brand TEXT,

    -- Geography
    country TEXT,
    city TEXT,
    area TEXT,

    -- Retail structure
    retailer_group TEXT,
    retailer_sub_group TEXT,
    channel TEXT,
    sub_channel TEXT,

    -- Sales team
    salesman TEXT,

    -- Order & customer details
    order_number TEXT,
    customer TEXT,
    customer_account_name TEXT,
    customer_account_number TEXT,

    -- Item details
    item TEXT,
    item_description TEXT,
    promo_item BOOLEAN,
    foc_nonfoc TEXT,

    -- Pricing & invoice
    unit_selling_price NUMERIC,
    invoice_number TEXT,
    invoice_date DATE,

    -- Time dimensions (kept explicitly for faster analytics)
    year INTEGER,
    month INTEGER,

    -- Metrics
    invoiced_quantity INTEGER,
    value NUMERIC
);


CREATE TABLE active_store (
    customer_account_name TEXT PRIMARY KEY,

    -- ===== 2024 =====
    apr_2024 INTEGER,
    aug_2024 INTEGER,
    dec_2024 INTEGER,
    feb_2024 INTEGER,
    jan_2024 INTEGER,
    jul_2024 INTEGER,
    jun_2024 INTEGER,
    mar_2024 INTEGER,
    may_2024 INTEGER,
    nov_2024 INTEGER,
    oct_2024 INTEGER,
    sep_2024 INTEGER,

    total_2024 INTEGER,

    -- ===== 2025 =====
    apr_2025 INTEGER,
    aug_2025 INTEGER,
    dec_2025 INTEGER,
    feb_2025 INTEGER,
    jan_2025 INTEGER,
    jul_2025 INTEGER,
    jun_2025 INTEGER,
    mar_2025 INTEGER,
    may_2025 INTEGER,
    nov_2025 INTEGER,
    oct_2025 INTEGER,
    sep_2025 INTEGER,

    total_2025 INTEGER,

    -- ===== Overall =====
    grand_total INTEGER
);
