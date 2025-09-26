from settings import *

app.use_app('PyQt6')

class Canvas(app.Canvas):
    def __init__(self):
        super().__init__(title='canvasss', size=(WINDOW_WIDTH, WINDOW_HEIGHT), 
                         resizable=True, show=True)
        
if __name__ == '__main__':
    c = Canvas()
    app.run()


