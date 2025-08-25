from listpick.utils import keycodes
import os, tty, select, curses

def open_tty():
    """ Return a file descriptor for the tty that we are opening"""
    tty_fd = os.open('/dev/tty', os.O_RDONLY)
    tty.setraw(tty_fd)
    return tty_fd

def get_char(tty_fd, timeout: float = 0.2, secondary: bool = False) -> int:
    """ Get character from a tty_fd with a timeout. """
    rlist, _, _ = select.select([tty_fd], [], [], timeout)
    if rlist:
        # key = ord(tty_fd.read(1))
        key = ord(os.read(tty_fd, 1))
        if not secondary:
            if key == 27:
                key2 = get_char(tty_fd, timeout=0.01, secondary=True)
                key3 = get_char(tty_fd, timeout=0.01, secondary=True)
                key4 = get_char(tty_fd, timeout=0.01, secondary=True)
                key5 = get_char(tty_fd, timeout=0.01, secondary=True)
                key6 = get_char(tty_fd, timeout=0.01, secondary=True)

                keys = [key2, key3, key4, key5, key6]

                key_str = "".join([chr(k) for k in keys if k != -1])

                ## Arrow Keys
                if key2 == ord('O') and key3 == ord('B'):
                    key = curses.KEY_DOWN
                elif key2 == ord('O') and key3 == ord('A'):
                    key = curses.KEY_UP
                elif key2 == ord('O') and key3 == ord('D'):
                    key = curses.KEY_LEFT
                elif key2 == ord('O') and key3 == ord('C'):
                    key = curses.KEY_RIGHT

                ## Shift+ Tab
                elif key2 == ord('[') and key3 == ord('Z'):
                    key = 353

                ## Home, End, Pgup, Pgdn
                elif key2 == ord('O') and key3 == ord('F'):
                    key = curses.KEY_END
                elif key2 == ord('O') and key3 == ord('H'):
                    key = curses.KEY_HOME
                elif key2 == ord('[') and key3 == ord('6') and key4 == ord("~"):
                    key = curses.KEY_NPAGE
                elif key2 == ord('[') and key3 == ord('5') and key4 == ord("~"):
                    key = curses.KEY_PPAGE


                # Delete key
                elif key_str == "[3~":    ## Delete
                    key = curses.KEY_DC
                elif key_str == "[3;2~":                                            ## Shift+Delete
                    key = 383

                ## Function Keys
                elif key2 == ord('O') and key3 == ord('P'):
                    key = curses.KEY_F1
                elif key_str == "OQ":
                    key = curses.KEY_F2
                elif key_str == "OR":
                    key = curses.KEY_F3
                elif key_str == "OS":
                    key = curses.KEY_F4
                elif key_str == "[15~":
                    key = curses.KEY_F5
                elif key_str == "[17~":
                    key = curses.KEY_F6
                elif key_str == "[17~":
                    key = curses.KEY_F7
                elif key_str == "[19~":
                    key = curses.KEY_F8
                elif key_str == "[20~":
                    key = curses.KEY_F9
                elif key_str == "[21~":
                    key = curses.KEY_F10
                elif key_str == "[23~":
                    key = curses.KEY_F11
                elif key_str == "[24~":
                    key = curses.KEY_F12

                ## Alt+KEY
                elif key2 >= ord('a') and key2 <= ord('z') and key3 == -1:      ## Alt+[a-zA-Z]
                    key = keycodes.META_a + (key2 - ord('a'))
                elif key2 >= ord('A') and key2 <= ord('Z') and key3 == -1:      ## Alt+[a-zA-Z]
                    key = keycodes.META_A + (key2 - ord('A'))
                elif key2 == ord('0') and key3 == -1:                           ## Alt+0
                    key = keycodes.META_0
                elif key2 >= ord('1') and key2 <= ord('9') and key3 == -1:      ## Alt+1-9
                    key = keycodes.META_1 + (key2 - ord('1'))
                elif key2 == 127:                                               ## Alt+BS
                    key = keycodes.META_BS

                # If it is an unknown key with an escape sequence then return -1.
                elif key2 != -1:
                    key = -1
        

    else:
        key = -1
    return key
