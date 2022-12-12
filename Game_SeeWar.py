from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardBusyException(BoardException):
    def __str__(self):
        return "В эту клетку уже был выстрел"

class BoardOutException(BoardException):
    def __str__(self):
        return "Стрельба за игровое поле!"

class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, size_ship, rotation):
        self.bow = bow
        self.size_ship = size_ship
        self.rotation = rotation
        self.lives = rotation

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.size_ship):
            nap_x = self.bow.x
            nap_y = self.bow.y

            if self.rotation == 0:
                nap_x += i

            elif self.rotation == 1:
                nap_y += i

            ship_dots.append(Dot(nap_x, nap_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.use = []
        self.ships = []

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.use:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.use.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.use:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.use.append(cur)

    def __str__(self):
        coord = ""
        coord += "   1  2  3  4  5  6 "
        for i, row in enumerate(self.field):
            coord += f"\n{i + 1}  " + "  ".join(row) + " "

        if self.hid:
            coord = coord.replace("■", "O")
        return coord

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardBusyException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "*"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Вы потопили корабль соперника!")
                    return False
                else:
                    print("Корабль соперника ранен!")
                    return True

        self.field[d.x][d.y] = "~"
        print("Вы промахнулись!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, board, comp):
        self.board = board
        self.comp = comp

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.comp.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Необходимо ввести 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Необходимо ввести целые числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("_" * 20)
        print("  ДОБРО ПОЖАЛОВАТЬ!!  ")
        print("      В ИГРУ       ")
        print("    МОРСКОЙ БОЙ    ")
        print("_" * 20)
        print(" формат ввода: x y ")
        print(" x - горизонталь  ")
        print(" y - вертикаль ")

    def loop(self):
        num = 0
        while True:
            print("_" * 20)
            print("Ваше игровое поле:")
            print(self.us.board)
            print("_" * 20)
            print("Поле соперника:")
            print(self.ai.board)
            if num % 2 == 0:
                print("_" * 20)
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ход соперника!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Поздравляем, Вы выиграли!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Соперник победил!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()