"""Selection cursors in xpm format
"""
from enum import Enum
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtCore import Qt

from typing import Dict, Tuple


class DrawingMode(Enum):
    """Enum for for drawin modes

    NoDraw: no drawing active
    New: Drawing overwrites existing selection
    Add: Drawing add to existing selection
    Sub: Drawing removes from existing selection
    """

    NoDraw, New, Add, Sub = range(4)


class DrawingShape(Enum):
    """Enum for drawing shapes

        NoShape:   No drawing active
        Ellipse:   Draw ellipse - click and drag diagonal
        Lasso:     Draw outline - click and draw line
        Polygon:   Draw n-sides irregular polygon - series of clicks
        Rectangle: Draw rectangle, click and draw diagonal
    Args:
        Enum ([type]): [description]
    """

    NoShape, Ellipse, Lasso, Polygon, Rectangle = range(5)


# None signals transparent
cursors_xpm = {
    "e": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ############  ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!!#  ",
        "  ##!##  ##!!!##  ##!!!!!!!!##  ",
        "   ####   ##!!##  ##!!########  ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!#######   ",
        "                  ##!!!#######  ",
        "                  ##!!!!!!!!##  ",
        "                  ##!!!#######  ",
        "                  ##!!#######   ",
        "                  ##!!#         ",
        "                  ##!!########  ",
        "                  ##!!########  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "ctrl+e": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ############  ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!!#  ",
        "  ##!##  ##!!!##  ##!!!!!!!!##  ",
        "   ####   ##!!##  ##!!########  ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!#######   ",
        "                  ##!!!#######  ",
        "            ##### ##!!!!!!!!##  ",
        "          ##########!!!#######  ",
        "          ##!!!!!###!!#######   ",
        "          ##!!!!!###!!#         ",
        "          ##########!!########  ",
        "            ##### ##!!########  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "E": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ############  ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!!#  ",
        "  ##!##  ##!!!##  ##!!!!!!!!##  ",
        "   ####   ##!!##  ##!!########  ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!#######   ",
        "            ##### ##!!!#######  ",
        "           ##!!## ##!!!!!!!!##  ",
        "         ####!!#####!!!#######  ",
        "         ##!!!!!!###!!#######   ",
        "         ##!!!!!!###!!#         ",
        "         ####!!#####!!########  ",
        "           ##!!## ##!!########  ",
        "            ##### ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "l": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ######        ",
        "  #!!## ##!!!#    ######        ",
        "  ##!## ##!!!##   ##!!##        ",
        "  ##!##  ##!!!##  ##!!##        ",
        "   ####   ##!!##  ##!!##        ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!##        ",
        "                  ##!!##        ",
        "                  ##!!##        ",
        "                  ##!!##        ",
        "                  ##!!##        ",
        "                  ##!!##        ",
        "                  ##!!########  ",
        "                  ##!!########  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "ctrl+l": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ######        ",
        "  #!!## ##!!!#    ######        ",
        "  ##!## ##!!!##   ##!!##        ",
        "  ##!##  ##!!!##  ##!!##        ",
        "   ####   ##!!##  ##!!##        ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!##        ",
        "                  ##!!##        ",
        "            ##### ##!!##        ",
        "          ##########!!##        ",
        "          ##!!!!!###!!##        ",
        "          ##!!!!!###!!##        ",
        "          ##########!!########  ",
        "            ##### ##!!########  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "L": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ######        ",
        "  #!!## ##!!!#    ######        ",
        "  ##!## ##!!!##   ##!!##        ",
        "  ##!##  ##!!!##  ##!!##        ",
        "   ####   ##!!##  ##!!##        ",
        "    ###    ####   ##!!##        ",
        "     ##     ##    ##!!##        ",
        "            ##### ##!!##        ",
        "           ##!!## ##!!##        ",
        "         ####!!#####!!##        ",
        "         ##!!!!!!###!!##        ",
        "         ##!!!!!!###!!##        ",
        "         ####!!#####!!########  ",
        "           ##!!## ##!!########  ",
        "            ##### ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ############  ",
        "                   ###########  ",
        "                                ",
        "                                ",
    ],
    "p": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "                  ##!!#####!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!##  ",
        "                  ##!!########  ",
        "                  ##!!#######   ",
        "                  ##!!#         ",
        "                  ##!!#         ",
        "                  ##!!#         ",
        "                  ##!!#         ",
        "                  #####         ",
        "                   ####         ",
        "                                ",
        "                                ",
    ],
    "ctrl+p": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "                  ##!!#####!!#  ",
        "            ##### ##!!!!!!!!!#  ",
        "          ##########!!!!!!!!##  ",
        "          ##!!!!!###!!########  ",
        "          ##!!!!!###!!#######   ",
        "          ##########!!#         ",
        "            ##### ##!!#         ",
        "                  ##!!#         ",
        "                  ##!!#         ",
        "                  #####         ",
        "                   ####         ",
        "                                ",
        "                                ",
    ],
    "P": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "            ##### ##!!#####!!#  ",
        "           ##!!## ##!!!!!!!!!#  ",
        "         ####!!#####!!!!!!!!##  ",
        "         ##!!!!!!###!!########  ",
        "         ##!!!!!!###!!#######   ",
        "         ####!!#####!!#         ",
        "           ##!!## ##!!#         ",
        "            ##### ##!!#         ",
        "                  ##!!#         ",
        "                  #####         ",
        "                   ####         ",
        "                                ",
        "                                ",
    ],
    "r": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "                  ##!!#####!!#  ",
        "                  ##!!!!!!!!!#  ",
        "                  ##!!!!!!!!##  ",
        "                  ##!!###!!###  ",
        "                  ##!!###!!!#   ",
        "                  ##!!#  #!!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  #####  #####  ",
        "                   ####   ####  ",
        "                                ",
        "                                ",
    ],
    "ctrl+r": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "                  ##!!#####!!#  ",
        "            ##### ##!!!!!!!!!#  ",
        "          ##########!!!!!!!!##  ",
        "          ##!!!!!###!!###!!###  ",
        "          ##!!!!!###!!###!!!#   ",
        "          ##########!!#  #!!!#  ",
        "            ##### ##!!#  ##!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  #####  #####  ",
        "                   ####   ####  ",
        "                                ",
        "                                ",
    ],
    "R": [
        "32 32 3 1",
        "  c None",
        "! c #FFFFFF",
        "# c #101010",
        "                                ",
        "                                ",
        "   #########                    ",
        "  ###########                   ",
        "  #!!!!!!!!!##                  ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!!!!!!##                 ",
        "  #!!!!!########                ",
        "  #!!!!!!##                     ",
        "  #!!!!!!##                     ",
        "  #!!!#!!!##                    ",
        "  #!!###!!!##                   ",
        "  #!!####!!!##    ###########   ",
        "  #!!## ##!!!#    ############  ",
        "  ##!## ##!!!##   ##!!!!!!!!##  ",
        "  ##!##  ##!!!##  ##!!!!!!!!!#  ",
        "   ####   ##!!##  ##!!#####!!#  ",
        "    ###    ####   ##!!#   #!!#  ",
        "     ##     ##    ##!!#   #!!#  ",
        "            ##### ##!!#####!!#  ",
        "           ##!!## ##!!!!!!!!!#  ",
        "         ####!!#####!!!!!!!!##  ",
        "         ##!!!!!!###!!###!!###  ",
        "         ##!!!!!!###!!###!!!#   ",
        "         ####!!#####!!#  #!!!#  ",
        "           ##!!## ##!!#  ##!!#  ",
        "            ##### ##!!#  ##!!#  ",
        "                  ##!!#  ##!!#  ",
        "                  #####  #####  ",
        "                   ####   ####  ",
        "                                ",
        "                                ",
    ],
}


