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
                        tag_str = tag_str + "," + k
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

    def doc_entry(self, conn_name):
        self.es_client.set_index(conn_name)
        records = self.get_all_records()
        nodes = self.get_nodes(records)
        edges = self.proc_edges(self.get_edges(self.get_tags_array(records)))
        j = dict()
        j['nodes'] = nodes
        j['edges'] = edges
        return j

    def get_tag_dict(self):
        record_array = self.get_all_records()
        tag_dict = dict()
        i = 1
        for record in record_array:
            tag = record['_source']['tags'].split(',') + record['_source']['automated_tags'].split(',')
            tag.pop(0)
            for t in tag:
                if t not in tag_dict.keys():
                    tag_dict[t] = record['_id']
                else:
                    docs = tag_dict[t]
                    tag_dict[t] = docs+"$$"+record['_id']
        return tag_dict

    def process_tag_dict(self, tag_dict):
        nodes_list = []
        nodes = dict()
        edges = []
        i = 1
        k = 1
        for key in tag_dict:
            if key not in nodes:
                nodes[key] = i
                from_id = i
                j = dict()
                j['id'] = i
                j['label'] = key
                nodes_list.append({"id": nodes[key], "label": key})
                i = i+1
            doc_list = tag_dict[key].split("$$")
            if len(doc_list) == 1:
                if doc_list[0] not in nodes:
                    nodes[doc_list[0]] = i
                    to_id = i
                    j = dict()
                    j['id'] = i
                    j['label'] = doc_list[0]
                    nodes_list.append(j)
                    i = i+1
                else:
                    to_id = nodes[doc_list[0]]
                j = dict()
                j['id'] = k
                j['from'] = from_id
                j['to'] = to_id
                j['label'] = ''
                edges.append(j)
                k = k+1
            else:
                for doc in doc_list:
                    if doc not in nodes:
                        nodes[doc] = i
                        to_id = i
                        j = dict()
                        j['id'] = i
                        j['label'] = doc
                        nodes_list.append(j)
                        i = i + 1
                    else:
                        to_id = nodes[doc]
                    j = dict()
                    j['id'] = k
                    j['from'] = from_id
                    j['to'] = to_id
                    j['label'] = ''
                    edges.append(j)
                    k = k + 1
        j = dict()
        j['nodes'] = nodes_list
        j['edges'] = edges
        return j

    def tag_entry(self, conn_name):
        print(conn_name)
        self.es_client.set_index(conn_name)
        tag_dict = self.get_tag_dict()
        return self.process_tag_dict(tag_dict)
