import sys
import os
import requests

from text_process import Text_Process
from .diggly_serializers import TopicCreator, TopicLinkSerializer
from ..models import Topic, TopicLink

# 2016 wikidiggly
# author: ola-halima
# prototype v1

base_url= "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&formatversion=2&{}"
base_url_extract= "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&{}"
wiki_url_base= "https://en.wikipedia.org/wiki/{}"
exintro= "&exintro="
exsentences= "&exsentences={}"
r_title= "title={}"
r_pageid= "pageids={}"
arg_seperator= "|" 

class WikipediaHelper():
    desc_len = 0
    summ_len = 0 
    t_processor = Text_Process(desc_len, summ_len)
    t_creator = TopicCreator()

    @classmethod
    def __init__(self, desc_len, summ_len): 
        desc_length = desc_len
        summ_length = summ_len    

    def get_article(self, r_args):
        resources = self.format_req(r_args)

        r_url = base_url_extract.format(resources)
        resp = requests.get(r_url)

        if resp.status_code != 200:
            #TODO: handle exception better
            raise ApiError('GET: article information\n{}'.format(resp.status_code))

        #print resp.json()
        pages = resp.json()['query']['pages']
        topics = self.parse_pages(pages)

        return topics

    def parse_pages(self, pages):
        topics = []
        print pages

        for page in pages:
            print page
            #TODO: find way to trip content length from api call
            content = page['extract'] #TODO: fix this to make bug proof
            
            print content
            parsedtext = self.t_processor.get_desc_summ(content)

            data = {"article_id" : int(page['pageid']),
                    "article_title" : page['title'],
                    "description" : parsedtext[self.t_processor.desc_text],
                    "summary" : parsedtext[self.t_processor.summ_text],
                    "wiki_link" : wiki_url_base.format("_".join(title.split()))}
            #TODO: fix url generation

            topic = self.t_creator.create_topic(data)        
            topics.append(topic)

        return topic

    def format_req(self, r_args):
        if self.__is_seq(r_args): # check if arg is a list
            if self.__is_pageid(r_args[0]):
                return r_pageid.format(arg_separator.join(r_args))
            else:
                return r_title.format(arg_separator.join(r_args))
    
        if self.__is_pageid(r_args):
            return r_pageid.format(r_args)

        #default return single page title format
        return r_title.format(r_args)

    #private functions
    def __is_pageid(self, arg):
        try:
            pid = int(arg)
            return True;
    
        except ValueError:
            return False;    

    def __is_seq(self, arg):
        return (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))