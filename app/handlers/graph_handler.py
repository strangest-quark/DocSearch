from client.elastic_search_client import ES_Client
from config.config import Config


class GraphHandler:

    def __init__(self, config: Config):
        self.es_client = ES_Client(config)

    def get_all_records(self):
        return self.es_client.match_all()

    def get_nodes(self, record_array):
        nodes = []
        i = 1
        for record in record_array:
            j = dict()
            j['id'] = i
            j['label'] = record['_id']
            i = i + 1
            nodes.append(j)
        return nodes

    def get_tags_array(self, record_array):
        tags = []
        for record in record_array:
            tag = record['_source']['tags'].split(',') + record['_source']['automated_tags'].split(',')
            tag.pop(0)
            tags.append(tag)
        return tags

    def get_edges(self, tags):
        edges = []
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                set1 = set(tags[i])
                set2 = set(tags[j])
                set3 = set1 & set2
                if bool(set3):
                    edge = [i + 1, j + 1]
                    tag_str = ""
                    for k in set3:
                        tag_str = tag_str + "," +k
                    edge.append(tag_str[1:])
                    edges.append(edge)
        return edges

    def proc_edges(self, edges):
        ed = []
        i = 1
        for edge in edges:
            j = dict()
            j['id'] = i
            j['from'] = edge[0]
            j['to'] = edge[1]
            j['label'] = edge[2]
            ed.append(j)
            i = i + 1
        return ed

    def entry(self, conn_name):
        self.es_client.set_index(conn_name)
        nodes = self.get_nodes(self.get_all_records())
        edges = self.proc_edges(self.get_edges(self.get_tags_array(self.get_all_records())))
        j = dict()
        j['nodes'] = nodes
        j['edges'] = edges
        return j
