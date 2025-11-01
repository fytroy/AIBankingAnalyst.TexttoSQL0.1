/* SCRIPT 1 of 2: CREATE ALL TABLES
    Run this script in SSMS on your new 'BankingDB'
    (This is the v3 corrected version)
*/
USE BankingDB;
GO

-- Drop tables if they exist to start fresh
PRINT 'Dropping existing tables (if any)...';
DROP TABLE IF EXISTS Fact_Transactions;
DROP TABLE IF EXISTS Dim_TransactionTypes;
DROP TABLE IF EXISTS Dim_Accounts;
DROP TABLE IF EXISTS Dim_Customers;
DROP TABLE IF EXISTS Dim_Date;
GO

-- 1. Create the Date Dimension
PRINT 'Creating Dim_Date...';
CREATE TABLE Dim_Date (
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    Day INT NOT NULL,
    Month INT NOT NULL,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    DayOfWeek INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayName VARCHAR(20) NOT NULL
);
GO

-- 2. Create the Customer Dimension
PRINT 'Creating Dim_Customers...';
CREATE TABLE Dim_Customers (
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID VARCHAR(20) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100),
    City VARCHAR(100), -- Increased size
    Country VARCHAR(100) NOT NULL, -- <-- THIS IS THE FIX (was 50)
    RegistrationDate DATE
);
GO

-- 3. Create the Account Dimension
PRINT 'Creating Dim_Accounts...';
CREATE TABLE Dim_Accounts (
    AccountKey INT IDENTITY(1,1) PRIMARY KEY,
    AccountID VARCHAR(20) NOT NULL,
    CustomerKey INT NOT NULL,
    AccountType VARCHAR(20) NOT NULL,
    OpenDate DATE NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FOREIGN KEY (CustomerKey) REFERENCES Dim_Customers(CustomerKey)
);
GO

-- 4. Create the Transaction Type Dimension
PRINT 'Creating Dim_TransactionTypes...';
CREATE TABLE Dim_TransactionTypes (
    TransactionTypeKey INT IDENTITY(1,1) PRIMARY KEY,
    TransactionTypeName VARCHAR(50) NOT NULL,
    IsDebit BIT NOT NULL
);
GO

-- 5. Create the main Fact Table
PRINT 'Creating Fact_Transactions...';
CREATE TABLE Fact_Transactions (
    TransactionKey INT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    AccountKey INT NOT NULL,
    TransactionTypeKey INT NOT NULL,
    Amount DECIMAL(18, 2) NOT NULL,
    Location VARCHAR(100), -- Increased size
    FOREIGN KEY (DateKey) REFERENCES Dim_Date(DateKey),
    FOREIGN KEY (AccountKey) REFERENCES Dim_Accounts(AccountKey),
    FOREIGN KEY (TransactionTypeKey) REFERENCES Dim_TransactionTypes(TransactionTypeKey)
);
GO

/* SCRIPT 2 of 2: POPULATE THE DATE TABLE */
PRINT 'Populating Dim_Date from 2023 to 2025...';
SET NOCOUNT ON;

DECLARE @StartDate DATE = '2023-01-01';
DECLARE @EndDate DATE = '2025-12-31';

WHILE @StartDate <= @EndDate
BEGIN
    INSERT INTO dbo.Dim_Date (
        DateKey, FullDate, Day, Month, Year, Quarter, DayOfWeek, MonthName, DayName
    ) VALUES (
        CONVERT(INT, FORMAT(@StartDate, 'yyyyMMdd')),
        @StartDate, DATEPART(DAY, @StartDate), DATEPART(MONTH, @StartDate),
        DATEPART(YEAR, @StartDate), DATEPART(QUARTER, @StartDate),
        DATEPART(WEEKDAY, @StartDate), FORMAT(@StartDate, 'MMMM'), FORMAT(@StartDate, 'dddd')
    );
    SET @StartDate = DATEADD(DAY, 1, @StartDate);
END;

PRINT '✅✅✅ Database schema created and Dim_Date populated successfully!';
GO