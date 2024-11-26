from core.elements.element import ElemType


class GuiStateMachine:
    def __init__(self, widget):
        self.state = ElemType.ENV
        self.widget = widget
        self.available_states = {
                  ElemType.ENV: [ElemType.WEB],
                  ElemType.WEB: [ElemType.APP, ElemType.FILE, ElemType.ENV],
                  ElemType.APP: [ElemType.WEB, ElemType.FILE, ElemType.ENV],
                  ElemType.FILE: [ElemType.WEB, ElemType.APP, ElemType.ENV]
                }

    def transition_state(self, state, widget):
        if state in self.available_states[self.state]:
            self.state = state
            self.widget = widget
        else:
            raise ValueError(f"Cannot transition from {self.state} to {state}.")

    def get_current_grid(self):
        return self.widget
