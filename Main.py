import sys

# add or modify if sys variables isn't detected
#sys.path.append("C:/Users/czyl/Downloads/omniORB/omniORB-4.3.2/lib/python")
#sys.path.append("C:/Users/czyl/Downloads/omniORB/omniORB-4.3.2/lib/x86_win32")

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
            self.player_service.login(username, password)
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
    playerid = client.login(username, password)
    print(playerid)