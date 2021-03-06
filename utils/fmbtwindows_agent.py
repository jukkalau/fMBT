# fMBT, free Model Based Testing tool
# Copyright (c) 2014, Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU Lesser General Public License,
# version 2.1, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.

import ctypes
import ctypes.wintypes
import glob
import os
import Queue
import string
import struct
import subprocess
import sys
import thread
import time
import zlib

try:
    import wmi # try to import wmi, requires that pywin32 and wmi packages
               # are installed in DUT
except:
    pass

_mouse_input_area = (1920, 1080)
_HTTPServerProcess = None

INPUT_MOUSE                 = 0
INPUT_KEYBOARD              = 1
INPUT_HARDWARE              = 2

# For touchMask
TOUCH_MASK_NONE             = 0x00000000
TOUCH_MASK_CONTACTAREA      = 0x00000001
TOUCH_MASK_ORIENTATION      = 0x00000002
TOUCH_MASK_PRESSURE         = 0x00000004
TOUCH_MASK_ALL              = 0x00000007

# For touchFlag
TOUCH_FLAG_NONE             = 0x00000000

# For pointerType
PT_POINTER                  = 0x00000001
PT_TOUCH                    = 0x00000002
PT_PEN                      = 0x00000003
PT_MOUSE                    = 0x00000004

# For pointerFlags
POINTER_FLAG_NONE           = 0x00000000
POINTER_FLAG_NEW            = 0x00000001
POINTER_FLAG_INRANGE        = 0x00000002
POINTER_FLAG_INCONTACT      = 0x00000004
POINTER_FLAG_FIRSTBUTTON    = 0x00000010
POINTER_FLAG_SECONDBUTTON   = 0x00000020
POINTER_FLAG_THIRDBUTTON    = 0x00000040
POINTER_FLAG_FOURTHBUTTON   = 0x00000080
POINTER_FLAG_FIFTHBUTTON    = 0x00000100
POINTER_FLAG_PRIMARY        = 0x00002000
POINTER_FLAG_CONFIDENCE     = 0x00004000
POINTER_FLAG_CANCELED       = 0x00008000
POINTER_FLAG_DOWN           = 0x00010000
POINTER_FLAG_UPDATE         = 0x00020000
POINTER_FLAG_UP             = 0x00040000
POINTER_FLAG_WHEEL          = 0x00080000
POINTER_FLAG_HWHEEL         = 0x00100000
POINTER_FLAG_CAPTURECHANGED = 0x00200000

WHEEL_DELTA                 = 120
XBUTTON1                    = 0x0001
XBUTTON2                    = 0x0002
MOUSEEVENTF_ABSOLUTE        = 0x8000
MOUSEEVENTF_HWHEEL          = 0x01000
MOUSEEVENTF_MOVE            = 0x0001
MOUSEEVENTF_MOVE_NOCOALESCE = 0x2000
MOUSEEVENTF_LEFTDOWN        = 0x0002
MOUSEEVENTF_LEFTUP          = 0x0004
MOUSEEVENTF_RIGHTDOWN       = 0x0008
MOUSEEVENTF_RIGHTUP         = 0x0010
MOUSEEVENTF_MIDDLEDOWN      = 0x0020
MOUSEEVENTF_MIDDLEUP        = 0x0040
MOUSEEVENTF_VIRTUALDESK     = 0x4000
MOUSEEVENTF_WHEEL           = 0x0800
MOUSEEVENTF_XDOWN           = 0x0080
MOUSEEVENTF_XUP             = 0x0100

SM_XVIRTUALSCREEN           = 76
SM_YVIRTUALSCREEN           = 77
SM_CXVIRTUALSCREEN          = 78
SM_CYVIRTUALSCREEN          = 79

