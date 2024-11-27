from enum import Enum

class Palette(Enum):
    """
    Represents the colour palette used by UI components and dialogs.

    This enum centralizes the colour palette for the application
    (excluding the window's background colour which is handled by the
    View class), making it easier to experiment with, reference,
    and modify the colour scheme, while maintaining consistency across
    the user interface.
    """
    MAIN_COLOUR = "background-color: hsl(37, 100%, 47%)"
    MAIN_HOVER = "background-color: hsl(37, 100%, 65%)"
    TEXT_COLOUR = "color: white"

class LabelStyle(Enum):
    """
    Represents the general styles applied to all labels/widgets inheriting from QLabel.

    This enum centralizes the styles for labels, ensuring consistency across 
    different components and dialogs that include labels in their layout.
    """
    STRUCTURE = f"""border-radius: 10px;
                       height: 10px; font-size: 20px;
                       {Palette.TEXT_COLOUR.value}"""

    DEFAULT_COLOUR = "background-color: hsl(60, 2%, 26%)"

    HOVER_COLOUR = "background-color: hsl(45, 3%, 29%)"

class Styles(Enum):
    """
    Represents the styles applied to specific UI components and dialogs.

    This enum centralizes the styles for UI components and dialogs, making it easier
    to reference, modify, and maintain consistent styling across the application.
    """
    EMPTY_LBL = f"{Palette.TEXT_COLOUR.value}; font-size: 30px; padding: 10px;"

    LBL_DEFAULT = f"""
                    QLabel{{
                        {LabelStyle.DEFAULT_COLOUR.value};
                        {LabelStyle.STRUCTURE.value};
                        border: 2px solid white;
                    }}
                    QLabel:hover{{
                        {LabelStyle.HOVER_COLOUR.value};
                    }}"""

    LBL_CLICKED = f"""
                    QLabel{{
                        {Palette.MAIN_COLOUR.value};
                        {LabelStyle.STRUCTURE.value};
                        border: 2px solid white;
                    }}"""

    FOCUSED_TAB = f"""QTabBar::tab::selected{{{Palette.MAIN_COLOUR.value};}}"""

    SIDEBAR_LBL = f"""background-color: hsl(60, 2%, 11%); {LabelStyle.STRUCTURE.value};
                      padding-left: 3px;
                   """

    TOOLBAR_BTN = f"""
                    QPushButton{{
                        {Palette.MAIN_COLOUR.value};
                        font-size: 20px;
                        }}
                    QPushButton:hover{{
                        {Palette.MAIN_HOVER.value};
                        }}"""
