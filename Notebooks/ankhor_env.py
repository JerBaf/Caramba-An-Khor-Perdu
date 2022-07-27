import matplotlib.pyplot as plt
import numpy as np
import random



class Tile:
    """
    Description:
        Representation of a game tile. A tile is described by
        its color and its symbol. When a tile is not placed yet,
        it has a default state on the grid: "Blank" color and 
        "Empty" symbol.
        
    Parameters:
        color: (String) Color of the tile. Must be in the valid set of colors.
        
    """
    
    DEFAULT_COLOR = "Blank"
    DEFAULT_SYMBOL = "Empty"
    SET_OF_COLORS = {"Red","Blue","Green","Black","White"}
    SET_OF_SYMBOLS = {"Bird","Dog","Scarab","Scrib","Storage","Desert","Bonus"}
    SYMBOL_NUMBER_DICT = {"Bird":2,"Dog":2,"Scarab":2,"Scrib":1,"Storage":1,"Desert":1,"Bonus":2}
    
    
    def __init__(self,color=DEFAULT_COLOR,symbol=DEFAULT_SYMBOL):
        if color not in Tile.SET_OF_COLORS and color != Tile.DEFAULT_COLOR:
            raise ValueError
        if symbol not in Tile.SET_OF_SYMBOLS and symbol != Tile.DEFAULT_SYMBOL:
            raise ValueError
        self.color = color
        self.symbol = symbol
        
    @staticmethod
    def create_tiles_values_mappings():
        """ Create the mapping between integers on the grid and the tiles. """
        tile_to_value = {(Tile.DEFAULT_COLOR,Tile.DEFAULT_SYMBOL):0}
        value_to_tile = {0:(Tile.DEFAULT_COLOR,Tile.DEFAULT_SYMBOL)}
        colors = sorted(Tile.SET_OF_COLORS)
        symbols = sorted(Tile.SET_OF_SYMBOLS)
        i = 1
        for c in colors:
            for s in symbols:
                tile_to_value[(c,s)] = i
                value_to_tile[i] = (c,s)
                i += 1
        return tile_to_value, value_to_tile

