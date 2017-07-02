# MicroPython JQ6500 sound module library
![lcd](http://www.rototron.info/wp-content/uploads/jq6500mp_01.jpg "JQ6500")

A library to control a JQ6500 sound module in serial mode on an ESP32 or other compatible board running MicroPython.

Example:
```
from jq6500 import Player
p = Player(port=2)
p.set_volume(30)
p.play()
p.get_length()
p.clean_up()
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
