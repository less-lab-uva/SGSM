import os
import pandas as pd
import pickle
import SG_Primitives as P
import SG_Utils as utils
import Property
# from properties import phi1, phi2, phi3, phi4, phi5, phi6, phi7, phi8, phi9
from properties import all_properties
from time import time
from PIL import Image
from functools import partial
from pathlib import Path


class Monitor:
    def __new__(cls, *args, **kwargs):
        if (len(args) > 0 or len(kwargs) > 0) and hasattr(cls,
                                                          'monitor_instance'):
            del cls.monitor_instance

        if not hasattr(cls, 'monitor_instance'):
            cls.monitor_instance = super(Monitor, cls).__new__(cls)
            cls.monitor_instance.initialize(*args, **kwargs)
        return cls.monitor_instance

    def initialize(
            self, log_path, route_path,
            save_sg=False):
        # self.properties = [phi1, phi2, phi3, phi4, phi5, phi6, phi7, phi8,
        #                    phi9]
        self.properties = all_properties
        self.timestep = 0
        self.save_sg = save_sg

        # Create log directory
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        # Create route directory
        self.route_path = self.log_path / route_path
        self.route_path.mkdir(parents=True, exist_ok=True)
        # # Create rsv directory
        # self.rsv_path = self.route_path / "rsv"
        # self.rsv_path.mkdir(parents=True, exist_ok=True)
        # # Create image directory
        # self.img_path = self.route_path / "images"
        # self.img_path.mkdir(parents=True, exist_ok=True)

    def add_property(self, property):
        self.properties.append(property)

    def get_property(self, name):
        ret = [prop for prop in self.properties if prop.name == name]
        if len(ret) == 0:
            return None
        return ret[0]

    def save_all_relevant_subgraphs(self, sg, sg_name):
        save_dir = self.route_path / sg_name
        save_dir.mkdir(parents=True, exist_ok=True)
        for prop in self.properties:
            prop.save_relevant_subgraph(sg, str(save_dir/f'{prop.name}.png'))

    def get_all_relevant_subgraphs(self, sg):
        return {prop.name: prop.save_relevant_subgraph(sg, None) for prop in self.properties}

    def check(self, sg, save_usage_information=False):
        # Save sg
        if self.save_sg:
            self.save_rsv(sg)

        # Check property
        for i, prop in enumerate(self.properties):
            # Update property data
            prop.update_data(sg, save_usage_information=save_usage_information)
            # Check property
            # start = time()
            prop_eval, state = prop.check_step(return_state=True)
            if save_usage_information:
                sg.graph[f'state_{prop.name}'] = state
                sg.graph[f'acc_{prop.name}'] = prop_eval
            pred_eval = prop.get_last_predicates()
            # end = time()
            # print(
            #     f"Property {prop.name} evaluated in {end-start:.2f}",
            #     f"seconds: {prop_eval}")
            self.log(prop_name=prop.name,
                     pred_eval=pred_eval, prop_eval=prop_eval)

        self.timestep += 1

    def save_rsv(self, rsv):
        # Save pkl file
        with open(self.rsv_path / f"{self.timestep}.pkl", 'wb') as f:
            pickle.dump(rsv, f)

    def save_images(self, images):
        for i, image in enumerate(images):
            pil_img = Image.fromarray(image)
            pil_img.save(self.img_path / f"ts_{self.timestep}_img_{i}.jpg")

    def log(self, prop_name, pred_eval, prop_eval):
        csv_path = self.route_path / f"{prop_name}.csv"
        keys = ["ts"]
        keys.extend(list(pred_eval.keys()))
        keys.append("prop_eval")
        values = [self.timestep]
        values.extend(list(pred_eval.values()))
        values.append(prop_eval)
        if self.timestep > 0:
            # Load csv file
            df = pd.read_csv(csv_path)
            df.loc[len(df)] = values
            df.to_csv(csv_path, index=False)
        else:
            # Create new csv file
            df = pd.DataFrame(columns=keys)
            df.loc[0] = values
            df.to_csv(csv_path, index=False)


def main():
    # # Property 1
    # a = partial(
    #     P.filterByAttr, partial(P.relSet, "Ego", "isIn"),
    #     "name", "Opposing Lane")
    # # a = partial(P.filterByAttr, partial(
    # #     P.relSet, "Ego", "isIn"), "name", "Ego Lane")
    # a = partial(P.gt, partial(P.size, a), 0)
    # phi1 = Property("phi1", "G(~a)", [("a", a)])

    # # # Property 2
    # # a = partial(P.relSet, partial(P.filterByAttr, "G",
    # #             "name", "Root Lane", edge_type="incoming"))
    # # a = partial(P.difference, a, partial(P.relSet, "Ego", "isIn"))
    # # a = partial(P.filterByAttr, a, "name", "Right*")
    # # a = partial(P.eq, partial(P.size, a), 0)

    # # s = partial(getattr, __name="Steering")
    # # s = partial(P.gt, s, 0)
    # # phi2 = Property("G(a -> s)", [("a", a), ("s", s)])

    # m = Monitor(log_path="./monitor_log/")
    # m.add_property(phi1)
    # # m.add_property(phi2)

    # base_path = Path("./rsv_sg_town04_max_car/")
    # sg_name_list = sorted(os.listdir(base_path))
    # for sg_name in sg_name_list[:10]:
    #     sg = utils.load_sg(base_path / sg_name)
    #     m.check(sg)

    m = Monitor()


if __name__ == '__main__':
    main()
