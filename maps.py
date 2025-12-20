# Tower Climber Maps
# Legend:
#   ' ' = Empty space
#   '-' = Platform
#   'E' = Enemy
#   'O' = Obstacle
#   'H' = Ladder (vertical)
#   'P' = Player spawn point
#   'X' = Exit

# Each map is 20 characters wide to fit 800px screen (40px per tile)

TOWER_LEVEL_1 = [
    "                    ",
    "         X          ",
    "      ------        ",
    "                    ",
    "  E                 ",
    "  -----      -----  ",
    "                    ",
    "             E      ",
    "     -----  ------  ",
    "                    ",
    "                    ",
    "         OO         ",
    "       ------       ",
    "                    ",
    "                    ",
    "           ------   ",
    "  E                 ",
    "  -------           ",
    "                    ",
    "         OO         ",
    "       -------      ",
    "                    ",
    "                    ",
    "   ----     -----   ",
    "                    ",
    "                    ",
    "          -------   ",
    "                    ",
    "   OOO              ",
    "  ------            ",
    "                    ",
    "                    ",
    "        --------    ",
    "                    ",
    "                    ",
    "  -----             ",
    "                    ",
    "           OO       ",
    "       --------     ",
    "                    ",
    "         P          ",
    "--------------------",
]

# Alternative tower with more challenging layout
TOWER_LEVEL_2 = [
    # Top
    "                    ",
    "         X          ",
    "       -----        ",
    "                    ",
    "                    ",
    "  E           E     ",
    "  ---         ---   ",
    "                    ",
    "        OOO         ",
    "      --------      ",
    "                    ",
    "                    ",
    "   E          E     ",
    "   ---       ----   ",
    "                    ",
    # Middle
    "         O          ",
    "  ----      -----   ",
    "                    ",
    "                    ",
    "           E        ",
    "       --------     ",
    "                    ",
    "  E                 ",
    "  -----   OOO       ",
    "        -------     ",
    "                    ",
    "              E     ",
    "          ------    ",
    "                    ",
    "  OO                ",
    # Lower
    "  -----             ",
    "                    ",
    "           E        ",
    "         ------     ",
    "                    ",
    "    E               ",
    "    ----    OO      ",
    "          ------    ",
    "                    ",
    "                    ",
    "  E           E     ",
    "  ----      -----   ",
    "                    ",
    "         OOO        ",
    "      ---------     ",
    # Ground
    "                    ",
    "                    ",
    "         P          ",
    "                    ",
    "--------------------",
]

# Compact tower for quick testing
TOWER_TEST = [
    "                    ",
    "         X          ",
    "      ------        ",
    "         H          ",
    "  E      H          ",
    "  -----  H---  -----",
    "         H          ",
    "         H   E      ",
    "     ----H ------   ",
    "         H          ",
    "   OO    H          ",
    "  -----  H          ",
    "         H          ",
    "         P          ",
    "--------------------",
]

# All available maps
ALL_MAPS = {
    "level_1": TOWER_LEVEL_1,
    "level_2": TOWER_LEVEL_2,
    "test": TOWER_TEST,
}