VK_LBUTTON = 0x01               # Left mouse button
VK_RBUTTON = 0x02               # Right mouse button
VK_CANCEL = 0x03                # Control-break processing
VK_MBUTTON = 0x04               # Middle mouse button (three-button mouse)
VK_XBUTTON1 = 0x05              # X1 mouse button
VK_XBUTTON2 = 0x06              # X2 mouse button
VK_BACK = 0x08                  # BACKSPACE key
VK_TAB = 0x09                   # TAB key
VK_CLEAR = 0x0C                 # CLEAR key
VK_RETURN = 0x0D                # ENTER key
VK_SHIFT = 0x10                 # SHIFT key
VK_CONTROL = 0x11               # CTRL key
VK_MENU = 0x12                  # ALT key
VK_PAUSE = 0x13                 # PAUSE key
VK_CAPITAL = 0x14               # CAPS LOCK key
VK_KANA = 0x15                  # IME Kana mode
VK_HANGUL = 0x15                # IME Hangul mode
VK_JUNJA = 0x17                 # IME Junja mode
VK_FINAL = 0x18                 # IME final mode
VK_HANJA = 0x19                 # IME Hanja mode
VK_KANJI = 0x19                 # IME Kanji mode
VK_ESCAPE = 0x1B                # ESC key
VK_CONVERT = 0x1C               # IME convert
VK_NONCONVERT = 0x1D            # IME nonconvert
VK_ACCEPT = 0x1E                # IME accept
VK_MODECHANGE = 0x1F            # IME mode change request
VK_SPACE = 0x20                 # SPACEBAR
VK_PRIOR = 0x21                 # PAGE UP key
VK_NEXT = 0x22                  # PAGE DOWN key
VK_END = 0x23                   # END key
VK_HOME = 0x24                  # HOME key
VK_LEFT = 0x25                  # LEFT ARROW key
VK_UP = 0x26                    # UP ARROW key
VK_RIGHT = 0x27                 # RIGHT ARROW key
VK_DOWN = 0x28                  # DOWN ARROW key
VK_SELECT = 0x29                # SELECT key
VK_PRINT = 0x2A                 # PRINT key
VK_EXECUTE = 0x2B               # EXECUTE key
VK_SNAPSHOT = 0x2C              # PRINT SCREEN key
VK_INSERT = 0x2D                # INS key
VK_DELETE = 0x2E                # DEL key
VK_HELP = 0x2F                  # HELP key
VK_LWIN = 0x5B                  # Left Windows key (Natural keyboard)
VK_RWIN = 0x5C                  # Right Windows key (Natural keyboard)
VK_APPS = 0x5D                  # Applications key (Natural keyboard)
VK_SLEEP = 0x5F                 # Computer Sleep key
VK_NUMPAD0 = 0x60               # Numeric keypad 0 key
VK_NUMPAD1 = 0x61               # Numeric keypad 1 key
VK_NUMPAD2 = 0x62               # Numeric keypad 2 key
VK_NUMPAD3 = 0x63               # Numeric keypad 3 key
VK_NUMPAD4 = 0x64               # Numeric keypad 4 key
VK_NUMPAD5 = 0x65               # Numeric keypad 5 key
VK_NUMPAD6 = 0x66               # Numeric keypad 6 key
VK_NUMPAD7 = 0x67               # Numeric keypad 7 key
VK_NUMPAD8 = 0x68               # Numeric keypad 8 key
VK_NUMPAD9 = 0x69               # Numeric keypad 9 key
VK_MULTIPLY = 0x6A              # Multiply key
VK_ADD = 0x6B                   # Add key
VK_SEPARATOR = 0x6C             # Separator key
VK_SUBTRACT = 0x6D              # Subtract key
VK_DECIMAL = 0x6E               # Decimal key
VK_DIVIDE = 0x6F                # Divide key
VK_F1 = 0x70                    # F1 key
VK_F2 = 0x71                    # F2 key
VK_F3 = 0x72                    # F3 key
VK_F4 = 0x73                    # F4 key
VK_F5 = 0x74                    # F5 key
VK_F6 = 0x75                    # F6 key
VK_F7 = 0x76                    # F7 key
VK_F8 = 0x77                    # F8 key
VK_F9 = 0x78                    # F9 key
VK_F10 = 0x79                   # F10 key
VK_F11 = 0x7A                   # F11 key
VK_F12 = 0x7B                   # F12 key
VK_F13 = 0x7C                   # F13 key
VK_F14 = 0x7D                   # F14 key
VK_F15 = 0x7E                   # F15 key
VK_F16 = 0x7F                   # F16 key
VK_F17 = 0x80                   # F17 key
VK_F18 = 0x81                   # F18 key
VK_F19 = 0x82                   # F19 key
VK_F20 = 0x83                   # F20 key
VK_F21 = 0x84                   # F21 key
VK_F22 = 0x85                   # F22 key
VK_F23 = 0x86                   # F23 key
VK_F24 = 0x87                   # F24 key
VK_NUMLOCK = 0x90               # NUM LOCK key
VK_SCROLL = 0x91                # SCROLL LOCK key
VK_LSHIFT = 0xA0                # Left SHIFT key
VK_RSHIFT = 0xA1                # Right SHIFT key
VK_LCONTROL = 0xA2              # Left CONTROL key
VK_RCONTROL = 0xA3              # Right CONTROL key
VK_LMENU = 0xA4                 # Left MENU key
VK_RMENU = 0xA5                 # Right MENU key
VK_BROWSER_BACK = 0xA6          # Browser Back key
VK_BROWSER_FORWARD = 0xA7       # Browser Forward key
VK_BROWSER_REFRESH = 0xA8       # Browser Refresh key
VK_BROWSER_STOP = 0xA9          # Browser Stop key
VK_BROWSER_SEARCH = 0xAA        # Browser Search key
VK_BROWSER_FAVORITES = 0xAB     # Browser Favorites key
VK_BROWSER_HOME = 0xAC          # Browser Start and Home key
VK_VOLUME_MUTE = 0xAD           # Volume Mute key
VK_VOLUME_DOWN = 0xAE           # Volume Down key
VK_VOLUME_UP = 0xAF             # Volume Up key
VK_MEDIA_NEXT_TRACK = 0xB0      # Next Track key
VK_MEDIA_PREV_TRACK = 0xB1      # Previous Track key
VK_MEDIA_STOP = 0xB2            # Stop Media key
VK_MEDIA_PLAY_PAUSE = 0xB3      # Play/Pause Media key
VK_LAUNCH_MAIL = 0xB4           # Start Mail key
VK_LAUNCH_MEDIA_SELECT = 0xB5   # Select Media key
VK_LAUNCH_APP1 = 0xB6           # Start Application 1 key
VK_LAUNCH_APP2 = 0xB7           # Start Application 2 key
VK_OEM_1 = 0xBA                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the ';:' key
VK_OEM_PLUS = 0xBB              # For any country/region, the '+' key
VK_OEM_COMMA = 0xBC             # For any country/region, the ',' key
VK_OEM_MINUS = 0xBD             # For any country/region, the '-' key
VK_OEM_PERIOD = 0xBE            # For any country/region, the '.' key
VK_OEM_2 = 0xBF                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the '/?' key
VK_OEM_3 = 0xC0                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the '`~' key
VK_OEM_4 = 0xDB                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the '[{' key
VK_OEM_5 = 0xDC                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the '\|' key
VK_OEM_6 = 0xDD                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the ']}' key
VK_OEM_7 = 0xDE                 # Used for miscellaneous characters; it can vary by keyboard.
                                # For the US standard keyboard, the 'single-quote/double-quote' key
