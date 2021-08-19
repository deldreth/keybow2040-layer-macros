import math
import board
from keybow2040 import Keybow2040, number_to_xy, hsv_to_rgb

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

keyboard = Keyboard(usb_hid.devices)
consumer_control = ConsumerControl(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

i2c = board.I2C()
keybow = Keybow2040(i2c)
keys = keybow.keys

keybow.led_sleep_enabled = True
keybow.led_sleep_time = 300

row1 = range(0, 3)
row2 = range(4, 7)
row3 = range(8, 11)
row4 = range(12, 15)

layer = 0

# The window keymap is used to bind keys to changing Windows desktop, browser tabs, new and old tables, and alt tab behaviors.
window_keymap = [
    ((Keycode.ALT, Keycode.TAB), (255, 225, 0)),
    ((Keycode.CONTROL, Keycode.GUI, Keycode.LEFT_ARROW), (255, 120, 0)),
    ((Keycode.CONTROL, Keycode.SHIFT, Keycode.TAB), (255, 50, 0)),
    None,
    (Keycode.TAB, (229, 199, 255)),
    ((Keycode.CONTROL, Keycode.SHIFT, Keycode.T), (61, 177, 255)),
    ((Keycode.CONTROL, Keycode.W), (255, 0, 0)),
    None,
    (Keycode.ALT, (165, 61, 255)),
    (None, (0, 100, 166)),
    ((Keycode.CONTROL, Keycode.T), (50, 255, 0)),
    None,
    ((Keycode.CONTROL, Keycode.SHIFT, Keycode.N), (70, 0, 130)),
    ((Keycode.CONTROL, Keycode.GUI, Keycode.RIGHT_ARROW), (255, 120, 0)),
    ((Keycode.CONTROL, Keycode.TAB), (255, 50, 0)),
    None,
]
window_layer = (keys[3], (255, 255, 255), window_keymap)

vscode_keymap = [
    ((Keycode.CONTROL, Keycode.U), (255, 0, 0)),
    None,
    None,
    None,
    ((Keycode.CONTROL, Keycode.ALT, Keycode.DOWN_ARROW), (255, 255, 0)),
    ((Keycode.CONTROL, Keycode.ALT, Keycode.UP_ARROW), (255, 255, 0)),
    None,
    None,
    ((Keycode.CONTROL, Keycode.D), (0, 255, 20)),
    None,
    None,
    None,
    (ConsumerControlCode.VOLUME_DECREMENT, (175, 0, 255), True),
    (ConsumerControlCode.VOLUME_INCREMENT, (175, 0, 255), True),
    (ConsumerControlCode.MUTE, (255, 0, 20), True),
    None,
]
vscode_layer = (keys[7], (255, 255, 255), vscode_keymap)

arrow_keymap = [
    (Keycode.SHIFT, (50, 0, 255)),
    (Keycode.A, (50, 255, 0)),
    (Keycode.Q, (255, 120, 0)),
    None,
    None,
    (Keycode.S, (50, 255, 0)),
    (Keycode.W, (50, 255, 0)),
    None,
    (Keycode.CONTROL, (100, 0, 255)),
    (Keycode.D, (50, 255, 0)),
    (Keycode.E, (0, 0, 255)),
    None,
    (Keycode.SPACE, (175, 0, 255)),
    None,
    None,
    None,
]
arrow_layer = (keys[11], (255, 255, 255), arrow_keymap)

number_keymap = [
    (None, (229, 199, 255)),
    (Keycode.FIVE, (165, 61, 255)),
    (Keycode.ONE, (70, 0, 130)),
    None,
    (Keycode.NINE, (229, 199, 255)),
    (Keycode.SIX, (165, 61, 255)),
    (Keycode.TWO, (70, 0, 130)),
    None,
    (Keycode.ZERO, (229, 199, 255)),
    (Keycode.SEVEN, (165, 61, 255)),
    (Keycode.THREE, (70, 0, 130)),
    None,
    (None, (229, 199, 255)),
    (Keycode.EIGHT, (165, 61, 255)),
    (Keycode.FOUR, (70, 0, 130)),
    None,
]
number_layer = (keys[15], (255, 255, 255), number_keymap)

layers = [window_layer, vscode_layer, arrow_layer, number_layer]

def reset_layers():
    for layer in layers:
        layer[0].set_led(255, 255, 255)


def reset_rows():
    for row in [row1, row2, row3, row4]:
        for key in row:
            keys[key].set_led(0, 0, 0)


def init():
    keybow.set_all(0, 0, 0)

    for key, rgb, _ in [window_layer, vscode_layer, arrow_layer, number_layer]:
        key.set_led(*rgb)


@keybow.on_press(window_layer[0])
def red_handler(key):
    global layer
    layer = 1
    render_layer(window_layer[2])


@keybow.on_press(vscode_layer[0])
def orange_handler(key):
    global layer
    layer = 2
    render_layer(vscode_layer[2])


@keybow.on_press(arrow_layer[0])
def green_handler(key):
    global layer
    layer = 3
    render_layer(arrow_layer[2])


@keybow.on_press(number_layer[0])
def purple_handler(key):
    global layer
    layer = 4
    render_layer(number_layer[2])


def render_layer(layer_keymap):
    reset_rows()
    reset_layers()

    for key in keys:
        if layer_keymap[key.number] is not None:
            key.set_led(*layer_keymap[key.number][1])

            @keybow.on_press(key)
            def layer_key_press(key):
                keycode, _, *rest = layer_keymap[key.number]
                if len(rest) > 0:
                    consumer_control.send(keycode)

                if keycode and type(keycode) is tuple:
                    keyboard.press(*keycode)
                elif keycode:
                    keyboard.press(keycode)

            @keybow.on_release(key)
            def layer_key_release(key):
                keycode, _, *rest = layer_keymap[key.number]
                if len(rest) > 0:
                    return

                if keycode and type(keycode) is tuple:
                    keyboard.release(*keycode)
                elif keycode:
                    keyboard.release(keycode)


rainbow = False


@keybow.on_hold(window_layer[0])
def hold_handler(key):
    global layer
    global rainbow
    layer = 0
    rainbow = not rainbow
    keybow.led_sleep_enabled = not rainbow

    if (not rainbow):
        init()


step = 1

init()

while True:
    # Always remember to call keybow.update() on every iteration of your loop!
    keybow.update()

    if layer is not 0:
        hue = ((step / 20)) / 20
        # hue = hue - int(hue)
        # hue = hue - math.floor(hue)

        # Display it on the key!
        layers[layer - 1][0].set_led(*hsv_to_rgb(hue, 1, 1))
        step += 1

    if rainbow:
        step += 4

        for i in range(16):
            # Convert the key number to an x/y coordinate to calculate the hue
            # in a matrix style-y.
            x, y = number_to_xy(i)

            # Calculate the hue.
            hue = (x + y + (step / 20)) / 8
            hue = hue - int(hue)
            hue = hue - math.floor(hue)

            # Convert the hue to RGB values.
            r, g, b = hsv_to_rgb(hue, 1, 1)

            # Display it on the key!
            keys[i].set_led(r, g, b)
