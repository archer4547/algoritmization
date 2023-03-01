-- Keep a log of main SQL queries
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- QUERY 1 --
SELECT description
FROM crime_scene_reports
WHERE year = 2021
AND month = 7
AND day = 28
AND street = "Humphrey Street";

-- REASON --
    -- Get some information about theft
-- REASON --

-- INFORMATION --
    -- Theft of the CS50 duck took place at 10:15am at the Humphrey Street bakery.
    -- Interviews were conducted today with three witnesses who were present
    -- at the time – each of their interview transcripts mentions the bakery.
    -- Littering took place at 16:36. No known witnesses.
-- INFORMATION --

-- CONCLUSION --
    -- 1. Theft of the CS50 duck took place at 10:15am at the Humphrey Street bakery.
    -- 2. Interviews were conducted today with three witnesses, each of their interview transcripts mentions the bakery.
    -- 3. Littering took place at 16:36.
-- CONCLUSION --
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- QUERY 2 --
SELECT transcript
FROM interviews
WHERE year = 2021
AND month = 7
AND day = 28
AND transcript LIKE "%bakery%";

-- REASON --
    -- Analize witnesses interviews using conclusion 2 from query 1
-- REASON --

-- INFORMATION --
    -- Sometime within ten minutes of the theft, I saw the thief get into a car in the bakery parking lot and drive away.
    -- If you have security footage from the bakery parking lot, you might want to look for cars that left the parking lot in that time frame.

    -- I don't know the thief's name, but it was someone I recognized.
    -- Earlier this morning, before I arrived at Emma's bakery,
    -- I was walking by the ATM on Leggett Street and saw the thief there withdrawing some money.

    -- As the thief was leaving the bakery, they called someone who talked to them for less than a minute.
    -- In the call, I heard the thief say that they were planning to take the earliest flight out of Fiftyville tomorrow.
    -- The thief then asked the person on the other end of the phone to purchase the flight ticket.
-- INFORMATION --

-- CONCLUSION --
    -- 1. Within 10 minutes after theft, thief got into a car in the bakery parking lot and drive away
    -- 2. Thief there withdrawing some money using ATM on Leggett Street before theft
    -- 3. Thief asked the person on the other end of the phone to purchase the flight ticket to take the earliest flight out of Fiftyville tomorrow
-- CONCLUSION --
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- QUERY 3 --
SELECT people.name
FROM people
WHERE people.license_plate IN                                               -- Subquery to find license plate list of people who left the bakery at the time that witness mentioned
            (SELECT bakery_security_logs.license_plate
            FROM bakery_security_logs
            WHERE bakery_security_logs.year = 2021
            AND bakery_security_logs.month = 7
            AND bakery_security_logs.day = 28
            AND bakery_security_logs.hour = 10
            AND bakery_security_logs.minute >= 15
            AND bakery_security_logs.minute <= 25
            AND bakery_security_logs.activity = "exit")


      AND people.id IN                                                      -- Subquery to find people who made transactions where witness mentioned
            (SELECT bank_accounts.person_id
            FROM bank_accounts
            WHERE bank_accounts.account_number IN
                (SELECT atm_transactions.account_number
                FROM atm_transactions
                WHERE atm_transactions.year = 2021
                AND atm_transactions.month = 7
                AND atm_transactions.day = 28
                AND atm_transactions.atm_location = "Leggett Street"
                AND atm_transactions.transaction_type = "withdraw"))


      AND people.passport_number IN                                         -- Subquery to find passport numbers of people who flew at the earliest flight out of Fiftyville at the day after theft
            (SELECT passport_number
            FROM passengers
            WHERE flight_id IN
                (SELECT flights.id
                FROM flights
                WHERE flights.year = 2021
                AND flights.month = 7
                AND flights.day = 29
                AND flights.origin_airport_id IN
                    (SELECT airports.id
                    FROM airports WHERE
                    airports.city = "Fiftyville")
                ORDER BY flights.hour ASC, flights.minute ASC
                LIMIT 1))


      AND people.phone_number IN                                            -- Subquery to find phone numbers of people using information that witness mentioned
            (SELECT phone_calls.caller
            FROM phone_calls
            WHERE phone_calls.year = 2021
            AND phone_calls.month = 7
            AND phone_calls.day = 28
            AND phone_calls.duration < 60);

-- REASON --
    -- Find the thief
-- REASON --

-- INFORMATION --
    -- Bruce
-- INFORMATION --

-- CONCLUSION --
    -- Bruce is thief
-- CONCLUSION --
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- QUERY 4 --
SELECT people.name
FROM people
WHERE people.phone_number IN
        (SELECT phone_calls.receiver
        FROM phone_calls
        WHERE phone_calls.year = 2021
        AND phone_calls.month = 7
        AND phone_calls.day = 28
        AND phone_calls.duration < 60
        AND phone_calls.caller IN
            (SELECT people.phone_number
            FROM people
            WHERE people.name = "Bruce"));

-- REASON --
    -- Find thief's accomplice
-- REASON --

-- INFORMATION --
    -- Robin
-- INFORMATION --

-- CONCLUSION --
    -- Robin is Bruce's accomplice
-- CONCLUSION --
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- QUERY 5 --
SELECT airports.city
FROM airports
WHERE airports.id IN
        (SELECT flights.destination_airport_id
        FROM flights
        WHERE flights.year = 2021
        AND flights.month = 7
        AND flights.day = 29
        AND flights.origin_airport_id IN
            (SELECT airports.id
            FROM airports WHERE
            airports.city = "Fiftyville")
        ORDER BY flights.hour ASC, flights.minute ASC
        LIMIT 1);

-- REASON --
    -- Find destination airport city
-- REASON --

-- INFORMATION --
    -- New York City
-- INFORMATION --

-- CONCLUSION --
    -- Thief escaped to New York City
-- CONCLUSION --
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------