VK_OEM_8 = 0xDF                 # Used for miscellaneous characters; it can vary by keyboard.
VK_OEM_102 = 0xE2               # Either the angle bracket key or the backslash key on the RT 102-key keyboard
VK_PROCESSKEY = 0xE5            # IME PROCESS key
VK_PACKET = 0xE7                # Used to pass Unicode characters as if they were keystrokes. The VK_PACKET key is the low word of a 32-bit Virtual Key value used for non-keyboard input methods. For more information, see Remark in KEYBDINPUT, SendInput, WM_KEYDOWN, and WM_KEYUP
VK_ATTN = 0xF6                  # Attn key
VK_CRSEL = 0xF7                 # CrSel key
VK_EXSEL = 0xF8                 # ExSel key
VK_EREOF = 0xF9                 # Erase EOF key
VK_PLAY = 0xFA                  # Play key
VK_ZOOM = 0xFB                  # Zoom key
VK_PA1 = 0xFD                   # PA1 key
VK_OEM_CLEAR = 0xFE             # Clear key

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004

KEY_0 = 0x30
KEY_1 = 0x31
KEY_2 = 0x32
KEY_3 = 0x33
KEY_4 = 0x34
KEY_5 = 0x35
KEY_6 = 0x36
KEY_7 = 0x37
KEY_8 = 0x38
KEY_9 = 0x39
KEY_A = 0x41
KEY_B = 0x42
KEY_C = 0x43
KEY_D = 0x44
KEY_E = 0x45
KEY_F = 0x46
KEY_G = 0x47
KEY_H = 0x48
KEY_I = 0x49
KEY_J = 0x4A
KEY_K = 0x4B
KEY_L = 0x4C
KEY_M = 0x4D
KEY_N = 0x4E
KEY_O = 0x4F
KEY_P = 0x50
KEY_Q = 0x51
KEY_R = 0x52
KEY_S = 0x53
KEY_T = 0x54
KEY_U = 0x55
KEY_V = 0x56
KEY_W = 0x57
KEY_X = 0x58
KEY_Y = 0x59
KEY_Z = 0x5A

LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(DWORD)
WORD = ctypes.c_ushort

WM_GETTEXT = 0x000d

# Structs for mouse and keyboard input

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', LONG),
                ('dy', LONG),
                ('mouseData', DWORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', WORD),
                ('wScan', WORD),
                ('dwFlags', DWORD),
                ('time', DWORD),
                ('dwExtraInfo', ULONG_PTR))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', DWORD),
                ('wParamL', WORD),
                ('wParamH', WORD))

class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (('type', DWORD),
                ('union', _INPUTunion))

# Structs for touch input

class POINTER_INFO(ctypes.Structure):
    _fields_ = [("pointerType", ctypes.c_uint32),
              ("pointerId", ctypes.c_uint32),
              ("frameId", ctypes.c_uint32),
              ("pointerFlags", ctypes.c_int),
              ("sourceDevice", ctypes.wintypes.HANDLE),
              ("hwndTarget", ctypes.wintypes.HWND),
              ("ptPixelLocation", ctypes.wintypes.POINT),
              ("ptHimetricLocation", ctypes.wintypes.POINT),
              ("ptPixelLocationRaw", ctypes.wintypes.POINT),
              ("ptHimetricLocationRaw", ctypes.wintypes.POINT),
              ("dwTime", DWORD),
              ("historyCount", ctypes.c_uint32),
              ("inputData", ctypes.c_int32),
              ("dwKeyStates", DWORD),
              ("PerformanceCount", ctypes.c_uint64),
              ("ButtonChangeType", ctypes.c_int)
              ]


class POINTER_TOUCH_INFO(ctypes.Structure):
    _fields_ = [("pointerInfo", POINTER_INFO),
              ("touchFlags", ctypes.c_int),
              ("touchMask", ctypes.c_int),
              ("rcContact", ctypes.wintypes.RECT),
              ("rcContactRaw", ctypes.wintypes.RECT),
              ("orientation", ctypes.c_uint32),
              ("pressure", ctypes.c_uint32)]

# Initialize Pointer and Touch info

pointerInfo = POINTER_INFO(pointerType=PT_TOUCH,
                         pointerId=0,
                         ptPixelLocation=ctypes.wintypes.POINT(90,54))

touchInfo = POINTER_TOUCH_INFO(pointerInfo=pointerInfo,
                             touchFlags=TOUCH_FLAG_NONE,
                             touchMask=TOUCH_MASK_ALL,
                             rcContact=ctypes.wintypes.RECT(pointerInfo.ptPixelLocation.x-5,
                                  pointerInfo.ptPixelLocation.y-5,
                                  pointerInfo.ptPixelLocation.x+5,
                                  pointerInfo.ptPixelLocation.y+5),
                             orientation=90,
                             pressure=32000)

if not "touchInfoLock" in globals():
    touchInfoLock = thread.allocate_lock()

def setTouchCoords(touchInfo, x, y, fingerRadius=5):
    touchInfo.pointerInfo.ptPixelLocation.x = x
    touchInfo.pointerInfo.ptPixelLocation.y = y

    touchInfo.rcContact.left = x - fingerRadius
    touchInfo.rcContact.right = x + fingerRadius
    touchInfo.rcContact.top = y - fingerRadius
    touchInfo.rcContact.bottom = y + fingerRadius

def _sendTouch(pointerFlags, errorWhen="doTouch"):
    touchInfo.pointerInfo.pointerFlags = pointerFlags
    try:
        success = ctypes.windll.user32.InjectTouchInput(1, ctypes.byref(touchInfo))
    except AttributeError:
        raise NotImplementedError("this windows version does not support touch injection")
    if (success == 0):
        print "%s error: %s" % (errorWhen, ctypes.FormatError())
        return False
    else:
        return True

def _touchHold():
    # Keep updating previous touchDown or touchMove coordinates
    # to avoid InjectTouchInput timeout
    _touchUpdateInterval = 0.25  # seconds
    while True:
        time.sleep(_touchUpdateInterval)
        touchInfoLock.acquire()
        try:
            if not (touchInfo.pointerInfo.pointerFlags & POINTER_FLAG_INCONTACT):
                print "touch: no more contact"
                break

            if not _sendTouch(POINTER_FLAG_UPDATE  |
                              POINTER_FLAG_INRANGE |
                              POINTER_FLAG_INCONTACT, "_touchHold"):
                break

        finally:
            touchInfoLock.release()

