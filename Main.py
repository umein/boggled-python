from connection import Connection
from boggled import UserNotFoundException

class PlayerClient:
    # establish connection to the server
    def __init__(self):
        self.connection = Connection()
        self.player_service = self.connection.get_player_service()

    # login function
    def login(self, username, password):
        try:
            return self.player_service.login(username, password)
            print("Login successful.")
        except UserNotFoundException as e:
            print("User not found:", e)
        except Exception as e:
            print("An error occurred:", e)

    def menu(self):
            while True:
                print ("\n--- Boggled Game Menu ---")
                print ("1. Leaderboard")
                print ("2. Account")
                print ("3. Start Game")
                print ("4. Exit Game")
                choice = input ("Enter your choice: ")

                if choice == '1':
                    self.leaderboard()
                elif choice == '2':
                    self.player_account()
                elif choice == '3':
                    self.start_game()
                elif choice == '4':
                    self.exit_game()
                else:
                    print ("Invalid input. Please try again." )

    def leaderboard(self):
        print("---- Leaderboard ----")
        self.menu()
        #TODO

    def player_account(self):
        print("------ Account ------")
        self.menu()
        #TODO

    def start_game(self):
        print("Waiting for players...")
        self.menu()
        #TODO

    def exit_game(self):
        while True:
            confirm = input ("Are you sure you want to exit the game? (y/n): ")
            if confirm == 'y':
                print ("Exiting the game. Godbless. Ingat Ka. Mwa")
                return
            elif confirm == 'n':
                print ("Returning to menu...")
                self.menu()
            else:
                print ("Invalid input. Please enter 'y' for yes or 'n' for no.")

# login method invocation
if __name__ == "__main__":
    client = PlayerClient()
    loggedinuser = None
    while not loggedinuser:
        print("\nUsername: ")
        username = input()
        print("Password: ")
        password = input()
        loggedinuser = client.login(username, password)
        if not loggedinuser:
            print ("Invalid credentials. Please please please dont prove em right.")
    print(loggedinuser)
    if loggedinuser:
        client.menu()