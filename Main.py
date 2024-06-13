from connection import Connection
from boggled import UserNotFoundException

class PlayerClient:
    # establish connection to the server
    def __init__(self):
        self.connection = Connection()
        self.player_service = self.connection.get_player_service()
        self.loggedinuser = None

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
                    if self.exit_game():
                        print("Exiting the Game")
                        break
                else:
                    print ("Invalid input. Please try again." )

    # login function
    def login(self):
        try:
            print("Username: ")
            username = input()
            print("Password: ")
            password = input()
            return self.player_service.login(username, password)
            print("Login successful.")
        except UserNotFoundException as e:
            print("User not found:", e)
        except Exception as e:
            print("An error occurred:", e)

    def leaderboard(self):
        print("---- Leaderboard ----")
        try:
            leaderboard = self.player_service.viewLeaderboard()
            if not leaderboard.players:
                print("Leaderboard is empty")
            else:
                print("Leaderboard:")
                for player in leaderboard.players:
                    print(f"Player: {player.username}, Score: {player.score}")
        except Exception as e:
            print("An error occurred:", e)
        self.menu()

    def player_account(self):
        print("------ Account ------")
        try:
            if self.loggedinuser is None:
                raise UserNotFoundException("No user is currently logged in.")
            user_details = self.player_service.viewProfile(self.loggedinuser)
            
            print(f"Name: {user_details.username}")
            print(f"User ID: {user_details.playerid}")
            print(f"Best Score: {user_details.highscore}")
            print(f"Total Games: {user_details.gamesPlayed}")
            print(f"Total Wins: {user_details.gamesWon}")
            
        except UserNotFoundException as e:
            print ("User not found:", e.message)
        except Exception as e:
            print ("An error occurred:", e)

        self.menu()

    def start_game(self):
        print("Waiting for players...")
        self.menu()
        #TODO

    def exit_game(self):
        while True:
            confirm = input ("Are you sure you want to exit the game? (y/n): ")
            if confirm.lower() == 'y':
                self.player_service.logout(self.loggedinuser)
                print ("Exiting the game. Godbless. Ingat Ka. Mwa")
                exit()
                return False
            elif confirm.lower() == 'n':
                print ("Returning to menu...")
                self.menu()
                return True
            else:
                print ("Invalid input. Please enter 'y' for yes or 'n' for no.")

# login method invocation
if __name__ == "__main__":
    client = PlayerClient()
    login_status = False
    while True:
        if not login_status:
            print("Please Login")
            client.loggedinuser = client.login()
            login_status = client.loggedinuser is not None

        if login_status:
            client.menu()