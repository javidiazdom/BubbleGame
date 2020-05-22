import arcade
import copy
import sys
from table import game_table

ORANGE = 255, 167, 0
GREEN = 100, 140, 17
YELLOW = 255, 255, 0


class Bubble():
    def __init__(self,color):
        super().__init__()
        self.table = []
        self.color = color

    def add_to_bubble(self, pos):
        self.table.append(pos)

    def is_on_bubble(self, t):
        return t in self.table

    def __str__(self):
        return str(self.table)
    
    def get_points(self):
        if self.color == ORANGE:
            return len(self.table) * (len(self.table) -1)
        else:
            return len(self.table) * (len(self.table) -1) * 2

    

class Board():
    def __init__(self, table):
        self.table = table
        self.bubbles = []

    def value (self, color):
        final_value=0
        for i in range (0,11):
            for j in range (0,10):
                if self.table[i][j] == color:
                    final_value+= i
        return final_value

    def delete_bubble(self, bubble):
        for x,y in bubble.table:
            self.table[x][y] = None
    
    def pop_bubble(self, bubble):
        self.delete_bubble(bubble)
        self.fill_blanc_spots()


    def pop(self, x, y):
        n = 0
        if self.has_near_boxes(x,y):
            n = self.delete_boxes((x,y))
            self.fill_blanc_spots()
        return n

    def calculate_bubbles(self):
        self.bubbles = []
        cache = set()
        cells = []
        def calculate_bubble(x,y):
            color = self.get_color(x,y)
            cells.append((x,y))
            cache.add((x,y))
            to_check = [(x-1,y),(x,y-1),(x,y+1),(x+1,y)]
            for x1,y1 in to_check:
                if x1 < 0 or x1 > 10 or y1 < 0 or y1 > 9 or ((x1,y1) in cache):
                    to_check.remove((x1,y1))
            for xT,yT in to_check:
                if (xT,yT) not in cache:
                    if self.get_color(xT,yT) == color:
                        calculate_bubble(xT,yT)
        
        for x in range(0,11):
            for y in range(0,10):
                if (x,y) not in cache and (self.table[x][y] is not None):
                    if self.has_near_boxes(x,y):
                        bubble = Bubble(self.get_color(x,y))
                        cells = []
                        calculate_bubble(x,y)
                        for cell in cells:
                            bubble.add_to_bubble(cell)
                        self.bubbles.append(bubble)
    
    def has_near_boxes(self,x,y):
        current_color = self.get_color(x,y)
        boxes = [(x-1,y),(x,y+1),(x,y-1),(x+1,y)]
        for xT,yT in boxes:
            if self.get_color(xT,yT) == current_color:
                return True
        return False

    def get_color(self, x, y):
        if x > 10 or y > 9 or x < 0 or y < 0:
            return None
        return self.table[x][y]

    def delete_boxes(self,t):
        for bubble in self.bubbles:
            if bubble.is_on_bubble(t):
                self.delete_bubble(bubble)
                return bubble.get_points()
        return None
    
    def fill_blanc_spots(self):
        for i in range (0,11):
            for j in range (0,10):
                if self.table[i][j] is None:
                    for k in range (i,0,-1):
                        self.table[k][j] = self.table[k-1][j]
                        
                    self.table[0][j] = None
    
    def get_casillas_a_eliminar(self, x,y):
        for bubble in self.bubbles:
            if bubble.is_on_bubble(x,y):
                return bubble


