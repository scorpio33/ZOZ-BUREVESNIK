class MenuManager:
    def __init__(self):
        self.current_menu = None
        self.menu_stack = []
        
    def get_current_menu(self):
        return self.current_menu
        
    def push_menu(self, menu):
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu
        
    def pop_menu(self):
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        return self.current_menu
