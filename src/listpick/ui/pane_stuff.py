import curses

features = {
    "position": "top",
    "height": 4,
}
def textbox(x:int, y:int, w:int, h:int, text:str):
    """ Draw a textbox in the region given. """
