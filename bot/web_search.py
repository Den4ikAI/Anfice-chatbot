from googlesearch import search
import wikipedia
import logging
import trafilatura
from trafilatura.settings import use_config

wikipedia.set_lang('ru')
config = use_config()
config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

class InternetSearch:
    def __init__(self):
        self.logger = logging.getLogger('Internet search')

    def get_num_words(self, text):
        if text is not None:
            return len(text.split(' '))
        else:
            return 0

    def check_blacklist(self, url):
        blacklist = ['tikt', 'vk', 'twitter', 'znanij', 'tube']
        for bad in blacklist:
            if bad in url:
                self.logger.warning('Url [{}] in blacklist!'.format(url))
                return False

        return True

    def get_url_text(self, url):
        downloaded = trafilatura.fetch_url(url)
        output = trafilatura.extract(downloaded, config=config)
        return output

    def wiki_sort(self, lst):
        wiki_index = [i for i in range(len(lst)) if 'wiki' in lst[i]]
        wiki_str = lst[wiki_index[0]]
        del lst[wiki_index[0]]
        return [wiki_str] + sorted(lst)

    def web_search(self, qtext, num_return_sequences):
        outputs = []
        urls = []
        qtext = qtext.replace('?','')
        if qtext.lower().startswith('что') or qtext.lower().startswith('кто'):
            try:
                outputs.append(wikipedia.summary(qtext))
            except wikipedia.WikipediaException as e:
                self.logger.warning(e)
        if len(outputs) == 0:
            for url in search(qtext, num=num_return_sequences, stop=num_return_sequences):
                urls.append(url)
            # print(urls)
            for i in urls:
                if 'wiki' in i:
                    urls = self.wiki_sort(urls)
                    break

            for url in urls:
                if self.check_blacklist(url):
                    try:
                        text = self.get_url_text(url)
                        if self.get_num_words(text) > 50:
                            outputs.append(text)
                        else:
                            self.logger.warning('Url [{}] does not have text!'.format(url))
                    except Exception as e:
                        self.logger.exception(e)
        return outputs
