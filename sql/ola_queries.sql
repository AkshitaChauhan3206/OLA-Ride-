/* Ola Ride Insights SQL file
   Table name is ola_bookings and it is built from data/ola_cleaned.csv
   Every query works in MySQL and in SQLite
   Questions 1 to 10 come from the project brief
   Questions 11 to 15 are extra business queries */


/* Q1 | Retrieve all successful bookings */
SELECT *
FROM ola_bookings
WHERE Booking_Status = 'Success';


/* Q2 | Average ride distance for each vehicle type, completed rides only */
SELECT Vehicle_Type,
       ROUND(AVG(Ride_Distance), 2) AS Avg_Ride_Distance_KM
FROM ola_bookings
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY Avg_Ride_Distance_KM DESC;


/* Q3 | Total number of rides cancelled by customers */
SELECT COUNT(*) AS Cancelled_By_Customers
FROM ola_bookings
WHERE Booking_Status = 'Canceled by Customer';


/* Q4 | Top 5 customers with the highest number of bookings */
SELECT Customer_ID,
       COUNT(*) AS Total_Bookings,
       SUM(Booking_Value) AS Total_Booked_Value
FROM ola_bookings
GROUP BY Customer_ID
ORDER BY Total_Bookings DESC, Total_Booked_Value DESC
LIMIT 5;


/* Q5 | Rides cancelled by drivers for personal and car related issues */
SELECT COUNT(*) AS Driver_Cancels_Personal_And_Car
FROM ola_bookings
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';


/* Q6 | Maximum and minimum driver ratings for Prime Sedan bookings */
SELECT MAX(Driver_Ratings) AS Max_Driver_Rating,
       MIN(Driver_Ratings) AS Min_Driver_Rating
FROM ola_bookings
WHERE Vehicle_Type = 'Prime Sedan'
  AND Driver_Ratings IS NOT NULL;


/* Q7 | All rides where payment was made using UPI */
SELECT *
FROM ola_bookings
WHERE Payment_Method = 'UPI';


/* Q8 | Average customer rating for each vehicle type */
SELECT Vehicle_Type,
       ROUND(AVG(Customer_Rating), 3) AS Avg_Customer_Rating
FROM ola_bookings
WHERE Customer_Rating IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY Avg_Customer_Rating DESC;


/* Q9 | Total booking value of rides completed successfully */
SELECT SUM(Booking_Value) AS Total_Successful_Booking_Value
FROM ola_bookings
WHERE Booking_Status = 'Success';


/* Q10 | All incomplete rides along with the reason */
SELECT Booking_ID,
       Customer_ID,
       Vehicle_Type,
       Booking_Value,
       Incomplete_Rides_Reason
FROM ola_bookings
WHERE Incomplete_Rides = 'Yes'
ORDER BY Incomplete_Rides_Reason, Booking_ID;


/* Q11 | Success rate and driver cancel rate for each vehicle type */
SELECT Vehicle_Type,
       COUNT(*) AS Bookings,
       ROUND(100.0 * SUM(CASE WHEN Booking_Status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Success_Rate_Pct,
       ROUND(100.0 * SUM(CASE WHEN Booking_Status = 'Canceled by Driver' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Driver_Cancel_Rate_Pct
FROM ola_bookings
GROUP BY Vehicle_Type
ORDER BY Success_Rate_Pct DESC;


/* Q12 | Booking value lost for every failed status */
SELECT Booking_Status,
       COUNT(*) AS Bookings,
       SUM(Booking_Value) AS Booking_Value_At_Stake
FROM ola_bookings
WHERE Booking_Status <> 'Success'
GROUP BY Booking_Status
ORDER BY Booking_Value_At_Stake DESC;


/* Q13 | Bookings and success rate for each hour of the day */
SELECT SUBSTR(Time, 1, 2) AS Hour_Of_Day,
       COUNT(*) AS Bookings,
       ROUND(100.0 * SUM(CASE WHEN Booking_Status = 'Success' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Success_Rate_Pct
FROM ola_bookings
GROUP BY SUBSTR(Time, 1, 2)
ORDER BY Hour_Of_Day;


/* Q14 | Revenue and share by payment method, completed rides only */
SELECT Payment_Method,
       COUNT(*) AS Rides,
       SUM(Booking_Value) AS Revenue,
       ROUND(100.0 * SUM(Booking_Value) / (SELECT SUM(Booking_Value) FROM ola_bookings WHERE Booking_Status = 'Success'), 2) AS Revenue_Share_Pct
FROM ola_bookings
WHERE Booking_Status = 'Success'
GROUP BY Payment_Method
ORDER BY Revenue DESC;


/* Q15 | Bookings where pickup and drop are the same place, a data quality check */
SELECT Booking_Status,
       COUNT(*) AS Bookings,
       ROUND(AVG(CASE WHEN Ride_Distance > 0 THEN Ride_Distance END), 2) AS Avg_Distance_KM
FROM ola_bookings
WHERE Pickup_Location = Drop_Location
GROUP BY Booking_Status
ORDER BY Bookings DESC;
