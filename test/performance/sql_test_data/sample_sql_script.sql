-- Sample SQL Script for Schema Conversion Testing
-- This script contains various SQL patterns commonly found in production environments

-- Simple SELECT statements
SELECT * FROM LIVE_USR.TABLE1;
SELECT * FROM LIVE_USR.TABLE2 WHERE id = 1;
SELECT * FROM LIVE_USR.TABLE3 ORDER BY created_date DESC;

-- JOIN operations
SELECT
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_date
FROM LIVE_USR.CUSTOMERS c
INNER JOIN LIVE_USR.ORDERS o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01';

-- Subquery with multiple schema references
SELECT
    p.product_id,
    p.product_name,
    (SELECT COUNT(*) FROM LIVE_USR.ORDERS o WHERE o.product_id = p.product_id) as order_count
FROM LIVE_USR.PRODUCTS p
WHERE p.category_id IN (SELECT category_id FROM LIVE_USR.CATEGORIES WHERE active = 1);

-- INSERT with SELECT
INSERT INTO PROD_USR.SALES (sale_id, product_id, quantity, sale_date)
SELECT sale_id, product_id, quantity, sale_date
FROM PROD_USR.INVENTORY
WHERE processed_flag = 0;

-- UPDATE with JOIN
UPDATE PROD_APP.USER_DATA ud
SET ud.last_login = CURRENT_TIMESTAMP
FROM PROD_APP.USER_PROFILE up
WHERE ud.user_id = up.user_id
AND up.status = 'ACTIVE';

-- Complex JOIN with multiple tables
SELECT
    e.employee_id,
    e.employee_name,
    d.department_name,
    s.supplier_name,
    p.product_name
FROM LIVE_USR.EMPLOYEES e
INNER JOIN LIVE_USR.DEPARTMENTS d ON e.department_id = d.department_id
LEFT JOIN LIVE_USR.SUPPLIERS s ON e.supplier_id = s.supplier_id
LEFT JOIN LIVE_USR.PRODUCTS p ON s.supplier_id = p.supplier_id
WHERE e.active_flag = 'Y';

-- Data Warehouse queries
SELECT
    fs.sale_date,
    dc.customer_name,
    dp.product_name,
    SUM(fs.amount) as total_amount
FROM PROD_DWH.FACT_SALES fs
INNER JOIN PROD_DWH.DIM_CUSTOMER dc ON fs.customer_key = dc.customer_key
INNER JOIN PROD_DWH.DIM_PRODUCT dp ON fs.product_key = dp.product_key
INNER JOIN PROD_DWH.DIM_TIME dt ON fs.time_key = dt.time_key
GROUP BY fs.sale_date, dc.customer_name, dp.product_name
HAVING SUM(fs.amount) > 1000;

-- Financial queries
SELECT
    gl.account_number,
    gl.account_name,
    SUM(je.debit_amount) as total_debit,
    SUM(je.credit_amount) as total_credit
FROM PROD_FINANCE.GL_ACCOUNTS gl
LEFT JOIN PROD_FINANCE.JOURNAL_ENTRIES je ON gl.account_id = je.account_id
WHERE je.posting_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY gl.account_number, gl.account_name;

-- HR queries
SELECT
    em.employee_id,
    em.employee_name,
    pd.salary,
    att.attendance_rate,
    pr.performance_score
FROM PROD_HR.EMPLOYEE_MASTER em
LEFT JOIN PROD_HR.PAYROLL_DATA pd ON em.employee_id = pd.employee_id
LEFT JOIN PROD_HR.ATTENDANCE att ON em.employee_id = att.employee_id
LEFT JOIN PROD_HR.PERFORMANCE_REVIEWS pr ON em.employee_id = pr.employee_id
WHERE em.status = 'ACTIVE';

-- Table name conversion examples
SELECT * FROM DEV_USR.TABLE1 WHERE id > 100;
SELECT * FROM DEV_USR.TABLE2 t2
INNER JOIN DEV_USR.TABLE3 t3 ON t2.id = t3.ref_id;

UPDATE DEV_USR.TABLE1 SET status = 'PROCESSED' WHERE batch_id = 12345;

INSERT INTO DEV_USR.OLD_CUSTOMERS (customer_id, name)
SELECT customer_id, name FROM DEV_USR.LEGACY_PRODUCTS WHERE active = 1;