class DrawingCursors:
    """load and select cursors based on the key press"""

    key_to_drawstate = {
        "e": (DrawingMode.New, DrawingShape.Ellipse),
        "E": (DrawingMode.Add, DrawingShape.Ellipse),
        "ctrl+e": (DrawingMode.Sub, DrawingShape.Ellipse),
        "l": (DrawingMode.New, DrawingShape.Lasso),
        "L": (DrawingMode.Add, DrawingShape.Lasso),
        "ctrl+l": (DrawingMode.Sub, DrawingShape.Lasso),
        "p": (DrawingMode.New, DrawingShape.Polygon),
        "P": [DrawingMode.Add, DrawingShape.Polygon],
        "ctrl+p": (DrawingMode.Sub, DrawingShape.Polygon),
        "r": (DrawingMode.New, DrawingShape.Rectangle),
        "R": (DrawingMode.Add, DrawingShape.Rectangle),
        "ctrl+r": (DrawingMode.Sub, DrawingShape.Rectangle),
    }

    cursors_loaded = False
    cursors: Dict[Tuple[DrawingMode, DrawingShape], QCursor] = {}

    @classmethod
    def __load_cursors(cls):
        cursors = {(DrawingMode.NoDraw, DrawingShape.NoShape): QCursor(Qt.ArrowCursor)}
        for k in cls.key_to_drawstate:
            px = QPixmap(cursors_xpm[k])
            mask = px.createHeuristicMask()
            px.setMask(mask)
            cursor = QCursor(px, 0, 0)  # hot point is always top left
            (mode, shape) = cls.key_to_drawstate[k]
            cursors[(mode, shape)] = cursor
        return cursors

    @classmethod
    def get_drawstate(cls, key):
        """Get the drawstate enum pair based on the key press

        Args:
            key (string): key text (can be combined - e.g. ctrl+r)

        Returns:
            [tuple[DrawingMode, DrawingShape]]: the mode and shape triggered by the key
        """
        return cls.key_to_drawstate.get(key, (DrawingMode.NoDraw, DrawingShape.NoShape))

    @classmethod
    def init_cursors(cls):
        """Load the xpm cursors into memory converting to and array of QCursor"""
        if not cls.cursors_loaded:
            cls.cursors = cls.__load_cursors()
            cls.cursors_loaded = True
