import logging, mysql.connector

class Card:
    def __init__(self, iD):
        self.iD = iD
        try:
            self.cursor = database.cursor()
        except mysql.connector.Error:
            db_connection()
            self.cursor = database.cursor()

    def validation(self):
        data = self.sqlSelect("SELECT `Name`, `Loaned`, `Credit` FROM `Card` WHERE `ID` = %s;", (self.iD, ))
        if data:
            self.credit = data[0][2]
            self.start(data[0])
        else:
            print("No card with ID ", self.iD)

    def start(self, data):
        print("Card ID: ", self.iD)
        print("Name: ", data[0])
        print("Loaned: ", data[1])
        print("Credit: ", data[2])
        print("Please select an option")
        print("1) Buy")
        print("2) Charge card")
        print("3) Lend card")
        print("4) Return card")
        while True:
            option = input("Option: ")
            if option == "e":
                return False
            try:
                option = int(option)
                if option == 1:
                    self.buy()
                    break
                elif option == 2:
                    self.charge()
                    break
                elif option == 3:
                    self.lend()
                    break
                elif option == 4:
                    self.back()
                    break
                else:
                    print("Not a valid option!")
            except ValueError:
                print("Not a number!")

    def buy(self):
        while True:
            drink_id = input("Drink number: ")
            if drink_id == "e":
                return False
            result = self.sqlSelect("SELECT `Price` FROM `Drink` WHERE `ID` = %s;", (drink_id, ))
            if result:
                break
            else:
                print("Not a valid drink number")

        price = result[0][0]
        if self.credit - price < 0:
            print("Not enough money!")
        else:
            self.credit -= price
            self.sqlChange("UPDATE `Card` SET `Credit` = %s WHERE `ID` = %s;", (self.credit, self.iD))
            result = self.sqlSelect("SELECT `Stock` FROM `Drink` WHERE `ID` = %s;", (drink_id, ))
            if result:
                vorrat = result[0][0] -1
                if vorrat:
                    self.sqlChange("UPDATE `Drink` SET `Stock` = %s WHERE `ID` = %s;", (vorrat, drink_id))
            logging.info("Card with ID "+str(self.iD)+" bought drink with ID "+str(drink_id))
            print("Drink successfully sold!")

    def charge(self):
        while True:
            amount = input("Amount: ")
            if amount == "e":
                return False
            try:
                amount = float(amount)
                break
            except ValueError:
                print("Not a valid amount!")
        self.credit += amount
        self.sqlChange("UPDATE `Card` SET `Credit` = %s WHERE `ID` = %s;", (self.credit, self.iD))
        logging.info("Card with ID "+str(self.iD)+" gets "+str(amount)+" €. New Credit: "+str(self.credit)+" €")
        print("Card succesfully charged!")
        print("New Credit: ", self.credit)

    def lend(self):
        result = input("Name of person:  ")
        if result == "e":
            return False
        self.sqlChange("UPDATE `Card` SET `Loaned` = 1, `Name` = %s WHERE `ID` = %s;", (result, self.iD))
        logging.info("Card with ID "+str(self.iD)+" lend")
        print("Card successfully loaned!")

    def back(self):
        self.sqlChange("UPDATE `Card` SET `Loaned` = 0, `Name` = NULL WHERE `ID` = %s;", (self.iD, ))
        logging.info("Card with ID "+str(self.iD)+" handed back")
        print("Card successfully returned!")

    def sqlChange(self, sql, data):
        try:
            self.cursor.execute(sql, data)
            database.commit()
        except mysql.connector.Error as e:
            logging.error("Database request change incorrect")
            logging.error(e)
            print("Error database (Change): ", e)

    def sqlSelect(self, sql, data):
        try:
            self.cursor.execute(sql, data)
            database.commit()
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logging.error("Database request select incorrect")
            logging.error(e)
            print("Error database (Select): ", e)
            return False

def db_connection():
    logging.info("Preparing database")
    global database
    try:
        database = mysql.connector.connect(host="localhost", port="3306", database="rfid_payment", user="root", password="")
        logging.info("Connected to database")
    except mysql.connector.Error as e:
        logging.fatal("No connection to database")
        logging.error(e)
        print("No connection to database")


logging.basicConfig(filename="rfid.log", style="{", format="{asctime} [{levelname}] {message}",
                            datefmt="%d.%m.%Y %H:%M:%S", level="INFO")

db_connection()

while True:
    card_id = input("Scan card: ")
    card_obj = Card(card_id)
    card_obj.validation()
