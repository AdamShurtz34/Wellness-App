import mysql.connector
from datetime import datetime


def get_quote(self):
    try:
        # Connect to MySQL database and fetch a random quote
        sql_statement = "SELECT * FROM Quotes ORDER BY RAND() LIMIT 1"
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchall()
        if result:
            return '"' + str(result[0][1]) + '"' + '\n\n- ' + str(result[0][2])
        else:
            return "No quotes available"  # Default message if no quotes found
    except mysql.connector.Error as err:
        return "Error fetching quote: {}".format(err)
    #-----------------------------------------
    # OLD LOGIC - "QUOTE OF THE DAY"
    # -----------------------------------------
    '''
    current_date = datetime.now()
    day_of_year = current_date.timetuple().tm_yday
    try:
        # get max id from quotes list, if day_of_year is greater than max, quote_id is a subtraction
        sql_statement = "SELECT MAX(quote_uid) FROM Quotes"
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchone()
        max_id = result[0]
        if day_of_year > max_id:
            quote_id = day_of_year - max_id
        else:
            quote_id = day_of_year
        # now pull today's quote using quote_id
        sql_statement = "SELECT * FROM Quotes WHERE quote_uid = {}".format(quote_id)
        self.mycursor.execute(sql_statement)
        result = self.mycursor.fetchone()
        return '"' + str(result[1]) + '"' + '\n\n- ' + str(result[2])
    except mysql.connector.Error as err:
        return "Error fetching quote: {}".format(err)  # Error message if fetch fails
    '''
