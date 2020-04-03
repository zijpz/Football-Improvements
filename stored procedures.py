#import the tool used to work with mysql in python
import mysql.connector

#connect to a mysql database with the required details
db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "bowenkedinskie",
    database = "forward football"
)

#a cursor gives us the ability to have multiple seperate working environments through the same connection to the database
mycursor = db.cursor()

#how to create a table
#mycursor.execute("CREATE TABLE person (name VARCHAR(50), age smallint UNSIGNED, personID int PRIMARY KEY AUTO_INCREMENT)")

#how to execute a command to look into the details of a table
#mycursor.execute("describe clean_event")

#input
s = input("username:")
 
if s == "player":
    mycursor.execute("select * from clean_player limit 10")
    for x in mycursor:
        print(x)

elif s == "trainer":
    mycursor.execute("select * from clean_training limit 10")
    for x in mycursor:
        print(x)

else:
    print("invalid username")

#making a stored procedure(i do this in mysql)
# CREATE PROCEDURE add_num(IN num1 INT, IN num2 INT, OUT sum INT)
# BEGIN 
# SET sum := num1 + num2; 
# END;")


#executing a stored procedure
#args = (5, 6, 0) # 0 is to hold value of the OUT parameter sum
#mycursor.callproc('add_num', args)

#closing the connection to the database
if db.is_connected(): 
    mycursor.close()
    db.close()
    print("connection closed")
