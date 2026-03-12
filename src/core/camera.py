class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        
    def update(self, target_x, target_y):
        # Center camera on target
        self.x = target_x - self.width / 2
        self.y = target_y - self.height / 2
        
    def apply(self, x, y):
        # Convert world coordinates to screen coordinates
        return (x - self.x, y - self.y)