class Deck:
    """
    Description:
        Representation of the two stack of Tiles from which the
        players can draw. The stacks are randomly shuffled according
        to the given seed.
        
    Parameters:
        seed: (int) Seed for initialization of the random number generator.
    
    """
    def __init__(self,seed=0):
        random.seed(seed)
        np.random.seed(seed)
        init_deck = []
        for c in Tile.SET_OF_COLORS:
            for s, n in Tile.SYMBOL_NUMBER_DICT.items():
                for i in range(n):
                    init_deck.append(Tile(c,s))
        random.shuffle(init_deck)
        self.stack_0 = init_deck[:len(init_deck)//2]
        self.stack_1 = init_deck[len(init_deck)//2:]
        
    def draw(self,stack):
        """ Draw a tile from the given stack. """
        if stack == 0:
            return self.stack_0.pop(0)
        else:
            return self.stack_1.pop(0)
        
    def tile_available(self):
        """ Return a tuple of the two available tiles'color. """
        Tile_0 = None
        Tile_1 = None
        if len(self.stack_0) != 0:
            Tile_0 = self.stack_0[0].color
        if len(self.stack_1) != 0:
            Tile_1 = self.stack_1[0].color
        return Tile_0, Tile_1

class Token():
    """
    Description:
        Representation of the token needed to buy
        tiles.
    
    Parameters:
        color: (String) Color of the token. Must be
                        included in "Red","Green","Blue",
                        "Black","White" or "Ankh".
    
    """
    
    REGULAR_COLORS = {"Red","Green","Blue","Black","White"}
    SPECIAL_COLOR = "Ankh"
    
    def __init__(self,color):
        if color not in Token.REGULAR_COLORS and color != Token.SPECIAL_COLOR:
            raise ValueError
        self.color = color

class Ressource_Pool():
    """
    Description:
        Representation of the pool of tokens needed to buy
        tiles. The regular and special colors are treated separately
        as they undergo different rules. Each color pool is a queue
        of tokens.
        
    Parameters:
        init_reg_nb: (int) Initial number of regular token.
        init_special_nb: (int) Initial number of special token.
        max_regular_nb: (int) Maximum number of regular token per color.
        max_special_nb: (int) Maximum number of special token.
        max_tot_reg_nb: (int) Maximum number of regular token accross all colors.
    
    """
    
    def __init__(self,init_reg_nb,init_special_nb,max_regular_nb,
                     max_special_nb,max_tot_reg_nb):
        self.MAX_REGULAR_NB = max_regular_nb
        self.MAX_SPECIAL_NB = max_special_nb
        self.MAX_REG_POOL_SIZE = max_tot_reg_nb
        self.red_tokens = [Token("Red") for i in range(init_reg_nb)]
        self.green_tokens = [Token("Green") for i in range(init_reg_nb)]
        self.blue_tokens = [Token("Blue") for i in range(init_reg_nb)]
        self.black_tokens = [Token("Black") for i in range(init_reg_nb)]
        self.white_tokens = [Token("White") for i in range(init_reg_nb)]
        self.ankh_tokens = [Token("Ankh") for i in range(init_special_nb)]
        self.pool_dict = {"Red":self.red_tokens,"Green":self.green_tokens,
                           "Blue":self.blue_tokens,"Black":self.black_tokens,
                           "White":self.white_tokens,"Ankh":self.ankh_tokens}
        
    def state(self):
        state_dict = dict()
        for c in self.pool_dict.keys():
            state_dict[c] = len(self.pool_dict[c])
        state_dict[Token.SPECIAL_COLOR] = len(self.pool_dict[Token.SPECIAL_COLOR])
        return state_dict
        
    
    def fill(self, color):
        """ Add a token of the given color to the ressource pool. """
        color_pool = self.pool_dict[color]
        max_color_pool_size = (self.MAX_SPECIAL_NB if color == Token.SPECIAL_COLOR
                                    else self.MAX_REGULAR_NB)
        total_regular_pool_size = sum([len(self.pool_dict[c]) for c in Token.REGULAR_COLORS])
        if len(color_pool) >= max_color_pool_size:
            raise Exception(f"Maximum number of token reached for the color {color}")
        elif color != Token.SPECIAL_COLOR and total_regular_pool_size >= self.MAX_REG_POOL_SIZE:
            raise Exception(f"Maximum number of total token reached: {total_regular_pool_size}")
        else:
            color_pool.append(Token(color))
        
    def draw(self, color):
        """ Draw a token of the given color to the ressource pool. """
        if len(self.pool_dict[color]) <= 0:
            raise Exception(f"No token left for the color {color}")
        else:
            self.pool_dict[color].pop(0)

class Shop:
    """
    Desciption:
        Representation of the Shop in the game. It possesses
        the deck and the global ressource pool in addition to 
        its standard commodities, namely the prices and the tiles 
        queue. In our implementation, the shop is authoritative. 
        By authoritative, we mean that this is the shop who makes
        the transactions. Thus it has the right to modify the players'
        ressource pools.
        
    Parameters:
        seed: (int) Seed for initialization of the random number generator.
        player_nb: (int) Number of players in the game.
    
    """
    
    def __init__(self,seed=0,player_nb=2):
        # Initialize shop ressource pool
        self.PLAYER_NB = player_nb
        init_token_nb = 3 + self.PLAYER_NB
        self.ressource_pool = Ressource_Pool(init_token_nb,init_token_nb,
                                init_token_nb,init_token_nb,
                                len(Token.REGULAR_COLORS)*init_token_nb)
        # Initialize the game deck
        self.deck = Deck(seed)
        # Randomly shuffle the prices
        random.seed(seed)
        np.random.seed(seed)
        initial_token_pool = [Token(c) for c in list(Token.REGULAR_COLORS)*3]
        random.shuffle(initial_token_pool)
        # Create the fixed list of prices
        self.price_list = []
        j = 0
        for i in [2,2,2,3,3,3]:
            self.price_list.append(initial_token_pool[j:j+i])
            j=j+i
        # Initialize the queue of tiles
        self.SHOP_SIZE = 6
        self.tiles_queue = []
        for i in range(self.SHOP_SIZE):
            stack_choice = np.random.randint(2)
            self.tiles_queue.append(self.deck.draw(stack_choice))
    
    def state(self):
        """ Return the state of the different attributes of the shop. """
        state_dict = dict()
        state_dict["Tiles_Queue"] = self.tiles_queue
        state_dict["Price_List"] = self.price_list
        state_dict["Deck"] = self.deck
        state_dict["Ressource_Pool"] = self.ressource_pool
        return state_dict
    
    def print_state(self):
        """ Visualization of the shop's state. """
        state_dict = self.state()
        tiles_queue = [(t.color,t.symbol) for
                                         t in state_dict["Tiles_Queue"]]
        
        price_list = [[t.color for t in l] for
                                         l in state_dict["Price_List"]]
        ressource_pool = state_dict["Ressource_Pool"].state()
        print(tiles_queue)
        print(price_list)
        print(state_dict["Deck"].tile_available())
        print(ressource_pool)
            
    def get_tile_price(self,tile_index):
        """ Return a dictionnary with the amount of token per color. """
        if tile_index < 0 or tile_index >= self.SHOP_SIZE:
            raise ValueError("Invalid tile index.")
        tile_price = dict.fromkeys(self.ressource_pool.pool_dict.keys(),0)
        for c in map(lambda t : t.color,self.price_list[tile_index]):
            tile_price[c] += 1
        return tile_price
    
    def update_tiles_queue(self,tile_index,stack_choice):
        """ Retrieve the wanted tile and update the tile queue. """
        bought_tile = self.tiles_queue.pop(tile_index)
        new_tile = self.deck.draw(stack_choice)
        self.tiles_queue.append(new_tile)
        return bought_tile
            
    def buy(self,tile_index,player_ressource_pool,stack_choice):
        """ Verify if the transaction is valid, and if so perform it. """
        if tile_index < 0 or tile_index >= self.SHOP_SIZE:
            raise ValueError("Invalid tile index.")
        if stack_choice not in [0,1]:
            raise ValueError("Invalid stack choice.")
        tile_price = self.get_tile_price(tile_index)
        player_ressource_state = player_ressource_pool.state()
        # Check if the player has the ressource to buy
        for color, price in tile_price.items():
            if player_ressource_state[color] < price:
                raise Exception(f"Not enough token of color {color} to buy the given tile.")
        # Make the transaction
        for color, price in tile_price.items():
            for i in range(price):
                player_ressource_pool.draw(color)
                self.ressource_pool.fill(color)
        # Update the tile queue
        bought_tile = self.update_tiles_queue(tile_index,stack_choice)
        return bought_tile
            
    def destroy(self,player_ressource_pool,stack_choice):
        """ Destroy the first tile of the queue in exchange of an Ankh. """
        player_ressource_state = player_ressource_pool.state()
        if player_ressource_state[Token.SPECIAL_COLOR] < 1:
            raise Exception(f"Not enough {Token.SPECIAL_COLOR} tokens to destroy.")
        # Make the transaction
        player_ressource_pool.draw(Token.SPECIAL_COLOR)
        self.ressource_pool.fill(Token.SPECIAL_COLOR)
        # Update the tile queue
        destroyed_tile = self.update_tiles_queue(0,stack_choice)
        
    def draw_ressources(self,player_ressource_pool,token_list):
        """ Verifiy if the transaction is valid, and if so perform it. """
        if len(token_list) > 3 or len(token_list) < 1:
            raise ValueError(f"The token_list should contain 1,2 or 3 elements not {len(token_list)}.")
        # Reformat tokens list into a dictionnary
        token_colors = [t.color for t in token_list 
                               if (t.color in Token.REGULAR_COLORS or 
                                  t.color == Token.SPECIAL_COLOR)]
        token_dict = dict.fromkeys(self.ressource_pool.pool_dict.keys(),0)
        for c in token_colors:
            token_dict[c] += 1
        # Check if the transaction is valid
        shop_ressource_state = self.ressource_pool.state()
        player_ressource_state = player_ressource_pool.state()
        # Check per color
        for color, number in token_dict.items():
            if shop_ressource_state[color] < number:
                raise Exception(f"Not enough token of color {color} in the shop.")
            elif (color == Token.SPECIAL_COLOR and 
                  player_ressource_state[color]+number > player_ressource_pool.MAX_SPECIAL_NB):
                raise Exception(f"Would exceed maximum number of token of color {color}.")
            elif (color in Token.REGULAR_COLORS and 
                  player_ressource_state[color]+number > player_ressource_pool.MAX_REGULAR_NB):
                raise Exception(f"Would exceed maximum number of token of color {color}.")
        # Check condition on all regular colors
        total_regular_token_number = sum([token_dict[c]
                                          for c in Token.REGULAR_COLORS])
        total_regular_pool_size = sum([len(player_ressource_pool.pool_dict[c]) 
                                           for c in Token.REGULAR_COLORS])
        if (total_regular_pool_size + total_regular_token_number > 
            player_ressource_pool.MAX_REG_POOL_SIZE):
            raise Exception(f"Would exceed maximum number of token for regular colors.")
        # Make the transaction
        for color, number in token_dict.items():
            for i in range(number):
                player_ressource_pool.fill(color)
                self.ressource_pool.draw(color)


class Player:
    """
    Description:
        Representation of a player in the game. It has
        a unique ID and a ressource pool.
        
    Parameters:
        player_id: (int) Unique player id.
    
    """
    
    def __init__(self,player_id):
        self.ressource_pool = Ressource_Pool(0,0,5,2,5) 
        self.ID = player_id

class Grid:
    """
    Description:
        Representation of the different player grids.
        The game grid is composed of a 25x25 numpy arrays
        where the value at each index correspond to a tile.
        The mapping is done with the built-in function in
        Tile class. There is an array for each player.
        
    Parameters:
        player_nb: (int) Number of player in the game.
    
    """
    GRID_SIDE_SIZE = 49
    MAX_POSITION = GRID_SIDE_SIZE*GRID_SIDE_SIZE - 1
    
    def __init__(self,player_nb):
        self.grid = np.ones((Grid.GRID_SIDE_SIZE,Grid.GRID_SIDE_SIZE,player_nb))
        self.tile_to_value, self.value_to_tile = Tile.create_tiles_values_mappings()
        self.DEFAULT_VALUE = self.tile_to_value[(Tile.DEFAULT_COLOR,Tile.DEFAULT_SYMBOL)]
        self.grid = self.grid * self.DEFAULT_VALUE
        self.empty = True
    
    def position_coordinates(self,position):
        """ Retrieve the coordinate on the grid given the integer position. """
        return (position//Grid.GRID_SIDE_SIZE,position%Grid.GRID_SIDE_SIZE)
    
    def get_neighbours(self,x,y,player_id):
        """ Retrieve the neighbouring tiles on the grid. """
        neighbours = []
        if x%2 == 1: # Top of basis
            for i in [-1,1]:
                for j in [-1,1]:
                    neighbour_tile = self.grid[x+i,y+j,player_id]
                    neighbours.append(neighbour_tile)
        else: # Regular Tile
            for i,j in [(-2,0),(0,-2),(0,2),(2,0)]:
                neighbour_tile = self.grid[x+i,y+j,player_id]
                neighbours.append(neighbour_tile)
        return neighbours
    
    def check_basis(self,x,y,player_id,tile):
        """ Check if the tile can be placed on the relative basis. """
        neighbours = self.get_neighbours(x,y,player_id)
        if self.DEFAULT_VALUE in neighbours:
            raise Exception("The basis miss at least one tile.")
        basis_colors = [self.value_to_tile[0] for t in neighbours]
        if tile.color not in basis_colors:
            raise Exception(f"Tile color {tile.color} not in the basis {basis_colors}.")
        return True
    
    def is_move_valid(self,player_id,tile,position):
        """ Check if the given player can make the move. """
        if position < 0 or position > self.MAX_POSITION: # Outside the grid
            raise ValueError(f"Position {position} outside the grid.")
        if position % 2 == 1: # Between Tiles
            raise ValueError(f"Position {position} located between tiles.")
        pos_x, pos_y = self.position_coordinates(position)
        if self.grid[pos_x,pos_y,player_id] != self.DEFAULT_VALUE: # Tile unavailable
            raise ValueError(f"Position {position} already occupied by a tile.")
        if pos_x%2 == 1: # On top of basis
            return self.check_basis(pos_x,pos_y,player_id,tile)
        if pos_x%2 == 0 and not self.empty:
            neighbours = self.get_neighbours(pos_x,pos_y,player_id)
            neighbours.remove(self.DEFAULT_VALUE)
            if len(neighbours) == 0:
                raise ValueError(f"Position {position} has no neighbouring tile.")
        return True

