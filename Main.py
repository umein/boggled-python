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

# login method invocation
if __name__ == "__main__":
    client = PlayerClient()
    print("Username: ")
    username = input()
    print("Password: ")
    password = input()
    loggedinuser = client.login(username, password)
    print(loggedinuser)