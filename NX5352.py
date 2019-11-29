import re
import os
import requests
from lxml import etree
from bs4 import BeautifulSoup 
from collections import defaultdict

class NX5352:

    def __init__(self, data_path):
        pass

    def get_all_files(self, dir_name = "data", file_name = "Tags.xml"):
        d = {}
        j = os.walk(dir_name)
        for i in j:
            if i[0].endswith(".com") and file_name in i[-1]:
                domain_name = os.path.split(i[0])[-1].split(".")[0]
                d[domain_name] = os.path.join(i[0], file_name)

        return d


    def get_domains_per_user(self):

        users_count = defaultdict(int)
        users = dict()

        d = self.get_all_files(dir_name = "data", file_name = "Users.xml")
        for i in d:
            t = self.get_xml_generator(d[i])
            for ev, el in t:
                t_u = el.attrib
                
                if "AccountId" not in t_u or int(t_u["AccountId"]) == -1:
                    continue

                # this seems faster than checking for the key
                try:
                    _ = users[int(t_u["AccountId"])]
                except KeyError:
                    users[int(t_u["AccountId"])] = list()

                users[int(t_u["AccountId"])].append(i)
                users_count[int(t_u["AccountId"])] += 1
                el.clear()

        return users, users_count


    def get_users_per_domain(self):
        """
        returns: dict, where keys = domains and values = number of users
        """
        domains = defaultdict(int)
        d = self.get_all_files(dir_name = "data", file_name = "Users.xml")
        for i in d:
            t = self.get_xml_generator(d[i])
            for ev, el in t:
                t_d = el.attrib

                if "AccountId" not in t_d or int(t_d["AccountId"]) == -1:
                    continue

                domains[i] += 1
                el.clear()

        return domains


    def get_user_domain_participation_edgelist(self, user_map, user_domain_count):
        # user_domain_count is the users_count dictionary from get_domain_per_users

        edgelist = set()

        d = self.get_all_files(dir_name = "data", file_name = "Posts.xml")

        for i in d:
            t = self.get_xml_generator(d[i], html = True)
            for ev, el in t:
                t_d = el.attrib

                if "owneruserid" not in t_d or int(t_d["owneruserid"]) == -1:
                    continue

                if user_domain_count[user_map[i][int(t_d["owneruserid"])]] > 1:
                    # ignore if participant is only in one domain
                    edgelist.add((user_map[i][int(t_d["owneruserid"])], i))

                el.clear()

        return list(edgelist)


    def get_user_map(self):
        user_map = {}
        d = self.get_all_files(dir_name = "data", file_name = "Users.xml")
        for i in d:
            t = self.get_xml_generator(d[i])
            user_map[i] = {}
            for ev, el in t:
                t_d = el.attrib

                if "AccountId" not in t_d or int(t_d["AccountId"]) == -1:
                    continue
                user_map[i][int(t_d["Id"])] = int(t_d["AccountId"])
                el.clear()
        
        return user_map


    def get_xml_generator(self, file_path, tag_name = "row", html = False):
        z = etree.iterparse(file_path, tag = tag_name, encoding = "utf-8", html = html)
        return z


    def get_all_sites(self):
        r = requests.get("https://data.stackexchange.com/")
        s = BeautifulSoup(r.text, "lxml")
        fields_soup = s.find_all("h2", class_ = "title")
        fields = {i.a["href"].split("/")[0]: i.a.getText() for i in fields_soup if "Meta" not in i.a.getText()}
        del fields_soup, s, r

        return fields





