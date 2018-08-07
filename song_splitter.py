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
from sys import argv

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
        self.audio_file = None
        self.filename = " "
        self.file_size = 0

    def get_video_info(self):
        """ Instantiates YouTube object from PyTube module and assigns video info to Downloader object's attributes. """

        yt = YouTube(self.url, on_progress_callback=self.progress_check)
        
        self.audio_file = yt.streams.filter(only_audio=True, file_extension='mp4').first()
        self.filename = yt.title + '.mp4'
        self.file_size = self.audio_file.filesize

    def download_file(self):
        """ Downloads file to same location as this script. """

        self.audio_file.download()

    def progress_check(self, stream=None, chunk=None, file_handle=None, remaining=None):
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
        times = self.get_time_links()

        # Creates songs based on number of time links scraped
        for i in range(0, len(times)):

            # Time when song starts in audio file
            start_time = Splitter.time_str_to_tuple(times[i])

            # Time when song ends in audio file or None if last song
            end_time = None if i == (len(times) - 1) else Splitter.time_str_to_tuple(times[i + 1])

            # Creates song
            song = audio.subclip(start_time, end_time)
            song.write_audiofile("clip{}.mp3".format(i+1))

    def get_time_links(self):
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

    @staticmethod
    def time_str_to_tuple(time_str):
        """
        Converts times from strings to tuples.

        Parameters:
            time_str (string): time song starts in video

        Returns:
            tuple of time_str converted to either (mm,ss) or (hh,mm,ss)
        """

        return tuple(map(int, time_str.split(":")))

def main():
    """ Main function. """

    # Prompts user for video url if none is given as a command line argument
    url = input("Enter video url: ") if len(argv) == 1 else argv[1]

    # Instantiates Downloader object using given url
    dl = Downloader(url)

    # Downloads audio file
    dl.get_video_info()
    dl.download_file()

    # Instantiates Splitter object using attributes of Downloader object
    split = Splitter(dl)

    # Splits audio file into individual songs
    split.split_songs()

if __name__ == '__main__':

    # Executes main function
    main()