-- Stored procedure calls
EXEC SP_GET_CUSTOMER_DATA @customer_id = 12345;
EXEC SP_UPDATE_ORDER_STATUS @order_id = 67890, @status = 'SHIPPED';
CALL SP_PROCESS_PAYMENT(12345, 999.99, 'USD');
EXECUTE SP_GENERATE_REPORT @report_type = 'MONTHLY', @start_date = '2024-01-01';

-- Function calls
SELECT FN_CALCULATE_TAX(price, tax_rate) as total_price FROM PROD_USR.SALES;
SELECT customer_name, FN_GET_DISCOUNT(customer_type) as discount_rate FROM LIVE_USR.CUSTOMERS;
SELECT order_id, FN_FORMAT_DATE(order_date) as formatted_date FROM LIVE_USR.ORDERS;
SELECT email, FN_VALIDATE_EMAIL(email) as is_valid FROM PROD_APP.USER_DATA;

-- View references
SELECT * FROM VW_CUSTOMER_ORDERS WHERE order_total > 1000;
SELECT * FROM VW_PRODUCT_INVENTORY WHERE stock_level < 10;
SELECT * FROM VW_EMPLOYEE_DETAILS WHERE department = 'SALES';
SELECT * FROM VW_SALES_SUMMARY WHERE month = '2024-01';

-- CREATE TABLE with schema references
CREATE TABLE TEST_APP.TBL_USER_V1 (
    user_id INT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    created_date TIMESTAMP
);

-- CREATE INDEX
CREATE INDEX IDX_CUSTOMER_ID ON LIVE_USR.CUSTOMERS(customer_id);
CREATE INDEX IDX_ORDER_DATE ON LIVE_USR.ORDERS(order_date);
CREATE INDEX IDX_PRODUCT_CODE ON LIVE_USR.PRODUCTS(product_code);

-- ALTER TABLE
ALTER TABLE DEV_USR.OLD_CUSTOMERS ADD COLUMN old_column_name VARCHAR(100);
ALTER TABLE TEST_APP.TBL_USER_V1 MODIFY legacy_field VARCHAR(200);

-- Database link references
SELECT * FROM PROD_USR.SALES@DBLINK_PROD;
INSERT INTO DEV_USR.INVENTORY SELECT * FROM PROD_USR.INVENTORY@DBLINK_STAGE;

-- Synonym usage
SELECT * FROM SYN_CUSTOMERS WHERE customer_type = 'PREMIUM';
UPDATE SYN_PRODUCTS SET price = price * 1.1 WHERE category = 'ELECTRONICS';

-- Complex CTE with multiple schemas
WITH CustomerSales AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(o.amount) as total_sales
    FROM LIVE_USR.CUSTOMERS c
    INNER JOIN LIVE_USR.ORDERS o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
),
ProductStats AS (
    SELECT
        p.product_id,
        p.product_name,
        COUNT(o.order_id) as order_count
    FROM LIVE_USR.PRODUCTS p
    LEFT JOIN LIVE_USR.ORDERS o ON p.product_id = o.product_id
    GROUP BY p.product_id, p.product_name
)
SELECT
    cs.customer_name,
    ps.product_name,
    cs.total_sales
FROM CustomerSales cs
CROSS JOIN ProductStats ps
WHERE cs.total_sales > 5000;

-- MERGE statement
MERGE INTO STG_USR.WORK_TABLE_01 target
USING LIVE_USR.TABLE1 source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET target.value = source.value
WHEN NOT MATCHED THEN
    INSERT (id, value) VALUES (source.id, source.value);

-- Window functions
SELECT
    employee_id,
    employee_name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank
FROM PROD_HR.EMPLOYEE_MASTER
WHERE status = 'ACTIVE';

-- Temporary table operations
SELECT * INTO #TempTable FROM DEV_USR.TABLE1 WHERE status = 'PENDING';
INSERT INTO DEV_USR.TABLE2 SELECT * FROM #TempTable;

-- Transaction with multiple schemas
BEGIN TRANSACTION;
    UPDATE PROD_USR.SALES SET processed = 1 WHERE sale_date = '2024-01-01';
    INSERT INTO PROD_USR.INVENTORY SELECT * FROM PROD_APP.USER_DATA WHERE sync_flag = 0;
    DELETE FROM PROD_FINANCE.JOURNAL_ENTRIES WHERE temp_value = 1;
COMMIT;

-- Backup and archive operations
INSERT INTO STG_USR.BACKUP_2023 SELECT * FROM LIVE_USR.TABLE1 WHERE year = 2023;
CREATE TABLE STG_USR.WORK_TABLE_01 AS SELECT * FROM LIVE_USR.TABLE2;
