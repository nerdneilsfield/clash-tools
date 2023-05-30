import base64
import logging

import yaml
import pyaes

from clash_tools import SsTranslator, VmessTranslator

class Subscriber(object):
    def __init__(self, url=None, name=None, rule_tags=None):
        self.proxies = []
        self.proxies_name = []
        self.url = url
        self.name = name
        self.rule_tags = rule_tags
        self.type = ""  # ss, clash
        self.key = ""  # the key of aes
        if self.rule_tags:
            self.rules = list(rule_tags.keys())
        else:
            self.rules = []

    def __str__(self):
        res = f"Subscriber: {self.name} {self.url}"
        for i in self.rules:
            res += f"\n\t{i}: {self.rule_tags[i]}"
        return res

    def init_with_object(self, sub_object):
        """init subscriber with object for subscribers file"""
        """ a example configuration shold look like"""
        """subscribers:"""
        """  - name: "test1" """
        """    url: "http://example.com" """
        """    rule_tags: """
        """       - rule1:  """
        """          - tag1  """
        """          - tag2  """
        """       - rule2:   """
        """          - tag2  """
        """          - tag3  """
        logging.debug(f"init subscriber with object {sub_object}")
        self.url = sub_object['url']
        self.name = sub_object['name']
        self.rule_tags = sub_object['rule_tags']
        if "type" in sub_object.keys():
            self.type = sub_object['type']
        else:
            self.type = "clash"
        if "key" in sub_object.keys():
            self.key = sub_object['key']
        else:
            self.key = ""
        self.rules = list(self.rule_tags.keys())

    def get_tags(self, rule_name):
        if rule_name in self.rules:
            return self.rule_tags[rule_name]
        else:
            logging.warning(f"Unknown rule: {rule}")
            return []

    def update_proxies(self):
        logging.info(f"Updating proxies for {self.url}")
        if list(self.url) == 0:
            logging.error(f"url not set for rule: {self.name}")
            return
        else:
            try:
                res = rq.get(self.url, timeout=10)
            except Exception as e:
                logging.error(f"error to retry rule: {self.name}")
                logging.debug(f"url: {self.url}")
                logging.debug(f"error: {e}")
                return

            try:  # parse the config
                logging.debug(f"parsing config for rule: {self.name}")
                logging.debug(f"parsing config with type: {self.type}")
                if self.type == "clash":
                    load_config = yaml.safe_load(res.text)
                    # self.proxies = load_config['proxies']
                    proxies = load_config['proxies']

                    for proxies in proxies:
                        proxies['name'] = unquote(proxies['name'])
                        self.proxies.append(proxies)
                        self.proxies_name.append(unquote(proxies['name']))
                elif self.type == "ss":
                    text = res.text
                    missing_padding = 4 - (len(text) % 4)
                    text += missing_padding * '='

                    text_decoded = base64.b64decode(text).decode("utf-8")
                    proxies_url = text_decoded.split("\n")
                    for url in proxies_url:
                        if SsTranslator.match(url):
                            proxy_item = SsTranslator.parse(url).to_dict()
                            self.proxies.append(proxy_item)
                            self.proxies_name.append(proxy_item['name'])
                        elif VmessTranslator.match(url):
                            proxy_item = VmessTranslator.parse(url).to_dict()
                            self.proxies.append(proxy_item)
                            self.proxies_name.append(proxy_item['name'])
                elif self.type == "clash_aes":

                    if len(self.key) > 32:
                        self.key = self.key[:32]
                    elif len(self.key) < 32:
                        self.key += "=" * (32 - len(self.key))
                    key = self.key.encode("utf-8")
                    aes = pyaes.AESModeOfOperationCTR(key)

                    content = aes.decrypt(res.content).decode("utf-8")
                    missing_padding = 4 - (len(content) % 4)
                    content += missing_padding * '='
                    content_yaml = base64.b64decode(content)
                    load_config = yaml.safe_load(content_yaml)
                    # self.proxies = load_config['proxies']
                    proxies = load_config['proxies']

                    for proxies in proxies:
                        proxies['name'] = unquote(proxies['name'])
                        self.proxies.append(proxies)
                        self.proxies_name.append(unquote(proxies['name']))

            except Exception as e:
                self.proxies = []
                self.proxies_name = []
                logging.error(f"error to parse remote config with {e}")
                line_num = 0
                for line in res.text.split("\n\r"):
                    logging.error(f"{line_num} : {line}")
                    line_num += 1
                return


class Subscribers(object):
    def __init__(self, subscribers_file=None):
        self.subscribers = {}
        self.subscribers_file = subscribers_file
        self.load_subscribers()

        self.subscribers_by_tag = {}

        self.update_tags()

    def __str__(self):
        res = f"subscribers: "
        for subscriber in self.subscribers.values():
            res += str(subscriber)
        return res

    def update_tags(self):
        for sub in self.subscribers.values():
            for rule_ in sub.rules:
                self.subscribers_by_tag[rule_] = {}
                for tag in sub.get_tags(rule_):
                    self.subscribers_by_tag[rule_][tag] = sub.name

    def load_subscribers(self):
        if self.subscribers_file is None:
            logging.error("subscribers file not set")
            return
        else:
            try:
                with open(self.subscribers_file, 'r') as f:
                    logging.info(
                        f"loading subscribers from file: {self.subscribers_file}")
                    load_config = yaml.safe_load(f)
                    for sub_object in load_config['subscribers']:
                        sub = Subscriber()
                        sub.init_with_object(sub_object)
                        self.subscribers[sub.name] = sub
            except Exception as e:
                logging.error(f"error to load subscribers file: {e}")
                return

    def get_subscribers_name_from_tag(self, rule_name, tag_name):
        if rule_name in self.subscribers_by_tag.keys():
            if tag_name in self.subscribers_by_tag[rule_name].keys():
                subscriber_name = self.subscribers_by_tag[rule_name][tag_name]
                return self.get_subscriber_by_name(subscriber_name)
        else:
            return None

    def get_subscriber_by_name(self, sub_name):
        return self.subscribers[sub_name]

    def append(self, subscriber):
        self.subscribers[subscriber.name] = subscriber

    def update_proxies(self):
        logging.debug("Updating proxies for all subscribers")
        for sub_name in self.subscribers.keys():
            self.subscribers[sub_name].update_proxies()