def touchDown(x, y, fingerRadius=5):
    touchInfoLock.acquire()
    try:
        setTouchCoords(touchInfo, x, y, fingerRadius)
        ok = _sendTouch(POINTER_FLAG_DOWN    |
                        POINTER_FLAG_INRANGE |
                        POINTER_FLAG_INCONTACT, "touchDown")
        if ok:
            thread.start_new_thread(_touchHold, ()) # update until raised
        return ok
    finally:
        touchInfoLock.release()

def touchMove(x, y, fingerRadius=5):
    touchInfoLock.acquire()
    try:
        setTouchCoords(touchInfo, x, y, fingerRadius)
        return _sendTouch(POINTER_FLAG_UPDATE  |
                          POINTER_FLAG_INRANGE |
                          POINTER_FLAG_INCONTACT, "touchMove")
    finally:
        touchInfoLock.release()

def touchUp(x, y, fingerRadius=5):
    touchInfoLock.acquire()
    try:
        setTouchCoords(touchInfo, x, y, fingerRadius)
        moveOk = _sendTouch(POINTER_FLAG_UPDATE  |
                            POINTER_FLAG_INRANGE |
                            POINTER_FLAG_INCONTACT,
                            "touchUp move to final location")
        return _sendTouch(POINTER_FLAG_UP, "touchUp") and moveOk
    finally:
        touchInfoLock.release()

def sendInput(*inputs):
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)

def Input(structure):
    if isinstance(structure, MOUSEINPUT):
        return INPUT(INPUT_MOUSE, _INPUTunion(mi=structure))
    if isinstance(structure, KEYBDINPUT):
        return INPUT(INPUT_KEYBOARD, _INPUTunion(ki=structure))
    if isinstance(structure, HARDWAREINPUT):
        return INPUT(INPUT_HARDWARE, _INPUTunion(hi=structure))
    raise TypeError('Cannot create INPUT structure!')


def MouseInput(flags, x, y, data):
    return MOUSEINPUT(x, y, data, flags, 0, None)


def KeybdInput(code, flags):
    return KEYBDINPUT(code, code, flags, 0, None)

def HardwareInput(message, parameter):
    return HARDWAREINPUT(message & 0xFFFFFFFF,
                         parameter & 0xFFFF,
                         parameter >> 16 & 0xFFFF)

def Mouse(flags, x=0, y=0, data=0):
    return Input(MouseInput(flags, x, y, data))

def Keyboard(code, flags=0):
    return Input(KeybdInput(code, flags))

def Hardware(message, parameter=0):
    return Input(HardwareInput(message, parameter))

################################################################################

UPPER = frozenset('~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?')
LOWER = frozenset("`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./")
ORDER = string.ascii_letters + string.digits + ' \b\r\t'
ALTER = dict(zip('!@#$%^&*()', '1234567890'))
OTHER = {'`': VK_OEM_3,
         '~': VK_OEM_3,
         '-': VK_OEM_MINUS,
         '_': VK_OEM_MINUS,
         '=': VK_OEM_PLUS,
         '+': VK_OEM_PLUS,
         '[': VK_OEM_4,
         '{': VK_OEM_4,
         ']': VK_OEM_6,
         '}': VK_OEM_6,
         '\\': VK_OEM_5,
         '|': VK_OEM_5,
         ';': VK_OEM_1,
         ':': VK_OEM_1,
         "'": VK_OEM_7,
         '"': VK_OEM_7,
         ',': VK_OEM_COMMA,
         '<': VK_OEM_COMMA,
         '.': VK_OEM_PERIOD,
         '>': VK_OEM_PERIOD,
         '/': VK_OEM_2,
         '?': VK_OEM_2}

def pressKey(keyName):
    keyCode = keyNameToKeyCode(keyName)
    event = Keyboard(keyCode, 0)
    return sendInput(event)

def releaseKey(keyName):
    keyCode = keyNameToKeyCode(keyName)
    event = Keyboard(keyCode, KEYEVENTF_KEYUP)
    return sendInput(event)

