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

    def release_properties(self, player):
        for prop in player.properties:
            prop.owner = None
        player.properties.clear()

    def sell_property(self, player, prop):
        sell_price = prop.price // 2
        player.money += sell_price
        prop.owner = None
        player.properties.remove(prop)
        print(f"{player.name} sold {prop.name} for ${sell_price}. New balance: ${player.money}")

    def attempt_property_sale(self, player, target_amount=0):
        while (player.money < target_amount or (target_amount == 0 and player.money < 0)) and player.properties:
            print(f"\n{player.name} has ${player.money} and needs ${target_amount}.")
            print("Choose a property to sell:")
            for idx, prop in enumerate(player.properties, start=1):
                print(f"  {idx}. {prop.name} (worth ${prop.price}, sell for ${prop.price // 2})")
            print("  0. Stop selling")
            try:
                choice = int(input("Select property number to sell: "))
            except ValueError:
                print("Invalid input. Enter a number.")
                continue
            if choice == 0:
                break
            if 1 <= choice <= len(player.properties):
                self.sell_property(player, player.properties[choice - 1])
            else:
                print("Invalid choice.")
        return player.money >= target_amount or (target_amount == 0 and player.money >= 0)

    def check_bankruptcy(self, player):
        if player.money >= 0:
            return False
        if player.properties:
            print(f"{player.name} is bankrupt but has properties to sell.")
            if self.attempt_property_sale(player, target_amount=0) and player.money >= 0:
                print(f"{player.name} recovered from bankruptcy with property sales.")
                return False
        print(f"{player.name} is bankrupt and removed from the game.")
        self.release_properties(player)
        if player in self.players:
            self.players.remove(player)
        if len(self.players) == 1:
            self.game_over = True
        return True

    def collect_payment(self, payer, payee, amount):
        if payer.money >= amount:
            payer.money -= amount
            payee.money += amount
            return True
        print(f"{payer.name} cannot afford ${amount}. Attempting to sell properties.")
        if not self.attempt_property_sale(payer, target_amount=amount):
            return False
        if payer.money >= amount:
            payer.money -= amount
            payee.money += amount
            print(f"{payer.name} paid ${amount} to {payee.name} after selling properties.")
            return True
        return False

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
            if self.collect_payment(player, property.owner, rent):
                print(f"{player.name} paid ${rent} rent to {property.owner.name}")
            else:
                print(f"{player.name} couldn't pay rent and is now bankrupt.")
                self.check_bankruptcy(player)
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
            print(f"{player.name} is bankrupt! Attempting property sale to recover...")
            self.check_bankruptcy(player)

    def play_minigame(self, player):
        """Play a short minigame for bonus/penalty money."""
        print("\n🎮 Minigame time! Win money to help your run.")
        minigames = [self._minigame_guess_dice, self._minigame_rps, self._minigame_trivia]
        game = random.choice(minigames)
        game(player)

    def _minigame_guess_dice(self, player):
        print("Minigame: Guess the dice roll (1-6)")
        try:
            guess = int(input("Your guess: "))
        except ValueError:
            print("Invalid input. You lose your turn and $25.")
            player.money -= 25
            return
        roll = random.randint(1, 6)
        print(f"Dice rolled: {roll}")
        if guess == roll:
            reward = 100
            player.money += reward
            print(f"Nice! You win ${reward}.")
        else:
            penalty = 25
            player.money -= penalty
            print(f"Nope. You lose ${penalty}.")

    def _minigame_rps(self, player):
        print("Minigame: Rock Paper Scissors (best of 3)")
        options = ["rock", "paper", "scissors"]
        score = 0
        for round_num in range(1, 4):
            comp = random.choice(options)
            choice = input(f"Round {round_num} - rock/paper/scissors? ").strip().lower()
            if choice not in options:
                print("Invalid choice, you forfeit the round.")
                score -= 1
            else:
                if choice == comp:
                    print(f"Tie (computer chose {comp}).")
                elif (choice == "rock" and comp == "scissors") or (choice == "paper" and comp == "rock") or (choice == "scissors" and comp == "paper"):
                    print(f"You win the round! (computer chose {comp})")
                    score += 1
                else:
                    print(f"You lose the round. (computer chose {comp})")
                    score -= 1
        if score > 0:
            reward = 150
            player.money += reward
            print(f"You won the match! +${reward}.")
        elif score < 0:
            penalty = 75
            player.money -= penalty
            print(f"You lost the match. -${penalty}.")
        else:
            print("Match tied. No money exchanged.")

    def _minigame_trivia(self, player):
        print("Minigame: Trivia Challenge")
        questions = [
            ("What is the capital of France?", "paris"),
            ("How many continents are there?", "7"),
            ("What planet is known as the Red Planet?", "mars"),
        ]
        question, answer = random.choice(questions)
        guess = input(f"{question} ").strip().lower()
        if guess == answer:
            reward = 120
            player.money += reward
            print(f"Correct! You earn ${reward}.")
        else:
            penalty = 60
            player.money -= penalty
            print(f"Wrong. The answer was {answer}. You lose ${penalty}.")

    def play_turn(self, player):
        input(f"{player.name}'s turn. Press enter to roll dice.")

        secret = input("Enter secret code for an instant win (or press enter to continue): ").strip()
        if secret.lower() in ["eureka", "openwin", "abracadabra"]:
            print(f"Secret code accepted! {player.name} wins the game instantly!")
            self.players = [player]
            self.game_over = True
            return

        dice = self.roll_dice()
        print(f"Rolled {dice}")
        property = self.move_player(player, dice)
        self.handle_property(player, property)
        if random.random() < 0.3:  # 30% chance for random event
            self.random_event(player)
        if random.random() < 0.2:  # 20% chance to trigger a minigame
            self.play_minigame(player)
            if player.money < 0:
                print(f"{player.name} went bankrupt during the minigame! Attempting property sale to recover...")
                self.check_bankruptcy(player)

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