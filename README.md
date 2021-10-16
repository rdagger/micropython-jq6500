# CircuitPython JQ6500 sound module library
![lcd](http://www.rototron.info/wp-content/uploads/jq6500mp_01.jpg "JQ6500")

A library to control a JQ6500 sound module in serial mode on an board running CircuitPython.

Example:
```
import board
from jq6500 import Player
p = Player(board.TX, board.RX, 30)
p.play()
p.get_length()
p.clean_up()# Ecrit ton programme ici ;-)

```

Available methods:
* get_equalizer
* get_file_count
* get_file_index
* get_folder_count
* get_length
* get_looping
* get_name
* get_position
* get_status
* get_version
* get_volume
* next
* next_folder
* pause
* play
* play_by_index
* play_by_number
* play_pause
* prev
* prev_folder
* restart
* set_equalizer
* set_looping
* set_source
* set_volume
* sleep
* volume_down
* volume_up

Tutorial on my website [Rototron](https://www.rototron.info/raspberry-pi-esp32-micropython-touch-sound-tutorial/) or click picture below for a YouTube video:

[![JQ6500 Tutorial](http://img.youtube.com/vi/QzOkSeeqB8g/0.jpg)](https://youtu.be/QzOkSeeqB8g)
