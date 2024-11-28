from PySide6.QtWidgets import QWidget
from core.elements.element import ElemType


class GuiState:
    """
    Manages and tracks the current state of the GUI.

    This state machine ensures that transitions between states are only 
    performed if they are valid, helping to identify and prevent bugs during 
    state changes.

    Additionally, it maintains data required by the View and UI components 
    for their operations, ensuring consistency across the application.
    """
    def __init__(self, initial_view: ElemType, widget: QWidget):
        """
        Initializes the state machine with an initial view and widget
        representing the grid currently displayed in the GUI.

        Args:
            initial_view (ElemType): The type of the elements being displayed
                                     when the GUI is launched.
            widget (QWidget): The initial widget to be displayed in the GUI.
        """
        self.state = initial_view
        self.widget = widget
        self.env_pos = None
        self.available_states = {
                  ElemType.ENV: [ElemType.WEB],
                  ElemType.WEB: [ElemType.APP, ElemType.FILE, ElemType.ENV],
                  ElemType.APP: [ElemType.WEB, ElemType.FILE, ElemType.ENV],
                  ElemType.FILE: [ElemType.WEB, ElemType.APP, ElemType.ENV]
                }

    def transition_state(self, state: ElemType, widget: QWidget):
        """
        Transitions to a new state if the transition is valid.

        This method checks if the transition from the current state to the 
        provided state is allowed, and if so, updates the attributes representing
        the new state of the application.

        Args:
            state (ElemType): The type of the elemens to be displayed in the GUI.
            widget (QWidget): The widget responsible for arranging and displaying 
                              the elements of the new state.
        """
        if state in self.available_states[self.state]:
            self.state = state
            self.widget = widget
        else:
            raise ValueError(f"Cannot transition from {self.state} to {state}.")

    def update_current_env_pos(self, env_pos: int):
        """
        Updates the stored position of the currently clicked environment.

        This method updates the internal state to reflect the new position 
        of the environment that was clicked.

        Args:
            env_pos (int): The position of the clicked environment.
        """
        self.env_pos = env_pos

    def get_current_grid(self):
        """
        Retrieves the current grid widget being displayed in the GUI.

        This method returns the widget that represents the current state of 
        the grid, allowing other components or methods to interact with it.

        Returns:
            QWidget: The widget that represents the current grid.
        """
        return self.widget

    def get_current_env_pos(self):
        """
        Retrieves the position of the currently clicked environment.

        This method returns the stored position of the environment that was
        last clicked, which is used to interact with it.

        Returns:
            int | None: The position of the currently clicked environment,
                        or None if no position is set.
        """
        return self.env_pos
