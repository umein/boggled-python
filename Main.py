import threading
import time
import os
os.environ['ORBdebugLevel'] = '40'

from omniORB import CORBA
from connection import Connection
from boggled import UserNotFoundException, NotEnoughPlayersException, GameNotFoundException, NotExistingWordException

class PlayerClient:
    # establish connection to the server
    def __init__(self):
        self.connection = Connection()
        self.player_service = self.connection.get_player_service()
        self.loggedinuser = None
        self.remaining_time = 0
        self.people_in_lobby = 0
        self.round_number = 1
        self.score = 0
        self.generated_letters = []
        self.game_winner = None

    # menu
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
            player_data = self.player_service.login(username, password)
            if isinstance(player_data, int):
                player_data = {'playerid': player_data}
            self.loggedinuser = player_data
            self.loggedinuser_id = player_data['playerid']
            print("Login successful.")
            return player_data
        except UserNotFoundException as e:
            print("User not found:", e)
        except Exception as e:
            print("An error occurred:", e)

    # leaderboard function
    def leaderboard(self):
        print("\n---- Leaderboard ----")
        try:
            leaderboard = self.player_service.viewLeaderboard()
            if not leaderboard.players:
                print("Leaderboard is empty")
            else:
                print("Leaderboard:")
                top_players = leaderboard.players[:5]
                for player in top_players:
                    print(f"Player: {player.username}, Score: {player.score}")
        except Exception as e:
            print("An error occurred:", e)
        self.menu()

    # profile function
    def player_account(self):
        print("\n------ Account ------")
        try:
            if self.loggedinuser is None:
                raise UserNotFoundException("No user is currently logged in.")
            user_details = self.player_service.viewProfile(int(self.loggedinuser['playerid']))
            
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

    #start game function
    def start_game(self):
        try:
            self.remaining_time = self.player_service.waitingLobby(int(self.loggedinuser['playerid']))
            print(f"REMAINING TIME: {self.remaining_time} secs")
            self.people_in_lobby = self.player_service.getLobbySize()
            print(f"CURRENT PLAYERS IN LOBBY: {self.people_in_lobby}")

            while self.remaining_time != 0:
                old_time = self.remaining_time
                curr_players = self.people_in_lobby

                self.remaining_time = self.player_service.waitingLobby(int(self.loggedinuser['playerid']))
                self.people_in_lobby = self.player_service.getLobbySize()

                if old_time != self.remaining_time:
                    print(f"REMAINING TIME: {self.remaining_time} secs")

                if self.people_in_lobby != curr_players:
                    print(f"CURRENT PLAYERS IN LOBBY: {self.people_in_lobby}")

            if self.people_in_lobby < 2:
                raise NotEnoughPlayersException("Not enough players to start the game")
                
            self.round_number = 1
            print("Attempting to start the game...")
            self.player_service.startGame(self.loggedinuser['playerid'])
            self.play_round()

            while not self.game_has_winner():
                self.play_round()

            print(f"GAME WINNER: {self.game_winner.username} with score {self.game_winner.score}")
            self.exit_game() 

        except NotEnoughPlayersException as e:
            print(f"Error: {e.message}")
            return -1 

    def play_round(self):
        try:
            print(f"START GAME FOR: {self.loggedinuser}")
            self.score = 0

            self.generate_letters()
            round_remaining_time = self.player_service.getRoundTime(self.loggedinuser['playerid'])

            while round_remaining_time > 0:
                old_time = round_remaining_time
                round_remaining_time = self.player_service.getRoundTime(self.loggedinuser['playerid'])


                if old_time!= round_remaining_time:
                    print(f"ROUND TIME: {round_remaining_time} secs")

                if round_remaining_time == 0:
                    break

                word = input("\nEnter a word: ")
                self.submit_word(word)

                time.sleep(1)

            print("Time's up")

            game_winner = self.player_service.getGameWinner(self.loggedinuser['playerid'])

            if game_winner.username == "none":
                self.round_number += 1
                in_between_rounds_time = self.player_service.getRoundWaitingTime(self.loggedinuser['playerid'])

                while in_between_rounds_time > 0:
                    old_time = in_between_rounds_time
                    in_between_rounds_time = self.player_service.getRoundWaitingTime(self.loggedinuser['playerid'])

                    if old_time!= in_between_rounds_time:
                        print(f"IN BETWEEN ROUNDS TIME: {in_between_rounds_time} secs")

                    time.sleep(1)

            else:
                self.game_winner = game_winner

        except GameNotFoundException as ex:
            print(ex.message)
            self.menu()
    
    # generate letters function
    def generate_letters(self):
        try:
            game_letters = self.player_service.getLetters(self.loggedinuser['playerid'])
            print("Generated letters:")
            self.generated_letters = game_letters.letters
            retrieved_letters = game_letters.letters
            print("Retrieved letters:", "".join(retrieved_letters))
            self.populate_letters(retrieved_letters)
            return game_letters
        except GameNotFoundException as ex:
            print("Game not found:", ex)
            raise ex
        except Exception as e:
            print("An error occurred while generating letters:", e)

    
    def can_form_word(self, word):

        word_lower = word.lower()
        available_letters_lower = [char.lower() for char in self.generated_letters]

        for char in word_lower:
            if char in available_letters_lower:
                available_letters_lower.remove(char)
            else:
                return False
            return True

    # populate letters function
    def populate_letters(self, letters):
        grid_size = 5  
        grid = []
        for i in range (grid_size):
            row = []
            for j in range (grid_size):
                index = i * grid_size + j
                if index < len (letters):
                    row.append (letters[index])
                else:
                    row.append (' ')  
            grid.append (row)

        print ("\n+-------------------------+")
        print ("|         Letters         |")
        print ("+-------------------------+")
        print ("|                         |")
        self.sent_words = []
        for i, row in enumerate(grid, 1):
            letter_str = "       " + " ".join(row) + "       "
            print (f"| {letter_str:<20} |")
        print ("+-------------------------+")

    def submit_word(self, word):
        try:
            if not self.can_form_word(word):
                print(f"Word '{word}' cannot be formed with the given letters.")
                return
            score = self.player_service.submitWords(self.loggedinuser['playerid'], word)
            print (f"Word '{word}' sent successfully! Your score is {score}.")
        except NotExistingWordException as e:
            print (f"Error: {e}")
        except GameNotFoundException as e:
            print (f"Error: {e}")
        except Exception as e:
            print (f"An error occurred: {e}")

    # game winner function
    def game_has_winner(self):
        try:
            player_data = self.player_service.getGameWinner(self.loggedinuser['playerid'])
            if player_data.username == "none":
                return False
            else:
                self.game_winner = player_data
                print(f"\nGame winner: {player_data.username} \nScore: {player_data.score}")
                return True
        except GameNotFoundException as ex:
            return True
        except Exception as e:
            print("An error occurred while checking for a game winner:", e)
            return False

    # exit game function
    def exit_game(self):
        while True:
            confirm = input ("Are you sure you want to exit the game? (y/n): ")
            if confirm.lower() == 'y':
                self.player_service.logout(self.loggedinuser['playerid'])
                print ("Exiting the game. Godbless. Ingat Ka. Mwa")
                exit()
                return False
            elif confirm.lower() == 'n':
                print ("Returning to menu...")
                self.menu()
                return True
            else:
                print ("Invalid input. Please enter 'y' for yes or 'n' for no.")

    

# method invocation
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
