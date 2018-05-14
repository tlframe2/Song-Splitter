"""
Downloads audio stream of YouTube video from given url, then splits the audio file into individual

songs based on time stamps in the uploader's description box. Useful for albums uploaded as one 

video or song mixes.
"""

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from moviepy.editor import AudioFileClip
from pytube import YouTube
from time import sleep

class Downloader():
    """
    Rips and downloads audio file from YouTube video.

    Attributes:
        url (string): address of YouTube video to be downloaded.
        filename (string): name of downloaded audio file.
        file_size (int): size of audio file in bytes.
    """

    def __init__(self, url):
        """
        Constructor for Downloader class.

        Parameters:
            url (string): address of YouTube video to be downloaded.
        """

        self.url = url
        self.filename = " "
        self.file_size = 0

    def download_file(self):
        """ Downloads audio file. """

        try:
            # Instantiates YouTube object from Pytube module
            yt = YouTube(self.url, on_progress_callback=self.__progress_check)

            # Finds highest quality audio stream
            audio_file = yt.streams.filter(only_audio=True, file_extension='mp4').first()

            # Sets filename attribute to title of video
            self.filename = yt.title + '.mp4'

            # Sets file_size attribute to number of bytes in audio file
            self.file_size = audio_file.filesize

            # Downloads audio file
            audio_file.download()

        except:
            # Prints error message if video cannot be found at given url
            print("Could not find video at url '{}'".format(self.url))

    def __progress_check(self, stream=None, chunk=None, file_handle=None, remaining=None):
        """ 
        Calculates and displays percentage of file that has been downloaded. 
        
        Gets called whenever file is being downloaded.
        """

        # Sleeps for one second so that it isn't running constantly
        sleep(1)
        percent = (100 * (self.file_size - remaining)) / self.file_size
        print(*"{:00.0f}% downloaded \r".format(percent), sep='', end='', flush=True)

class Splitter():
    """
    Splits downloaded audio file into individual songs based on time links on video page.

    Attributes:
        url (string): address of YouTube video to be scraped for time links.
        filename (string): name of downloaded audio file.
    """

    def __init__(self, obj):
        """
        Constructor for Splitter class.

        Parameters:
            obj (Downloader): object created by Downloader class.
        """

        self.url = obj.url
        self.filename = obj.filename

    def split_songs(self):
        """ Creates songs from downloaded audio file by clipping it using provided time links. """

        # Instantiates AudioFileClip object from Moviepy module
        audio = AudioFileClip(self.filename)

        # List of time links scraped from audio file's YouTube page
        times = self.__get_time_links()

        # Creates songs based on number of time links scraped
        for i in range(0, len(times)):

            # Time when song starts in audio file
            start_time = self.__time_str_to_tuple(times[i])

            # Time when song ends in audio file or None if last song
            end_time = None if i == (len(times) - 1) else self.__time_str_to_tuple(times[i + 1])

            # Creates song
            song = audio.subclip(start_time, end_time)
            song.write_audiofile("clip{}.mp3".format(i+1))

    def __get_time_links(self):
        """ 
        Scrapes time links from YouTube page and adds them to list.
        
        Returns:
            time_list: list of strings of song times scraped from webpage.
        """

        try:
            # Opens page at given url
            html = urlopen(self.url)

        except HTTPError as err:
            # Prints error message if unable to connect to Internet
            print(err)

        else:
            # Instantiates BeautifulSoup object
            bsObj = BeautifulSoup(html, "lxml")

            # Identifies anchor tags on page as time links and adds them to list as strings
            time_list = []
            time_links = bsObj.findAll("a", {"href": "#"})
            for link in time_links:
                time_list.append(link.get_text())
            return time_list

    def __time_str_to_tuple(self, time_str):
        """
        Converts times from strings to tuples.

        Returns:
            tuple: time converted to tuple as either (mm,ss) or (hh,mm,ss)
        """

        return tuple(map(int, time_str.split(":")))

def main():
    """ Main function. """

    # Prompts user for video url
    url = input("Enter video url: ")

    # Instantiates Downloader object using given url
    download = Downloader(url)

    # Downloads audio file
    download.download_file()

    # Instantiates Splitter object using attributes of Downloader object
    splitter = Splitter(download)

    # Splits audio file into individual songs
    splitter.split_songs()

if __name__ == '__main__':

    # Executes main function
    main()
