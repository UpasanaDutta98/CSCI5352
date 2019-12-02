import re
import os
import requests
from lxml import etree
from bs4 import BeautifulSoup 
import networkx as nx
from collections import defaultdict

class NX5352:

    def __init__(self, data_path):
        pass # TODO

    def get_domains_per_user(self):
        """
        users: dict, where keys = StackExchange ID and values = list of domains user is in
        users_count: dict, where keys = StackExchange ID and values = number of domains user is in
        """
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
        returns: dict, where keys = domains and values = NUMBER of users
        """

        # TODO: list of users in values 

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
        # TODO: weighted edgelist! # participation in domain

        # user_domain_count is the users_count dictionary from get_domain_per_users

        edgelist = set() # misleading name: sorry about that
        nodelist = list()

        d = self.get_all_files(dir_name = "data", file_name = "Posts.xml")

        # make a nested list of domains (to allow bipartite graph formation)
        # utilized in get_nx_bipartite()
        tmp = [i for i in d]
        nodelist.append(tmp)
        del tmp

        tmp = set() # now add all other nodes here
        for i in d:
            t = self.get_xml_generator(d[i], html = True)
            for ev, el in t:
                t_d = el.attrib

                if "owneruserid" not in t_d or int(t_d["owneruserid"]) == -1:
                    continue

                se_id = user_map[i][int(t_d["owneruserid"])]
                if user_domain_count[se_id] > 1:
                    # ignore if participant is only in one domain
                    edgelist.add((se_id, i))
                    tmp.add(se_id)

                el.clear()

        nodelist.append(list(tmp))
        del tmp, t

        return list(edgelist), nodelist



    def get_tag_domain_participation_edgelist(self, tag_map, tag_domain_count):
        raise NotImplementedError



    def get_user_domain_activity(self, user_map):
        raise NotImplementedError




    '''
    UTILITIES
    =========
    Some necessary, others not so necessary :|
    '''

    def get_user_map(self):
        '''
        1. Map the domain userID of every user to global stackexchange ID
        2. returns dictionary: user_map[domain_name (str)][domain_user_id] = stackexchange_id
        '''
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



    def get_tag_map(self):
        # TODO!
        raise NotImplementedError



    def get_xml_generator(self, file_path, tag_name = "row", html = False):
        '''
        utility function to get generator for iterative parsing. does not overload memory.
        '''
        z = etree.iterparse(file_path, tag = tag_name, encoding = "utf-8", html = html)
        return z



    def get_nx_bipartite(self, edgelist, nodelist, directed = False):
        '''
        WARNING: Not multipartite
        nodelist contains nested lists. 
        each nested list represents one class of bipartite graph.
        TODO: not considering directed at the moment
        '''

        G = nx.Graph()
        G.add_nodes_from(nodelist[0], bipartite = 0)
        G.add_nodes_from(nodelist[1], bipartite = 1)
        G.add_edges_from(edgelist)

        return G



    def get_all_sites(self):
        r = requests.get("https://data.stackexchange.com/")
        s = BeautifulSoup(r.text, "lxml")
        fields_soup = s.find_all("h2", class_ = "title")
        fields = {i.a["href"].split("/")[0]: i.a.getText() for i in fields_soup if "Meta" not in i.a.getText()}
        del fields_soup, s, r

        return fields



    def get_all_files(self, dir_name = "data", file_name = "Tags.xml"):
        '''
        returns: dict, key = domain_name (str) and value = relative_path of data folder for domain
        '''
        d = {}
        j = os.walk(dir_name)
        for i in j:
            if i[0].endswith(".com") and file_name in i[-1]:
                domain_name = os.path.split(i[0])[-1].split(".")[0]
                d[domain_name] = os.path.join(i[0], file_name)

        return d