class BubbleGame(arcade.Window):
    def __init__ (self, width, height, title, board):
        super().__init__(width, height, title)
        self.current_player = False
        self.player1Color = GREEN
        self.player2Color = YELLOW

        self.player1_points = 0
        self.player2_points = 0

        self.board = board
        self.board.calculate_bubbles()

        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):
        pass

    def on_draw(self):
        arcade.start_render()

        arcade.draw_lrtb_rectangle_filled(100, 500, 540, 100, arcade.color.BABY_BLUE)

        for i in range(0,11):
            arcade.draw_line(100 + (i*40), 540, 100 + (i*40), 100, arcade.color.BLACK, 1)
            arcade.draw_line(100, 500 - (i*40), 500, 500 - (i*40), arcade.color.BLACK, 1)


        #for bubble in self.board.bubbles: 
        self.drawBoard()
        
    def drawBoard(self):
        currentX = 101
        currentY = 539
        for row in self.board.table:
            for item in row:
                if item is not None:
                    arcade.draw_lrtb_rectangle_filled(currentX,currentX + 38 , currentY, currentY - 38,item)
                currentX += 40
            currentY-= 40
            currentX= 101
        
        arcade.draw_text("Puntuaciones: Player 1 = " + str(self.player1_points) + ", Player 2 = " + str(self.player2_points), 150, 560, arcade.color.BLACK, 16)
            
    def update_points(self,points,player):
        if points is None:
            return
        if player == 1:
            self.player1_points += points
        if player == 2:
            self.player2_points += points
        self.current_player = not self.current_player
        self.board.calculate_bubbles()
        
        
    def on_key_press(self, symbol, modifiers):
        current_player = self.current_player
        color_actual = GREEN if current_player else YELLOW
        movimientos = []
        for bubble in self.board.bubbles:
            if bubble.color == color_actual or bubble.color == ORANGE:
                movimientos.append(bubble)


        movimientos_min = {}
        for movimiento in movimientos:
            new_tablero = self.expandir(movimiento, self.board.table[:])
            movimientos_min[movimiento] = self.calcular_min(new_tablero)

        if (bool(movimientos_min)):
            
            for movimiento in movimientos_min:
                print("Movimiento:",str(movimiento), "valor asignado: ", movimientos_min[movimiento])

            movimientos_maximo = max(movimientos_min, key=movimientos_min.get)
            casillaX,casillaY = movimientos_maximo.table[0]
            self.move(casillaX,casillaY)
        else: 
            self.current_player = not current_player



    def calcular_min(self, tablero):
        tablero.calculate_bubbles()
        color_min = GREEN if self.current_player else YELLOW
        movimientos = []
        for bubble in tablero.bubbles:
            if bubble.color == color_min or bubble.color == ORANGE:
                movimientos.append(bubble)
        
        puntuacion = 0
        mejor_puntuacion = sys.maxsize
        for movimiento in movimientos:
            new_tablero = self.expandir(movimiento, tablero.table[:])
            puntuacion = movimiento.get_points() + new_tablero.value(movimiento.color)
            if puntuacion < mejor_puntuacion:
                mejor_puntuacion = puntuacion

        return puntuacion

    def expandir(self, movimiento, tablero_anterior):
        new_tablero = Board(copy.deepcopy(tablero_anterior))
        new_tablero.pop_bubble(movimiento)
        return new_tablero


    def move(self,x,y):
        player = 1 if self.current_player else 2
        self.update_points(self.board.pop(x, y),player)

    
    def on_mouse_press(self, x,y, button, key_modifiers):
        if (button == 1):
            color,newX,newY = self.get_clicked_colour(x,y)
            if color is not None:
                if self.current_player and color == self.player1Color:
                    n_casillas = self.board.pop(newX, newY)
                    self.update_points(n_casillas,1)
                if (not self.current_player) and color == self.player2Color:
                    n_casillas = self.board.pop(newX, newY)
                    self.update_points(n_casillas,2)
                if color == ORANGE:
                    n_casillas = self.board.pop(newX, newY)
                    self.update_points(n_casillas,1 if self.current_player else 2)

    

    def get_clicked_colour(self,x,y):
        if (x < 100 or y > 540 or x > 500 or y < 100):
            return None,None,None
        else:
            newX = (x - 100) // 40
            newY = (y - 100) // 40
            return self.board.table[10-newY][newX], 10-newY,newX


def main():
    game = BubbleGame(600,640,"Bubble game", Board(game_table))
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()