from LTLfDFA import LTLfDFA
from functools import partial

from PIL import Image
from io import BytesIO
import networkx as nx


class Property:
    def __init__(self, property_name, property_string, predicates):
        self.name = property_name
        self.ltldfa = LTLfDFA(property_string)
        self.data = {}
        self.predicates = {}
        for a, b in predicates:
            self.data[a] = []
            self.predicates[a] = b

    def update_data(self, sg, save_usage_information=False):
        sg.graph[f'save_usage_information_{self.name}'] = save_usage_information
        if save_usage_information:
            sg.graph[f'usage_information_{self.name}'] = []
        for atomic_predicate, sg_predicate in self.predicates.items():
            self.data[atomic_predicate].append((
                len(self.data[atomic_predicate]),
                self.__evaluate_predicate(sg_predicate, sg)
            ))

    def save_relevant_subgraph(self, sg, file_name):
        svg = file_name is not None and file_name.endswith('svg')
        if not sg.graph[f'save_usage_information_{self.name}']:
            raise ValueError("Cannot save relevant subgraph without save_usage_information set and calling update_data before this.")
        all_nodes = set()
        for data_dict in sg.graph[f'usage_information_{self.name}']:
            func_name = data_dict['func']  # TODO: filter only by those used in comparison expressions?
            data = data_dict['data']
            # print(func_name, data)
            all_nodes.update(data)
        all_nodes.update([node for node in sg.nodes if node.name == 'ego'])
        # print(all_nodes)
        graph_copy = nx.induced_subgraph(sg, all_nodes)
        # graph_copy = copy.deepcopy(sg)
        # graph_copy = nx.induced_subgraph(graph_copy, all_nodes)
        # graph_copy.graph['size'] = (100, 100)
        if svg:
            img = nx.nx_pydot.to_pydot(graph_copy).create_svg()
            with open(file_name, 'wb') as f:
                f.write(img)
        else:
            img = nx.nx_pydot.to_pydot(graph_copy).create_png()
            img = Image.open(BytesIO(img))
            if file_name is None:
                return img
            else:
                img.save(file_name)

    def check_from_init(self):
        return self.ltldfa.from_init(self.data, return_state=False)

    def check_step(self, return_state=False):
        acc, state = self.ltldfa.step(self.get_last_predicates(), return_state=True)
        if return_state:
            return acc, state
        return acc

    def get_last_predicates(self):
        result = {}
        for key, val in self.data.items():
            result[key] = val[-1][1]
        return result

    def __evaluate_predicate(self, predicate, sg, func_chain=None):
        if func_chain is None:
            func_chain = ''
        func_chain += '.' + predicate.func.__name__
        param_list = []
        for arg in predicate.args:
            if isinstance(arg, partial):
                param_list.append(self.__evaluate_predicate(arg, sg, func_chain=func_chain))
            else:
                param_list.append(arg)
        if sg.graph[f'save_usage_information_{self.name}']:
            data = set()
            for param in param_list:
                if type(param) == set:
                    data.update(param)
            sg.graph[f'usage_information_{self.name}'].append({
                    'func': func_chain,
                    'data': data
                })
        if predicate.func.__name__ in ['filterByAttr', 'relSet']:
            return predicate.func(*param_list, sg, **predicate.keywords)
        else:
            return predicate.func(*param_list, **predicate.keywords)
