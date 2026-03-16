import random

class Property:
    def __init__(self, name, price, rent):
        self.name = name
        self.price = price
        self.rent = rent
        self.owner = None

class Player:
    def __init__(self, name, money=1500):
        self.name = name
        self.money = money
        self.properties = []
        self.position = 0

class MonopolyTrailGame:
    def __init__(self, players):
        self.players = players
        self.properties = [
            Property("Boardwalk", 400, 50),
            Property("Park Place", 350, 35),
            Property("Marvin Gardens", 280, 24),
            Property("Ventnor Avenue", 260, 22),
            Property("Atlantic Avenue", 260, 22),
            Property("Illinois Avenue", 240, 20),
            Property("Indiana Avenue", 220, 18),
            Property("Kentucky Avenue", 220, 18),
            Property("New York Avenue", 200, 16),
            Property("Tennessee Avenue", 180, 14),
            Property("St. James Place", 180, 14),
            Property("Virginia Avenue", 160, 12),
            Property("States Avenue", 140, 10),
            Property("St. Charles Place", 140, 10),
            Property("Pennsylvania Avenue", 160, 12),
            Property("North Carolina Avenue", 300, 26),
            Property("Pacific Avenue", 300, 26),
            Property("Pennsylvania Railroad", 200, 25),
            Property("Reading Railroad", 200, 25),
            Property("B&O Railroad", 200, 25),
            Property("Short Line", 200, 25),
            Property("Electric Company", 150, 75),  # Rent is 4x dice roll
            Property("Water Works", 150, 75),  # Rent is 4x dice roll
        ]
        self.board_size = len(self.properties)
        self.current_player_index = 0
        self.game_over = False

    def roll_dice(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def move_player(self, player, steps):
        player.position = (player.position + steps) % self.board_size
        landed_property = self.properties[player.position]
        print(f"{player.name} landed on {landed_property.name}")
        return landed_property

    def handle_property(self, player, property):
        if property.owner is None:
            if player.money >= property.price:
                choice = input(f"Do you want to buy {property.name} for ${property.price}? (y/n): ").lower()
                if choice == 'y':
                    player.money -= property.price
                    player.properties.append(property)
                    property.owner = player
                    print(f"{player.name} bought {property.name}")
                else:
                    print(f"{player.name} passed on {property.name}")
            else:
                print(f"{player.name} doesn't have enough money to buy {property.name}")
        elif property.owner != player:
            rent = property.rent
            if "Railroad" in property.name:
                railroads_owned = len([p for p in property.owner.properties if "Railroad" in p.name])
                rent = 25 * (2 ** (railroads_owned - 1))
            elif property.name in ["Electric Company", "Water Works"]:
                utilities_owned = len([p for p in property.owner.properties if p.name in ["Electric Company", "Water Works"]])
                dice_roll = self.roll_dice()
                rent = dice_roll * (4 if utilities_owned == 1 else 10)
            if player.money >= rent:
                player.money -= rent
                property.owner.money += rent
                print(f"{player.name} paid ${rent} rent to {property.owner.name}")
            else:
                print(f"{player.name} can't afford rent! Game over for {player.name}")
                self.players.remove(player)
                if len(self.players) == 1:
                    self.game_over = True
        else:
            print(f"{player.name} owns {property.name}")

    def random_event(self, player):
        events = [
            ("You found a wallet with $100!", 100),
            ("You got sick and paid $50 for medicine.", -50),
            ("You won a lottery! +$200", 200),
            ("Flat tire! Pay $30 for repair.", -30),
            ("Bonus from job! +$150", 150),
            ("Lost your luggage! Pay $40 to replace.", -40),
        ]
        event, amount = random.choice(events)
        player.money += amount
        print(f"Random event: {event} ({'+' if amount > 0 else ''}${amount})")
        if player.money < 0:
            print(f"{player.name} is bankrupt!")
            self.players.remove(player)
            if len(self.players) == 1:
                self.game_over = True

    def play_turn(self, player):
        input(f"{player.name}'s turn. Press enter to roll dice.")
        dice = self.roll_dice()
        print(f"Rolled {dice}")
        property = self.move_player(player, dice)
        self.handle_property(player, property)
        if random.random() < 0.3:  # 30% chance for random event
            self.random_event(player)

    def play_game(self):
        print("Welcome to Monopoly Trail!")
        while not self.game_over and len(self.players) > 1:
            player = self.players[self.current_player_index]
            self.play_turn(player)
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.players:
            print(f"{self.players[0].name} wins!")
        else:
            print("All players bankrupt!")

if __name__ == "__main__":
    num_players = int(input("Enter number of players: "))
    players = []
    for i in range(num_players):
        name = input(f"Enter name for player {i+1}: ")
        players.append(Player(name))
    game = MonopolyTrailGame(players)
    game.play_game()