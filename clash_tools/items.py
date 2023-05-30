import base64
import json
import logging
import re
from urllib.parse import unquote, urlparse


class ClashProxyItem(object):
    pass


class ClashSsProxyItem(ClashProxyItem):
    def __init__(self):
        self.type = "ss"
        self.server = ""
        self.cipher = ""
        self.password = ""
        self.name = ""
        self.port = ""
        self.plugin = ""
        self.plugin_opts = {}

    def to_dict(self):
        res_dict = {}

        # convert properties to dict
        res_dict["type"] = self.type
        res_dict["server"] = self.server
        res_dict["cipher"] = self.cipher
        res_dict["password"] = self.password
        res_dict["name"] = self.name
        res_dict["port"] = self.port
        res_dict["plugin"] = self.plugin
        res_dict["plugin-opts"] = self.plugin_opts

        return res_dict

    def load_from_url(self, text):
        url_content = urlparse(text)

        self.name = unquote(url_content.fragment)
        plugin_text = unquote(url_content.query)
        netloc = unquote(url_content.netloc)

        auth_text = netloc.split("@")[0]
        missing_padding = 4 - len(auth_text) % 4
        auth_text += missing_padding * "="
        auth_text_decoded = base64.b64decode(auth_text).decode("utf-8")
        self.cipher = auth_text_decoded.split(":")[0]
        self.password = auth_text_decoded.split(":")[1]

        self.server = netloc.split("@")[1].split(":")[0]
        self.port = netloc.split("@")[1].split(":")[1]
        self.type = "ss"

        plugin_res = re.findall(r"plugin=(.+?);", plugin_text, re.S)

        if len(plugin_res) > 0:
            plugin = str(plugin_res[0])
            if plugin == "obfs-local":
                self.plugin = "obfs"
                plugin_text = plugin_text.replace("plugin=obfs-local;", "")
                plugin_mode = re.findall(r"obfs=(.+?);", plugin_text, re.S)
                if len(plugin_mode) > 0:
                    self.plugin_opts["mode"] = str(plugin_mode[0])
                    plugin_text = plugin_text.replace("obfs=%s;" % plugin_mode[0], "")

                    plugin_host = re.findall(r"obfs-host=(.*)", plugin_text, re.S)
                    if len(plugin_host) > 0:
                        self.plugin_opts["host"] = str(plugin_host[0])
            elif plugin == "v2ray-plugin":
                pass


class ClashVmessProxyItem(ClashProxyItem):
    def __init__(self):
        self.type = "vmess"
        self.server = ""
        self.cipher = ""
        self.name = ""
        self.port = ""
        self.uuid = ""
        self.aid = ""
        self.udp = ""
        self.tls = ""
        self.skip_cert_verify = ""
        self.server_name = ""
        self.network = ""
        self.ws_opts = {}
        self.h2_opts = {}

        self.version = 2

        self.json_data = {}

    def to_dict(self):
        res_dict = {}

        # convert properties to dict
        res_dict["type"] = self.type
        res_dict["server"] = self.server
        res_dict["name"] = self.name
        res_dict["port"] = self.port
        res_dict["uuid"] = self.uuid
        res_dict["alterId"] = self.aid
        if self.cipher == "":
            res_dict["cipher"] = "auto"
        if self.udp != "":
            res_dict["udp"] = self.udp
        if self.tls != "":
            res_dict["tls"] = self.tls
        if self.skip_cert_verify != "":
            res_dict["skip-cert-verify"] = self.skip_cert_verify
        if self.network != "":
            res_dict["network"] = self.network
        if self.server_name != "":
            res_dict["servername"] = self.server_name
        if self.ws_opts != {}:
            res_dict["ws-opts"] = self.ws_opts
        if self.h2_opts != {}:
            res_dict["h2-opts"] = self.h2_opts

        return res_dict

    def load_from_url(self, text):
        text = text.replace("vmess://", "")

        missing_padding = 4 - len(text) % 4
        text += missing_padding * "="
        text_decoded = base64.b64decode(text)

        self.json_data = json.loads(text_decoded)

        logging.debug(self.json_data)

        self.name = self.json_data["ps"]
        self.port = self.json_data["port"]
        self.server = self.json_data["add"]
        self.version = int(self.json_data["v"])
        self.uuid = self.json_data["id"]
        self.aid = self.json_data["aid"]
        network = self.json_data["net"]

        if network == "ws":
            self.network = "ws"
            self.ws_opts["path"] = self.json_data["path"]
            self.ws_opts["headers"] = {}
            self.ws_opts["headers"]["Host"] = self.json_data["host"]
            # self.ws_opts['headers']['Sec-WebSocket-Protocol'] = self.json_data['ws-path']

        if network == "tcp":
            self.network = ""
