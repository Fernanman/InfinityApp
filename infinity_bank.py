import sqlite3 as sql
import matplotlib.pyplot as plt
import random
import secrets
import time
import threading
from multiprocessing import Process
import os

class FILOArray:
    def __init__(self, max_len=50):
        """
        Intializes the FILOArray class.

        Keyword arguments:
        max_len -- the maximum number of items that can be in the array 
        """
        self.max_len = max_len
        self.array = []

    def __getitem__(self, key):
        """
        Indexes the array at the key.
        """
        return self.array[key]
    
    def __repr__(self) -> str:
        """
        Returns the stringified array.
        """
        return str(self.array)

    def insert(self, data):
        """
        Inserts the data into the array. Pops the first element if it is full.

        Keyword arguments:
        data -- the data to be inserted
        """

        if self.full():
            self.array.pop(0)

        self.array.append(data)

    def remove(self, data):
        """
        Removes the data from the array.

        Keyword arguments:
        data -- the data to be removed
        """

        self.remove(data)

    def full(self):
        """
        Returns whether or not the array is full.
        """
        return len(self.array) == self.max_len


class InfinityBank:
    def __init__(self, db_name="accounts.db", update_rate=0.1):
        """
        Intializes the bank class.

        Keyword arguments:
        db_name -- the name of the database file 
        update_rate -- the rate in seconds at which the conversion rate updates
        """
        # Maybe the bank should have its own account?
        self.token_manager = {}
        self.logged_accounts = []
        # The conversion rate is USD / Infinity = Conversion rate -> Infinity * Conversion rate = USD
        self.conversion_rate = 1.0 

        self.db = self.connect_db(db_name)
        self.cursor = self.db.cursor()

        self.create_tables()

        self.x = FILOArray()
        self.y = FILOArray()

        self.conversion_thread = threading.Thread( target=self.update_conversion, args=(update_rate, ) )
        self.conversion_thread.start()
        # self.conversion_process = Process(target=self.update_conversion, args=(update_rate, ))
        # self.conversion_process.start()
    
    def connect_db(self, db_name):
        """
        Connects to the database that the bank will use to store all of the account and the corresponding information in.
        Creates a db folder if one does not already exist. Returns a database connection.
        """
        if not os.path.isdir("./db"):
            os.mkdir("./db")

        path = os.fspath( os.path.abspath(f"./db/{db_name}") )

        # Maybe note , check_same_thread=False
        return sql.connect(path, check_same_thread=False)
    
    def create_tables(self):
        """
        Checks the current database for all of the tables that will be used. If the table does not exist, then the table will be made.
        """

        # https://www.sqlite.org/schematab.html
        tables = self.cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type='table'").fetchall()

        if len(tables) == 0:
            # https://www.sqlite.org/datatype3.html
            
            print("Creating table.")
            self.cursor.execute("""
                                CREATE TABLE accounts ( 
                                Public_Signature VARCHAR(64) PRIMARY KEY,
                                Private_Signature VARCHAR(64) NOT NULL,
                                Infinity_Balance REAL NOT NULL,
                                USD_Balance DECIMAL(15, 2) NOT NULL 
                                )
                                """)

    def create_account(self, pub_sig: str, priv_sig: str) -> bool:
        """
        Creates a new account. An account takes 500 USD to open, so each account starts with 500 USD and 0 Infinity currency.
        If there is an account alread with that name, then the account is not created and an error is returned.

        Keyword arguments:
        pub_sig -- the public signature / username of the account
        priv_sig -- the private signature / password of the account
        """

        try:
            self.cursor.execute(f"INSERT INTO accounts VALUES ('{pub_sig}', '{priv_sig}', 0, 500)")
            self.db.commit()
            
            return True
        except sql.IntegrityError as e:
            return False
    
    def delete_account(self, pub_sig: str, priv_sig: str) -> bool:
        """
        Deletes an account in the database. If the account exists, then the account is deleted and True is returned.
        Otherwise, False is returned.

        Keyword arguments:
        pub_sig -- the public signature / username of the account
        priv_sig -- the private signature / password of the account
        """
        
        try:
            self.cursor.execute(f"DELETE FROM accounts WHERE Public_Signature='{pub_sig}' AND Private_Signature='{priv_sig}'")
            self.db.commit()
            
            return True
        except sql.IntegrityError as e:
            return False

    def login(self, pub_sig: str, priv_sig: str) -> str:
        """
        Logs into an accout by giving an existing public and private signature in the database. The token is used to 
        ensure that only one device is logged into the account. If the account exists and is not currently logged in, then
        the user is given a token so that they can interact with their account. Otherwise, None is returned.

        Keyword arguments:
        pub_sig -- the public signature / username of the account
        priv_sig -- the private signature / password of the account
        """

        account = self.cursor.execute(f"SELECT Public_Signature FROM accounts WHERE Public_Signature='{pub_sig}' AND Private_Signature='{priv_sig}'").fetchone()

        if account is not None and account[0] not in self.logged_accounts: 
            account = account[0]
            token = secrets.token_hex(32)
            self.token_manager[token] = account
            self.logged_accounts.append(account)
            
            return token
        else:
            return None

    def logout(self, token: str) -> bool:
        """
        Logs out of an account if it is logged in already. If the account is logged in, then True is returned.
        Otherwise, False is returned.

        Keyword arguments:
        token -- the token assigned to the account that is being logged out
        """

        if token in self.token_manager:
            self.logged_accounts.remove(self.token_manager[token])
            del self.token_manager[token]

            return True
        
        else:
            return False

    # Low key buy and sell can be the same function but they are
    def buy(self, acc_tok: str, amount: float) -> bool:
        """
        Converts the given amount from base currency (USD) to Infinity at the current conversion rate.
        If the user has the given amount in their account, then the action is taken and True is returned. 
        Otherwise, no action is taken and False is returned.

        Keyword arguments:
        acc_tok -- the token to the logged in account that is buying Infinity
        amount -- the amount of base currency (USD) being used to buy Infinity
        """

        if acc_tok in self.token_manager:
            account = self.token_manager[acc_tok]
            balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{account}'").fetchone()
            
            if balance[0] >= amount:
                self.cursor.execute(f"UPDATE accounts SET USD_Balance = USD_Balance - {amount} WHERE Public_Signature='{account}'")
                self.cursor.execute(f"UPDATE accounts SET Infinity_Balance = Infinity_Balance + {amount} / {self.conversion_rate} WHERE Public_Signature='{account}'")

                balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{account}'").fetchone()
                self.db.commit()
            
                return True
        
        return False
        
    def sell(self, acc_tok: str, amount: float) -> bool:
        """
        Converts the given amount from Infinity to base currency at the current conversion rate.
        If the user has the given amount in their account, then the action is taken and True is returned. 
        Otherwise, no action is taken and False is returned.

        Keyword arguments:
        acc_tok -- the token to the logged account that is selling Infinity
        amount -- the amount of Infinity to sell
        """

        if acc_tok in self.token_manager:
            account = self.token_manager[acc_tok]
            balance = self.cursor.execute(f"SELECT Infinity_Balance, USD_Balance FROM accounts WHERE Public_Signature='{account}'").fetchone()
            
            if balance[0] >= amount:
                self.cursor.execute(f"UPDATE accounts SET Infinity_Balance  = Infinity_Balance - {amount} WHERE Public_Signature='{account}'")
                self.cursor.execute(f"UPDATE accounts SET USD_Balance = USD_Balance + {amount} * {self.conversion_rate} WHERE Public_Signature='{account}'")

                balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{account}'").fetchone()
                self.db.commit()
            
                return True
        
        return False

    # Going to want to change this so that to account is just their public signature. Also can only transfer infinity.
    def transfer(self, from_acc_tok: str, to_acc_pub: str, trans_type: bool, 
                 amount: float) -> bool:
        """
        Transfers a currency from one account to another. If the sending party has sufficient funds for the transfer
        and both accounts are logged in, then the currecny is transferred and True is returned. Otherwise, no action
        is taken and False is returned.

        Keyword arguments:
        from_acc -- the token of the sending account
        to_acc_pub -- the public signature of the receiving account
        trans_type -- the type of currency being exchanged; True = Infinity, False = base
        amount -- the amount of the currency being transferred
        """
        
        # print(self.get_accounts())
        if from_acc_tok in self.token_manager and (to_acc_pub, ) in self.get_accounts():
            print("________________ IN _____________________")
            from_account = self.token_manager[from_acc_tok]

            if trans_type:
                from_balance = self.cursor.execute(f"SELECT Infinity_Balance, USD_Balance FROM accounts WHERE Public_Signature='{from_account}'").fetchone()
                currency = "Infinity_Balance"
            else:
                from_balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{from_account}'").fetchone()
                currency = "USD_Balance"

            if from_balance[0] >= amount:
                self.cursor.execute(f"UPDATE accounts SET {currency} = {currency} - {amount} WHERE Public_Signature='{from_account}'")
                self.cursor.execute(f"UPDATE accounts SET {currency} = {currency} + {amount} WHERE Public_Signature='{to_acc_pub}'")

                from_balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{from_account}'").fetchone()
                to_balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{to_acc_pub}'").fetchone()
                
                self.db.commit()
                return True

        return False

    def reward(self, acc_tok: str, amount: float) -> bool:
        """
        Rewards the account by giving them Infinity. Returns True if the account is logged in.
        Returns False otherwise.

        acc_tok -- the token of the logged in account
        amount -- the amount that is being rewarded
        """
        if acc_tok in self.token_manager:
            account = self.token_manager[acc_tok]
            self.cursor.execute(f"UPDATE accounts SET Infinity_Balance = Infinity_Balance + {amount} WHERE Public_Signature='{account}'")
            
            return True
        
        return False
        
    def update_conversion(self, wait):
        """
        Randomly updates the conversion rate to a cap. Simulates changes in market value.

        Keyword arguments:
        wait -- the time to wait between updates
        """
        i = 0
        while True:
            self.conversion_helper()

            self.y.insert(round(self.get_conv_rate(), 4))
            self.x.insert(round(i, 2))

            plt.title("Market Value")
            plt.ylabel("Conversion Rate")
            plt.xlabel("Seconds")
            plt.plot(self.x.array, self.y.array)
            plt.savefig('./market.png')
            plt.clf()

            time.sleep(wait)
            i += wait 

    def conversion_helper(self):
        """
        Returns a random number according to the current conversion rate.
        """

        if self.conversion_rate > 10: increase = random.random() < 0.1
        elif self.conversion_rate > 6: increase = random.random() < 0.2
        elif self.conversion_rate > 3: increase = random.random() < 0.4
        elif self.conversion_rate < 0.1: increase = random.random() < 0.9
        elif self.conversion_rate < ( 1 / 6): increase = random.random() < 0.8
        elif self.conversion_rate < ( 1 / 3 ): increase = random.random() < 0.6
        else: increase = random.random() < 0.5
       
        if increase: 
            target = self.conversion_rate + ( random.random() * (1 / 5 - 1 / 25) + 1 / 25 )   
        else: 
            if self.conversion_rate < (1 / 3.5): 
                target = self.conversion_rate - ( random.random() * (1 / 40 - 1 / 400) + 1 / 400 )
            else: target = self.conversion_rate - ( random.random() * (1 / 5 - 1 / 25) + 1 / 25 )
            
            if target < 0:
                target = self.conversion_rate - self.conversion_rate * 0.25

        self.conversion_rate += ( target - self.conversion_rate ) * random.random() 

    def get_account_balance(self, acc_tok: str) -> tuple:
        """ 
        Returns the balance of the account if it is currently logged into. Otherwise, returns None.

        Keyword arguments:
        acc_tok -- the token to the account that balance is being checked.
        """
        
        if acc_tok in self.token_manager:
            account = self.token_manager[acc_tok]
            balance = self.cursor.execute(f"SELECT USD_Balance, Infinity_Balance FROM accounts WHERE Public_Signature='{account}'").fetchone()

            return balance
        
        return None

    def get_conv_rate(self) -> float:
        """
        Returns the current conversion rate.
        """

        return self.conversion_rate

    def get_accounts(self) -> list:
        """
        Returns all of the accounts in the 
        """

        return self.cursor.execute("SELECT Public_Signature FROM accounts").fetchall()

    def get_logged_accounts(self) -> list:
        """
        Returns all of the accounts that are currently logged into.
        """

        return self.logged_accounts
 
    def get_acc_name(self, acc_tok: str) -> str:
        """
        Returns the public signature associated with the provided token.

        Keyword arguments:
        acc_token -- the account token that needs its public signature
        """
        return self.token_manager[acc_tok]