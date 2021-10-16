"""Micropython serial library for JQ6500 mini MP3 module."""
import board
import busio
from time import sleep


class Player(object):
    """JQ6500 mini MP3 module."""

    EQ_NORMAL = 0
    EQ_POP = 1
    EQ_ROCK = 2
    EQ_JAZZ = 3
    EQ_CLASSIC = 4
    EQ_BASS = 5

    SRC_SDCARD = 1
    SRC_BUILTIN = 4

    LOOP_ALL = 0  # Plays all the tracks and repeats.
    LOOP_FOLDER = 1  # Plays all the tracks in the same folder and repeats.
    LOOP_ONE = 2  # Plays the same track and repeats.
    LOOP_RAM = 3  # Unknown
    LOOP_ONE_STOP = 4  # Plays the track and stops.
    LOOP_NONE = 4

    STATUS_STOPPED = 0
    STATUS_PLAYING = 1
    STATUS_PAUSED = 2

    READ_DELAY = .1

    def __init__(self, rx, tx, volume=20):
        """
        Constructor for JQ6500.

            Args:
                rx: UART RX port.
                tx: UART TX port.
                volume(int) : Initial volume (default: 20, range 0-30).
        """
        self.uart = busio.UART(tx, rx, baudrate=9600)
        self.uart.read()
        self.reset()
        self.set_volume(volume)

    def clean_up(self):
        """Clean up and release resources."""
        self.reset()
        if 'deinit' in dir(self.uart):
            self.uart.deinit()

    def play(self):
        """Play the current file."""
        self.write_bytes([0x0D])

    def play_pause(self):
        """Toggle play or pause for the current file."""
        status = self.get_status()
        if status == self.STATUS_PAUSED or status == self.STATUS_STOPPED:
            self.play()
        elif status == self.STATUS_PLAYING:
            self.pause()

    def restart(self):
        """Restart current playing or paused file from the beginning."""
        old_volume = self.get_volume()
        self.set_volume(0)
        self.next()
        self.pause()
        self.set_volume(old_volume)
        self.prev()

    def pause(self):
        """Pause the current file.  Use play() to resume."""
        self.write_bytes([0x0E])

    def next(self):
        """Play the next file."""
        self.write_bytes([0x01])

    def prev(self):
        """Play the previous file."""
        self.write_bytes([0x02])

    def next_folder(self):
        """Play the next folder."""
        self.write_bytes([0x0F, 0x01])

    def prev_folder(self):
        """Play the previous folder."""
        self.write_bytes([0x0F, 0x00])

    def play_by_index(self, file_index):
        """
        Play file by FAT table index.

        Args:
            file_index (int):  File FAT table index number.

        Notes:
            The index number has nothing to do with the filename.
            To sort SD Card FAT table, search for a FAT sorting utility.
        """
        self.write_bytes([0x03, (file_index >> 8) & 0xFF, file_index & 0xFF])

    def play_by_number(self, folder_number, file_number):
        """
        Play file by folder number and file number.

        Args:
            folder_number (int):  Folder name number.
            file_number (int):  Filename number.

        Notes:
            Only applies to SD Card.
            To use this function, folders must be named from 00 to 99,
            and files must be named from 000.mp3 to 999.mp3.
        """
        self.write_bytes([0x12, folder_number & 0xFF, file_number & 0xFF])

    def volume_up(self):
        """Increase volume by 1 (Volume range 0-30)."""
        self.write_bytes([0x04])

    def volume_down(self):
        """Decrease volume by 1 (Volume range 0-30)."""
        self.write_bytes([0x05])

    def set_volume(self, level):
        """
        Set volume to a specific level.

        Args:
            level (int):  Volume level (Volume range 0-30).
        """
        assert(0 <= level <= 30)
        self.write_bytes([0x06, level])

    def set_equalizer(self, mode):
        """
        Set equalizer to 1 of 6 preset modes.

        Args:
            mode (int): (EQ_NORMAL, EQ_POP, EQ_ROCK, EQ_JAZZ,
                        EQ_CLASSIC, EQ_BASS).
        """
        self.write_bytes([0x07, mode])

    def set_looping(self, mode):
        """
        Set looping mode.

        Args:
            mode (int): (LOOP_ALL , LOOP_FOLDER, LOOP_ONE, LOOP_RAM,
                         LOOP_ONE_STOP, LOOP_NONE).
        """
        self.write_bytes([0x11, mode])

    def set_source(self, source):
        """
        Set source location of MP3 files (on-board flash or SD card).

        Args:
            source (int): (SRC_SDCARD, SRC_BUILTIN).

        Notes:
            SD card requires JQ6500-28P model.
        """
        self.write_bytes([0x09, source])

    def sleep(self):
        """
        Put the device to sleep.

        Notes:
            Not recommended for use with SD cards.
        """
        self.write_bytes([0x0A])

    def reset(self):
        """
        Soft reset of the device.

        Notes:
            Method is not reliable (especially with SD cards).
            Power-cycling is preferable.
        """
        self.write_bytes([0x0C])
        sleep(.5)

    def get_status(self):
        """
        Get device status. (STATUS_PAUSED,STATUS_PLAYING, STATUS_STOPPED).

        Notes:
            Only returns playing or paused with built-in flash.
            Method is unreliable with SD cardsself.
        """
        self.write_bytes([0x42])
        sleep(self.READ_DELAY)
        status = self.uart.read()
        sleep(self.READ_DELAY)
        if status.isdigit():
            return int(status)
        else:
            return -1

    def get_volume(self):
        """Get current volume level (0-30)."""
        self.write_bytes([0x43])
        sleep(self.READ_DELAY)
        level = self.read_bytes()
        return level

    def get_equalizer(self):
        """
        Get current equalizer mode.

        (EQ_NORMAL, EQ_POP, EQ_ROCK, EQ_JAZZ, EQ_CLASSIC, EQ_BASS).
        """
        self.write_bytes([0x44])
        sleep(self.READ_DELAY)
        eq = self.read_bytes()
        return eq

    def get_looping(self):
        """
        Get current looping mode.

        (LOOP_ALL , LOOP_FOLDER, LOOP_ONE, LOOP_RAM, LOOP_ONE_STOP, LOOP_NONE).
        """
        self.write_bytes([0x45])
        sleep(self.READ_DELAY)
        looping = self.read_bytes()
        return looping

    def get_file_count(self, source):
        """
        Return the number of files on the specified media.

        Args:
            source (int): (SRC_SDCARD, SRC_BUILTIN).
        """
        if source == self.SRC_SDCARD:
            self.write_bytes([0x47])
        else:
            # SRC_BUILTIN
            self.write_bytes([0x49])
        sleep(self.READ_DELAY)
        count = self.read_bytes()
        return count

    def get_folder_count(self, source):
        """
        Return the number of folders on the specified media.

        Args:
            source (int): (SRC_SDCARD, SRC_BUILTIN).

        Notes:
            Only SD cards can have folders.
        """
        if source == self.SRC_SDCARD:
            self.write_bytes([0x53])
            count = self.read_bytes()
            return count
        else:
            return 0

    def get_file_index(self, source):
        """
        Get FAT file index of current file.

        Args:
            source (int): (SRC_SDCARD, SRC_BUILTIN).

        Notes:
            Refers to current playing or paused file.  If stopped refers
            to the next file to play.
        """
        if source == self.SRC_SDCARD:
            self.write_bytes([0x4B])
            sleep(self.READ_DELAY)
            count = self.read_bytes()
            return count
        else:
            # SRC_BUILTIN
            self.write_bytes([0x4D])
            sleep(self.READ_DELAY)
            count = self.read_bytes()
            return count + 1

    def get_position(self):
        """Get current position in seconds of current file."""
        self.write_bytes([0x50])
        sleep(self.READ_DELAY)
        position = self.read_bytes()
        return position

    def get_length(self):
        """Get length in seconds of current file."""
        self.write_bytes([0x51])
        sleep(self.READ_DELAY)
        length = self.read_bytes()
        return length

    def get_name(self):
        """
        Get the filename of the current file on the SD card.

        Notes:
            SD card must be active source.
        """
        self.write_bytes([0x52])
        sleep(self.READ_DELAY)
        return self.uart.read()

    def get_version(self):
        """Get version number."""
        self.write_bytes([0x46])
        sleep(self.READ_DELAY)
        version = self.read_bytes()
        return version

    def read_buffer(self):
        """Return UART buffer as bytes."""
        return self.uart.read()

    def read_bytes(self):
        """Return 4 bytes from UART port."""
        b = self.uart.read(4)
        print(b)
        if len(b) > 0:
            return int(b, 16)
        else:
            return -1

    def write_bytes(self, b):
        """
        Write byte(s) to the UART port.

        Args:
            b ([byte]): List of bytes to write to the UART port.
        """
        message_length = len(b) + 1
        data = [0x7E, message_length] + b + [0xEF]
        # print (','.join('0x{:02X}'.format(x) for x in data))
        self.uart.read()
        self.uart.write(bytes(data))