def keyboardStream(string):
    shiftPressed = False
    for character in string.replace('\r\n', '\r').replace('\n', '\r'):
        if shiftPressed and character in LOWER or not shiftPressed and character in UPPER:
            yield Keyboard(VK_SHIFT, shiftPressed and KEYEVENTF_KEYUP)
            shiftPressed = not shiftPressed
        character = ALTER.get(character, character)
        if character in ORDER:
            code = ord(character.upper())
        elif character in OTHER:
            code = OTHER[character]
        else:
            continue
            raise ValueError('String is not understood!')
        yield Keyboard(code)
        yield Keyboard(code, KEYEVENTF_KEYUP)
    if shiftPressed:
        yield Keyboard(VK_SHIFT, KEYEVENTF_KEYUP)

def screenshotZYBGR(screenshotSize=(None, None)):
    "Return width, height and zlib-compressed pixel data"
    # Size of both queues is 1. Who manages to put a request in will
    # get the response with requested resolution.
    _g_screenshotRequestQueue.put(screenshotSize)
    return _g_screenshotResponseQueue.get()

def sendType(text):
    for event in keyboardStream(text):
        sendInput(event)
        time.sleep(0.05)
    return True

def keyNameToKeyCode(keyName):
    if isinstance(keyName, int):
        return keyName
    elif isinstance(keyName, str):
        if len(keyName) == 1:
            return ord(keyName.upper())
        elif keyName.startswith("VK_") or keyName.startswith("KEY_") and keyName in globals():
            return globals()[keyName]
        elif ("VK_" + keyName) in globals():
            return globals()["VK_" + keyName]
        elif ("KEY_" + keyName) in globals():
            return globals()["KEY_" + keyName]
        else:
            raise ValueError('invalid key: "%s"' % (keyName,))
    else:
        raise TypeError('invalid key type: %s (key name: %s)' % (type(keyName), keyName))

def sendKey(keyName, modifiers):
    """
    keyName is a name (string) or a code (integer)
    modifiers is a list of keyNames.

    Examples:
      pressKey("s", modifiers=["VK_LWIN"])
      pressKey("KEY_A", modifiers=["VK_LSHIFT"])
    """
    sendKeyDown(keyName, modifiers)
    time.sleep(0.1)
    sendKeyUp(keyName, modifiers)

def sendKeyDown(keyName, modifiers):
    for m in modifiers:
        pressKey(m)
    pressKey(keyName)
    return True

def sendKeyUp(keyName, modifiers):
    releaseKey(keyName)
    for m in modifiers:
        releaseKey(m)
    return True

def sendClick(x, y, button=1):
    print "sendClick", x, y
    sendMouseMove(x, y, button)
    sendMouseDown(button)
    sendMouseUp(button)
    return True

def sendTouchDown(x, y):
    return touchDown(x, y)

def sendTouchUp(x, y):
    return touchUp(x, y)

def sendTouchMove(x, y):
    return touchMove(x, y)

def sendTap(x, y):
    touchDown(x, y)
    time.sleep(0.1)
    touchUp(x, y)
    return True

def sendMouseDown(button=1):
    if button == 1:
        flags = MOUSEEVENTF_LEFTDOWN
    elif button == 2:
        flags = MOUSEEVENTF_MIDDLEDOWN
    elif button == 3:
        flags = MOUSEEVENTF_RIGHTDOWN
    else:
        return False
    event = Mouse(flags, 0, 0, 0)
    return sendInput(event)

def sendMouseUp(button=1):
    if button == 1:
        flags = MOUSEEVENTF_LEFTUP
    elif button == 2:
        flags = MOUSEEVENTF_MIDDLEUP
    elif button == 3:
        flags = MOUSEEVENTF_RIGHTUP
    else:
        return False
    event = Mouse(flags, 0, 0, 0)
    return sendInput(event)

def sendMouseMove(x, y, button=1):
    flags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE
    x = x * 65535 /_mouse_input_area[0]
    y = y * 65535 /_mouse_input_area[1]
    event = Mouse(flags, x, y, 0)
    return sendInput(event)

def windowList():
    windows = []
    def enumWindowsProc(hwnd, p):
        props = windowProperties(hwnd)
        bbox = props["bbox"]
        # skip zero-sized windows
        if bbox[0] < bbox[2] and bbox[1] < bbox[3]:
            windows.append(props)
        return True

    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                         ctypes.wintypes.HWND,
                                         ctypes.c_void_p)
    callback = EnumWindowsProc(enumWindowsProc)
    ctypes.windll.user32.EnumWindows(callback, 0)
    return windows

