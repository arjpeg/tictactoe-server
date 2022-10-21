PLAYER1, PLAYER2 = "X", "O"


class TicTacToe:
    def __init__(self) -> None:
        self.winner: str | None = None
        self.grid = self.make_grid()

        self.moves = []

    def make_grid(self):
        g = []

        for _ in range(3):
            r = []
            for __ in range(3):
                r.append(" ")

            g.append(r)

        return g

    @property
    def last_player(self):
        return PLAYER1 if len(self.moves) % 2 else PLAYER2

    @property
    def last_player_won(self) -> bool:
        # Check if the game is over

        # Horizontals
        if any([all([x == self.last_player for x in row]) for row in self.grid]):
            print("HORIZONTAL")
            return True

        # Verticles
        for idx in range(len(self.grid)):
            if all([row[idx] == self.last_player for row in self.grid]):
                return True

        # Diagonals l->r
        if all(
            [self.grid[idx][idx] == self.last_player for idx in range(len(self.grid))]
        ):
            return True
        # r->l
        if all(
            [
                self.grid[idx][(idx * -1) + 2] == self.last_player
                for idx in range(len(self.grid))
            ]
        ):
            return True

        return False

    def play(self, player: str, row: int, col: int):
        if player == self.last_player:
            raise RuntimeError("It isn't your turn")

        if row > len(self.grid) or col > len(self.grid):
            raise RuntimeError("Move out of bounds")

        if self.grid[row][col] != " ":
            raise RuntimeError("Slot already full")

        self.grid[row][col] = player
        self.moves.append(player)

        if self.winner == None and self.last_player_won:
            self.winner = self.last_player

        return self.grid

    def clear(self):
        self.winner: str | None = None
        self.grid = self.make_grid()

        self.moves = []


if __name__ == "__main__":
    g = TicTacToe()

    def print_board():
        print()
        for r in g.grid:
            for c in r:
                print(c if c != " " else "_", end="")
            print()

        if g.winner:
            print(f"\b{g.winner} won!")

    g.play("X", 0, 0)
    print_board()
    g.play("O", 0, 2)
    print_board()
    g.play("X", 1, 1)
    print_board()
    g.play("O", 1, 2)
    print_board()
    g.play("X", 2, 2)
    print_board()
    g.play("O", 2, 0)
    print_board()
