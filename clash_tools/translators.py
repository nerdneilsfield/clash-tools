import re

from clash_tools import ClashSsProxyItem, ClashVmessProxyItem


class ConfigurationTranslator(object):
    pass


class SsTranslator(ConfigurationTranslator):

    @staticmethod
    def match(text):
        ss_reg = re.compile(r"^ss://.*", re.S)
        return ss_reg.match(text)

    @staticmethod
    def parse(text):
        ss_proxy = ClashSsProxyItem()
        ss_proxy.load_from_url(text)
        return ss_proxy


class VmessTranslator(ConfigurationTranslator):

    @staticmethod
    def match(text):
        vmess_reg = re.compile(r"^vmess://.*", re.S)
        return vmess_reg.match(text)

    @staticmethod
    def parse(text):
        vmess_proxy = ClashVmessProxyItem()
        vmess_proxy.load_from_url(text)
        return vmess_proxy