def topWindowWidgets():
    hwnd = topWindow()
    if not hwnd:
        return None
    return windowWidgets(hwnd)

def windowWidgets(hwnd):
    """
    Returns dictionary hwnd -> [winfo, ...]
    where winfo is a tuple:
        hwnd, parenthwnd, classname, text, (left, top, right, bottom)
    """
    GetClassName = ctypes.windll.user32.GetClassNameW
    GetWindowRect = ctypes.windll.user32.GetWindowRect
    SendMessage = ctypes.windll.user32.SendMessageW
    SBUFSIZE = 2048
    sbuf = ctypes.create_unicode_buffer(SBUFSIZE)
    r = ctypes.wintypes.RECT()

    rootProp = windowProperties(hwnd)
    rootInfo = (hwnd, None, "", rootProp["title"], rootProp["bbox"])

    widgets = {hwnd: [], "root": [rootInfo]}
    def enumChildProc(child_hwnd, parent_hwnd):
        GetWindowRect(child_hwnd, ctypes.byref(r))
        if r.top == r.bottom or r.left == r.right:
            # nobody can click this size of object or its children
            # => skip them
            return True

        GetClassName(child_hwnd, sbuf, SBUFSIZE)
        cname = sbuf.value

        textLen = SendMessage(child_hwnd, WM_GETTEXT, SBUFSIZE, ctypes.byref(sbuf))
        if textLen:
            text = sbuf.value
        else:
            text = ""

        winfo = (child_hwnd, parent_hwnd, cname, text, (r.left, r.top, r.right, r.bottom))
        widgets[parent_hwnd].append(winfo)
        widgets[child_hwnd] = []
        ctypes.windll.user32.EnumChildWindows(child_hwnd, cb, child_hwnd)
        return True
    EnumChildProc = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                       ctypes.wintypes.HWND,
                                       ctypes.c_void_p)
    cb = EnumChildProc(enumChildProc)
    ctypes.windll.user32.EnumChildWindows(hwnd, cb, hwnd)
    return widgets

def _dumpTree(depth, key, wt):
    for hwnd, parent, cname, text, rect in wt[key]:
        print "%s%s (%s) cls='%s' text='%s' rect=%s" % (
            " " * (depth*4), hwnd, parent, cname, text, rect)
        if hwnd in wt:
            _dumpTree(depth + 1, hwnd, wt)

def dumpWidgets():
    hwnd = topWindow()
    wt = widgetList(hwnd)
    _dumpTree(0, hwnd, wt)

def shell(command):
    if isinstance(command, list):
        useShell = False
    else:
        useShell = True
    try:
        output = subprocess.check_output(command, shell=useShell)
    except subprocess.CalledProcessError, e:
        if hasattr(e, "output"):
            output = e.output
        else:
            output = None
    return output

def _exitStatusWriter(process, statusFile):
    statusFile.write(str(process.wait()))
    statusFile.close()

def shellSOE(command, asyncStatus=None, asyncOut=None, asyncError=None):
    if isinstance(command, list):
        useShell = False
    else:
        useShell = True

    if (asyncStatus, asyncOut, asyncError) != (None, None, None):
        # asynchronous execution
        if not asyncStatus or asyncStatus == True:
            asyncStatus = os.devnull
        if not asyncOut or asyncOut == True:
            asyncOut = os.devnull
        if not asyncError or asyncError == True:
            asyncError = os.devnull
        sFile = file(asyncStatus, "w")
        oFile = file(asyncOut, "w")
        eFile = file(asyncError, "w")
        p = subprocess.Popen(command, shell=useShell,
                             stdin = file(os.devnull),
                             stdout = oFile,
                             stderr = eFile)
        thread.start_new_thread(_exitStatusWriter, (p, sFile))
        return (None, None, None)

    # synchronous execution
    try:
        p = subprocess.Popen(command, shell=useShell,
                             stdin = subprocess.PIPE,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
        out, err = p.communicate()
        status = p.returncode
    except OSError:
        status, out, err = None, None, None
    return status, out, err

def topWindow():
    return ctypes.windll.user32.GetForegroundWindow()

def topWindowProperties():
    hwnd = topWindow()
    if not hwnd:
        return None
    return windowProperties(hwnd)

def windowProperties(hwnd):
    props = {'hwnd': hwnd}
    titleLen = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    titleLen = min(titleLen, 2047) # limit max length for safety
    titleBuf = ctypes.create_unicode_buffer(titleLen + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, titleBuf, titleLen + 1)

    r = ctypes.wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(r))

    props['title'] = titleBuf.value
    props['bbox'] = (r.left, r.top, r.right, r.bottom) # x1, y2, x2, y2
    return props

