import copy

import pydot
import networkx as nx
from ltlf2dfa.parser.ltlf import LTLfParser
import matplotlib.pyplot as plt
import matplotlib.animation

from PIL import Image
from io import BytesIO


def parse_mtlf_to_ltlf(ltlf_formula, connector='&', add_eventually=True):
    while '$' in ltlf_formula:
        index = ltlf_formula.find('$')
        next_left_bracket = index + ltlf_formula[index:].find('[')
        next_right_bracket = index + ltlf_formula[index:].find(']')
        end = next_right_bracket
        duration = int(ltlf_formula[next_left_bracket+1:next_right_bracket])
        post_duration = ltlf_formula[next_right_bracket:]
        next_left_bracket = post_duration.find('[')
        next_right_bracket = post_duration[next_left_bracket:].find(']')
        end += next_right_bracket + next_left_bracket
        subpredicate = post_duration[next_left_bracket+1:next_right_bracket+1]
        if '$' in subpredicate:
            raise ValueError("Cannot nest $ operators")
        replacement = ''
        for i in range(duration):
            substr = subpredicate
            for _ in range(i):
                substr = f'X({substr})'
            replacement += substr
            if i != duration - 1:
                replacement += f' {connector} '
        if add_eventually:
            replacement = f'F({replacement})'
        else:
            replacement = f'({replacement})'
        ltlf_formula = ltlf_formula[:index] + \
            replacement + ltlf_formula[index+end+1:]
    return ltlf_formula


class LTLfDFA:
    ACCEPTING_PREFIX = " node [shape = doublecircle];"

    def __init__(self, ltlf_formula):
        ltlf_formula = parse_mtlf_to_ltlf(ltlf_formula)
        self._formula = ltlf_formula
        parser = LTLfParser()
        formula = parser(self._formula)
        self._pydot_str = formula.to_dfa()
        # the output is a list of one element
        dfa_pydot = pydot.graph_from_dot_data(self._pydot_str)[0]
        self._dfa = nx.nx_pydot.from_pydot(dfa_pydot)
        # the special state 'init' has exactly 1 edge that is an unconditional to the start state
        self._init_state = next(iter(self._dfa.out_edges('init')))[-1]
        self._current_state = self._init_state
        # set accepting states
        lines = self._pydot_str.split("\n")
        for line in lines:
            if not line.startswith(LTLfDFA.ACCEPTING_PREFIX):
                continue
            substr = line[len(LTLfDFA.ACCEPTING_PREFIX):]
            accepting_nodes = substr.split(";")
            for node in accepting_nodes:
                node = node.strip()
                if len(node) > 0:
                    self._dfa.nodes[node.strip()]['accepting'] = True
        for node in self._dfa.nodes:
            if 'accepting' not in self._dfa.nodes[node]:
                self._dfa.nodes[node]['accepting'] = False
        # convert edge labels to python expressions
        for u, v, a in self._dfa.edges(data=True):
            if 'label' in a:
                # all labels are wrapped in double quotes
                a['label'] = a['label'][1:-1]
                a['orig_label'] = a['label']
                a['label'] = a['label'].replace("&", " and ")  # replace and
                a['label'] = a['label'].replace("|", " or ")  # replace or
                a['label'] = a['label'].replace("~", " not ")  # replace not
                a['label'] = a['label'].replace("true", "True")  # Python True casing

    def step(self, data, return_state=False):
        self._current_state = self._compute_next_state(
            self._current_state, data)
        if return_state:
            return self._dfa.nodes[self._current_state]['accepting'], self._current_state
        else:
            return self._dfa.nodes[self._current_state]['accepting']

    def _compute_next_state(self, current_state, data_dict):
        valid_states = []
        for u, v, a in self._dfa.out_edges(current_state, data=True):
            if eval(a['label'], dict(data_dict)):
                valid_states.append(v)
        if len(valid_states) != 1:
            raise ValueError(
                f"Unable to find state transition from {u} with {data_dict}, aborting.")
        return valid_states[0]

    def from_init(self, data, return_state=False):
        current_state = self._init_state
        data_key = next(iter(data))
        ret_val = []
        time_steps = len(data[data_key])
        for i in range(time_steps):
            data_dict = {var: data[var][i][-1] for var in data}
            current_state = self._compute_next_state(current_state, data_dict)
            if return_state:
                ret_val.append(
                    (self._dfa.nodes[current_state]['accepting'], current_state))
            else:
                ret_val.append(self._dfa.nodes[current_state]['accepting'])
        return ret_val

    def save_image(self, file_name, cur_node=None, color=False):
        if file_name.endswith('svg'):
            sg_img = self.get_pydot_image(cur_node=cur_node, color=color, svg=True)
            with open(file_name, 'wb') as f:
                f.write(sg_img)
        else:
            sg_img = self.get_pydot_image(cur_node=cur_node, color=color)
            sg_img.save(file_name)

    def get_pydot_image(self, cur_node=None, color=True, svg=False):
        graph_copy = copy.deepcopy(self._dfa)
        graph_copy.graph['size'] = (100, 100)
        for node in graph_copy.nodes:
            node_props = graph_copy.nodes[node]
            del node_props['accepting']
            node_props['height'] = 2.5
            node_props['fontsize'] = 50
            node_props['fontname'] = 'times bold'
            if color:
                if node == 'init' or node == '\\n':
                    node_color = 'invis'
                else:
                    node_color = 'green' if self._dfa.nodes[node]['accepting'] else 'red'
                node_props['shape'] = 'circle'
                node_props['color'] = 'black' if cur_node == node else node_color
                node_props['penwidth'] = 20 if cur_node == node else 3
                node_props['fillcolor'] = node_color
                node_props['style'] = 'filled'
            else:
                node_props['shape'] = 'doublecircle' if self._dfa.nodes[node]['accepting'] else 'circle'
                if node == 'init':
                    node_props['fillcolor'] = 'invis'
                    node_props['style'] = 'invis'
                else:
                    node_props['fillcolor'] = 'grey80' if node == cur_node else 'white'
                    node_props['style'] = 'filled'
        if svg:
            return nx.nx_pydot.to_pydot(graph_copy).create_svg()
        else:
            sg_img = nx.nx_pydot.to_pydot(graph_copy).create_png()
            return Image.open(BytesIO(sg_img))

    def animate(self, steps, mp4_file, fps=20):
        fig, ax = plt.subplots()
        ax.axis('off')

        def handle_current_state(index):
            cur_node = steps[index]
            ax.clear()
            sg_img = self.get_pydot_image(cur_node, color=False)
            ax.imshow(sg_img)
            ax.set_title(f'Time: {index} State: {cur_node}, Holds: {self._dfa.nodes[cur_node]["accepting"]}')
            ax.axis('off')

        ani = matplotlib.animation.FuncAnimation(fig, handle_current_state, frames=len(steps), repeat=False)

        writer = matplotlib.animation.FFMpegFileWriter(fps=fps, codec="mpeg4")
        ani.save(mp4_file, writer=writer)
