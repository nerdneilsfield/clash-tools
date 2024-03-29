import logging
import os

import yaml

from clash_tools.utils import match_pattern_list


class Rule(object):
    def __init__(self, rule_path, subscribers=None):
        self.name = None
        self.rule_content = None
        self.tags = []
        self.rule_path = rule_path
        self.subscribers = subscribers
        self.proxies_name = []

        self.load_config()
        self.update_tags()

        if self.subscribers:
            self.subscribers.update_proxies()
            for subscriber in self.subscribers.subscribers.values():
                print(subscriber.proxies_name)
                self.add_to_proxies(subscriber.proxies, subscriber.exclude_rules)
                for tag in subscriber.get_tags(self.name):
                    self.add_to_proxies_groups(
                        tag, subscriber.proxies_name, subscriber.exclude_rules
                    )

    def load_config(self):
        try:
            with open(self.rule_path, "r") as rule_file:
                self.rule_content = yaml.safe_load(rule_file)
        except Exception as e:
            logging.error(f"error to parse rule file: {self.rule_path}")
            logging.debug(f"error: {e}")
            return False
        finally:
            return True

    def update_tags(self):
        self.name = self.rule_content["name"]
        del self.rule_content["name"]
        for proxy in self.rule_content["proxy-groups"]:
            self.tags.append(proxy["name"])
        self.tags = list(set(self.tags))

    def add_to_proxies_groups(self, tag_name, proxies_name, exclude_rules):
        """tag_name: the tag of proxies group"""
        """ proxies_name: the list of name of proxies"""
        if tag_name not in self.tags:
            logging.warning(f"tag {tag_name} not in rule")
            return False
        else:
            for i in range(len(self.rule_content["proxy-groups"])):
                if self.rule_content["proxy-groups"][i]["name"] == tag_name:
                    for proxy_name in proxies_name:
                        if self.rule_content["proxy-groups"][i]["proxies"] is not None:
                            if proxy_name not in self.rule_content["proxy-groups"][i][
                                "proxies"
                            ] and not match_pattern_list(exclude_rules, proxy_name):
                                self.rule_content["proxy-groups"][i]["proxies"].append(
                                    proxy_name
                                )
                        else:
                            self.rule_content["proxy-groups"][i]["proxies"] = []
                            if not match_pattern_list(exclude_rules, proxy_name):
                                self.rule_content["proxy-groups"][i]["proxies"].append(
                                    proxy_name
                                )
            return True

    def add_to_proxies(self, proxies, exclude_rules):
        """add proxies to rule's proxies"""
        for proxy in proxies:
            if proxy["name"] not in self.proxies_name and not match_pattern_list(
                exclude_rules, proxy["name"]
            ):
                self.proxies_name.append(proxy["name"])
                self.rule_content["proxies"].append(proxy)
            else:
                logging.info(f"skip proxy: {proxy['name']}")
                print(f"skip proxy: {proxy['name']}")

    def generate_config(self):
        logging.debug(f"generating config for rule: {self.name}")
        res = ""
        try:
            res = yaml.dump(self.rule_content)
        except Exception as e:
            logging.error(f"error to dump rule to string with {e}")
        return res


#     @staticmethod
#     def check(rule_path):
#         try:
#             with open(rule_path, "r") as rule_file:
#                 load_config = yaml.safe_load(rule_file)
#         except Exception as e:
#             logging.error(f"error to parse rule file: {rule_path}")
#             logging.debug(f"error: {e}")
#             return False
#         finally:
#             return True


class Rules(object):
    def __init__(self, output_path=None, subscribers=None, rules=None):
        logging.debug(
            f"inviting rules with output_path: {output_path} and subscribers: {subscribers} and rules: {rules}"
        )
        self.rules = rules if rules is not None else []
        self.subscribers = subscribers if subscribers is not None else []
        self.output_path = (
            os.path.abspath(output_path)
            if output_path is not None
            else os.path.abspath(__file__)
        )
        logging.debug(
            f"inited rules with output_path: {self.output_path} and subscribers: {self.subscribers} and rules {self.rules}"
        )

    def get_rule_names(self):
        return [rule.name for rule in self.rules]

    def append_with_path(self, rule_path):
        logging.debug(f"append rule with path: {rule_path}")
        rule_ = Rule(rule_path=rule_path)
        self.rules.append(rule_)

    def append(self, rule_):
        logging.debug(f"append rule: {rule_.name}")
        self.rules.append(rule_)

    def set_subscribers(self, subscribers):
        logging.debug(
            f"set subscribers with {len(subscribers.subscribers.keys())} for rules"
        )
        self.subscribers = subscribers

    def update_proxies(self):
        self.subscribers.update_proxies()

    def generate_config(self, rule_id):
        rule_name = self.rules[rule_id].name
        for subscriber in self.subscribers.subscribers.values():
            sub_tags = subscriber.get_tags(rule_name)
            if len(sub_tags) > 0:
                # tags.append(sub_tags)
                # if the subscriber have tag for the rule, add it
                self.rules[rule_id].add_to_proxies(
                    subscriber.proxies, subscriber.exclude_rules
                )
                for tag in sub_tags:
                    self.rules[rule_id].add_to_proxies_groups(
                        tag, subscriber.proxies_name, subscriber.exclude_rules
                    )

        logging.info(f"generate config for {rule_name}.......")
        config_output = self.rules[rule_id].generate_config()
        if len(config_output) > 0:
            output_path = os.path.join(self.output_path, rule_name + "_gen.yaml")
            logging.info(f"saving generate config to {output_path}")
            with open(output_path, "w") as output_file:
                output_file.write(config_output)

    def generate_configs(self):
        self.update_proxies()

        logging.debug(f"generating configs for {len(self.rules)} rules")
        for rule_id in range(len(self.rules)):
            self.generate_config(rule_id)