def launchHTTPD():
    global _HTTPServerProcess
    _HTTPServerProcess = subprocess.Popen("python -m SimpleHTTPServer 8000")
    return True

def stopHTTPD():
    print "stopping " + str(_HTTPServerProcess)
    _HTTPServerProcess.terminate()
    return True

def screenshotTakerThread():
    # Screenshots must be taken in the same thread. If BitBlt is
    # called from different threads, screenshots are not update. On the
    # other hand, creating new GetDC + ... for every screenshot worked
    # on 32-bit Python in separate threads, but did not work in 64-bit
    # after the first thread. Pythonshare-server creates a new thread for
    # each connection. Therefore we need a single screenshot taker thread.
    global _g_lastWidth, _g_lastHeight

    def takerFree(srcdc, memdc, bmp):
        if bmp != None:
            ctypes.windll.gdi32.DeleteObject(bmp)
        if memdc != None:
            ctypes.windll.gdi32.DeleteObject(memdc)
        if srcdc != None:
            ctypes.windll.user32.ReleaseDC(0, srcdc)

    def takerRealloc(width, height, srcdc, memdc, bmp, c_bmp_header, c_bits):
        takerFree(srcdc, memdc, bmp)
        bmp_header = struct.pack('LHHHH', struct.calcsize('LHHHH'), width, height, 1, 24)
        srcdc = ctypes.windll.user32.GetDC(0)
        memdc = ctypes.windll.gdi32.CreateCompatibleDC(srcdc)
        bmp = ctypes.windll.gdi32.CreateCompatibleBitmap(srcdc, width, height)
        c_bmp_header = ctypes.c_buffer(bmp_header)
        c_bits = ctypes.c_buffer(' ' * (height * ((width * 3 + 3) & -4)))
        return srcdc, memdc, bmp, c_bmp_header, c_bits

    srcdc, memdc, bmp, c_bmp_header, c_bits = (None,) * 5

    SRCCOPY = 0xCC0020
    DIB_RGB_COLORS = 0

    width, height = _g_screenshotRequestQueue.get()
    while width != "QUIT":

        if width == None: # try autodetect
            left = ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            right =ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            width = right - left
        else:
            left = 0

        if height == None:
            top = ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            bottom = ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
            height = bottom - top
        else:
            top = 0

        if (width, height) != (_g_lastWidth, _g_lastHeight):
            srcdc, memdc, bmp, c_bmp_header, c_bits = takerRealloc(
                width, height, srcdc, memdc, bmp, c_bmp_header, c_bits)
            _g_lastWidth = width
            _g_lastHeight = height

        print "W x H ==", width, "X", height

        ctypes.windll.gdi32.SelectObject(memdc, bmp)
        ctypes.windll.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, SRCCOPY)
        got_bits = ctypes.windll.gdi32.GetDIBits(
            memdc, bmp, 0, height, c_bits, c_bmp_header, DIB_RGB_COLORS)

        _g_screenshotResponseQueue.put((width, height, zlib.compress(c_bits.raw)))

        width, height = _g_screenshotRequestQueue.get()

    takerFree(srcdc, memdc, bmp)

if not "_mouse_input_area" in globals():
    left = ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    right =ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    top = ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    bottom = ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    width = right - left
    height = bottom - top
    _mouse_input_area = (width, height)

if not "_g_touchInjenctionInitialized" in globals():
    try:
        if (ctypes.windll.user32.InitializeTouchInjection(1, 1) != 0):
            print "Initialized Touch Injection"
            _g_touchInjenctionInitialized = True
        else:
            print "InitializeTouchInjection failed"
    except:
        _g_touchInjenctionInitialized = False
        print "InitializeTouchInjection not supported"

if not "_g_screenshotRequestQueue" in globals():
    # Initialize screenshot thread and communication channels
    _g_lastWidth = None
    _g_lastHeight = None
    _g_screenshotRequestQueue = Queue.Queue(1)
    _g_screenshotResponseQueue = Queue.Queue(1)
    thread.start_new_thread(screenshotTakerThread, ())

if __name__ == '__main__':
    start = time.time()
    screenshot(0)
    end = time.time()
    print "total screenshot time:", end-start
