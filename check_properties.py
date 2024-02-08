import argparse
import os
import re
import time
from multiprocessing import Pool

from tqdm import tqdm
import SG_Utils as utils
from Monitor import Monitor
from pathlib import Path


def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)',
                                      text)]


def check_directory(dir_to_check, save_folder, threaded=False):
    m = Monitor(log_path=save_folder, route_path=dir_to_check.name)
    rsv_folder = dir_to_check/'rsv'
    sg_name_list = [p for p in os.listdir(rsv_folder) if p.endswith(".pkl")]
    sg_name_list = sorted(sg_name_list, key=natural_keys)
    # # Get 1 sg every 10 frames (2Hz)
    # if sut == 'InterFuser' or sut == 'TCP':
    #     if sut == 'TCP' and dir_to_check.name == 'done_RouteScenario_24':
    #         pass
    #     else:
    #         sg_name_list = [p for i, p in enumerate(sg_name_list) if i % 10 == 0]
    print(f"{str(dir_to_check)}: Checking {len(sg_name_list)} files")
    start = time.time()
    for sg_name in tqdm(sg_name_list, disable=threaded):
        sg = utils.load_sg(str(rsv_folder / sg_name))
        m.check(sg, save_usage_information=True)
        # m.save_all_relevant_subgraphs(sg, sg_name.replace('.pkl', ''))

    end = time.time()
    print(f"{str(dir_to_check)} | Checked {len(sg_name_list)} SGs | Total time taken: {end - start:.2f} seconds | Average time per SG: {(end - start) / len(sg_name_list):.2f} seconds")


def main():
    parser = argparse.ArgumentParser(prog='Property checker')
    parser.add_argument('-f', '--folder_to_check', type=Path)
    parser.add_argument('-s', '--save_folder', type=Path, default='default/')
    args = parser.parse_args()

    dirs = [p for p in args.folder_to_check.iterdir()]
    if len(dirs) > 1:
        results = []
        with Pool(len(dirs)) as p:
            for d in dirs:
                if d.name.startswith("done_RouteScenario_"):
                    results.append(p.apply_async(check_directory, (d, args.save_folder, True)))
            for r in results:
                r.wait()
    else:
        check_directory(args.system_under_test, dirs[0], args.save_folder, False)


if __name__ == "__main__":
    main()
