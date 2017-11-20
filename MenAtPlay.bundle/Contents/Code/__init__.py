# MenAtPlay
import re
import os
import platform
import simplejson as json

# Log Title
PLUGIN_LOG_TITLE = 'Men At Play'

VERSION_NO = '2017.11.10.0'

# Delay used when requesting HTML, may be good to have to prevent being
# banned from the site
REQUEST_DELAY = 0

# URLS
BASE_URL = 'http://www.menatplay.com/%s'

# Example Movie URL http://www.menatplay.com/movie/the-barber
BASE_MOVIE_URL = 'http://www.menatplay.com/movie/'

# File names to match for this agent
movie_pattern = re.compile(Prefs['regex'])

def Start():
    HTTP.CacheTime = CACHE_1WEEK
    HTTP.Headers['User-agent'] = 'Mozilla/4.0 (compatible; MSIE 8.0; ' \
        'Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; ' \
        '.NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'

class MenAtPlay(Agent.Movies):
    name = 'Men At Play'
    languages = [Locale.Language.NoLanguage, Locale.Language.English]
    primary_provider = False
    fallback_agent = ['com.plexapp.agents.gayporncollector']
    contributes_to = ['com.plexapp.agents.cockporn']

    def Log(self, message, *args):
        if Prefs['debug']:
            Log(PLUGIN_LOG_TITLE + ' - ' + message, *args)

    def search(self, results, media, lang, manual):
        title = media.primary_metadata.title
        filename = media.items[0].parts[0].file
        self.Log('-----------------------------------------------------------')
        self.Log('SEARCH CALLED v.%s', VERSION_NO)
        self.Log('SEARCH - Platform: %s %s', platform.system(),
                 platform.release())
        self.Log('SEARCH - media.title - %s', media.title)
        self.Log('SEARCH - filename - %s', filename)
        self.Log('SEARCH - title - %s', title)
        self.Log('SEARCH - media.items - %s', media.items)
        self.Log('SEARCH - media.filename - %s', media.filename)
        self.Log('SEARCH - lang - %s', lang)
        self.Log('SEARCH - manual - %s', manual)
        self.Log('SEARCH - Prefs->cover - %s', Prefs['cover'])
        self.Log('SEARCH - Prefs->folders - %s', Prefs['folders'])
        self.Log('SEARCH - Prefs->regex - %s', Prefs['regex'])

        if not filename:
            return

        (file_title, _) = os.path.splitext(os.path.basename(filename.lower()))
        final_dir = os.path.basename(os.path.dirname(filename.lower()))
        self.Log('SEARCH - Enclosing Folder: %s', final_dir)

        if Prefs['folders'] != "*":
            folder_list = re.split(',\s*', Prefs['folders'].lower())
            if final_dir not in folder_list:
                self.Log('SEARCH - Skipping %s because the folder %s is not '
                         'in the acceptable folders list: %s', filename,
                         final_dir, ','.join(folder_list))
            return

        m = movie_pattern.search(file_title)
        if not m:
            self.Log('SEARCH - Skipping %s because the file name is not in '
                     'the expected format.', file_title)
            return

        # sanitize the file name by removing special character sequences and
        # replacing each sequence with a space
        sanitized_name = re.sub('[^a-z0-9]+' , ' ' , file_title)

        # Get the title from the sanitized name
        m = re.search(r"(map)?[ \\-]*(?P<>.+)$" , sanitized_name)
        if not m:
            self.Log('Unable to get title from name!')
            return
        self.Log('SEARCH - Sanitized Name: %s', sanitized_name)

        # remove the resolution from the end and strip spacing
        file_title = re.sub('[0-9]{3,4}p', '', m.group('title')).strip()
        self.Log('SEARCH - File Title: %s', file_title)
        self.Log('SEARCH - Split File Title: %s' % file_title.split(' '))

        # file_title = file_title.replace(' ', '-')
        file_title = re.sub( ' ' , '-' , file_title)
        self.Log('SEARCH - File Title for URL: %s', file_title)

        movie_url = BASE_MOVIE_URL + file_title

        self.Log('SEARCH - Video URL: %s', movie_url)
        try:
            html = HTML.ElementFromURL(movie_url, sleep=REQUEST_DELAY)
        except:
            file_title = "the-" + file_title
            movie_url = BASE_MOVIE_URL + file_title
            self.Log('SEARCH - Video URL: %s', movie_url)
            try:
                html = HTML.ElementFromURL(movie_url, sleep=REQUEST_DELAY)
            except:
                self.Log("SEARCH - Title not found: %s" % movie_url)
                return

    def fetch_movie_name(self, html, metadata)
        movie_name = html.xpath('//*[@id="content"]/article/div[2]/div[1]/div[1]/h1'
                                'text()')
        self.Log('SEARCH - title: %s', movie_name)
        metadata.title = movie_name

    def fetch_summary(self, html, metadata):
        raw_about_text = html.xpath('//*[@id="content"]/article/div[2]/div[1]/div[1]/div[2]/div[1]/p/text()')
        self.Log('UPDATE - About Text - RAW %s', raw_about_text)
        about_text = ' '.join(str(x.text_content().strip())
                              for x in raw_about_text)
        metadata.summary = about_text

    def fetch_release_date(self, html, metadata):
        release_date = html.xpath('//*[@id="content"]/article/div[2]/div[1]/div[1]/div[1]/div'
                                  'text()')[0].strip()
        self.Log('UPDATE - Release Date - New: %s' % release_date)
        metadata.originally_available_at = \
            Datetime.ParseDate(release_date).date()
        metadata.year = metadata.originally_available_at.year

    def fetch_roles(self, html, metadata):
        metadata.roles.clear()
        htmlcast = html.xpath('//*[@id="scroll"]/div[2]/ul[2]/li/a/span/'
                              'text()')
        self.Log('UPDATE - cast: "%s"' % htmlcast)
        for cast in htmlcast:
            cname = cast.strip()
            if (len(cname) > 0):
                role = metadata.roles.new()
                role.name = cname

    def update(self, metadata, media, lang, force=False):
        self.Log('UPDATE CALLED')

        if not media.items[0].parts[0].file:
            return

        file_path = media.items[0].parts[0].file
        self.Log('UPDATE - File Path: %s', file_path)
        self.Log('UPDATE - Video URL: %s', metadata.id)

        # Fetch HTML
        html = HTML.ElementFromURL(metadata.id, sleep=REQUEST_DELAY)

        # Set tagline to URL
        metadata.tagline = metadata.id

        # Try to get Video title
        try:
            self.fetch_movie_name(html, metadata)
        except:
            pass

        # Try to get description text
        try:
            self.fetch_summary(html, metadata)
        except:
            pass

        # Try to get release date
        try:
            self.fetch_release_date(html, metadata)
        except:
            pass

        # Try to get and process the video cast
        try:
            self.fetch_roles(html, metadata)
        except:
            pass

        valid_image_names = self.fetch_gallery(html, metadata)
        metadata.posters.validate_keys(valid_image_names)

        # Set Content Rating to X
        metadata.content_rating = 'X'

        # Set Studio to Men At Play
        metadata.studio = 'Men At Play'

        # Set Genres to Men At Play
        metadata.genres = 'Men At Play'
