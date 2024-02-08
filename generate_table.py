import argparse
import pandas as pd
from pathlib import Path
from properties import all_properties


def main():
    parser = argparse.ArgumentParser(prog='Property checker')
    parser.add_argument('-bf', '--base_folder', type=Path)
    parser.add_argument('-of', '--output_folder', type=Path)
    args = parser.parse_args()
    SUTS = ["Interfuser", "TCP", "LAV"]
    ROUTES = list(range(16, 26, 1))
    PROPERTIES = [prop.name for prop in all_properties]
    
    # Sum of property violations accross all routes
    summary = pd.DataFrame(columns=["SUT", *PROPERTIES, "Total"])
    route_with_most_violations = (16, 0)

    args.output_folder.mkdir(parents=True, exist_ok=True)

    for route in ROUTES:
        n_violations = 0
        # Property violations per route
        results = pd.DataFrame(columns=["SUT", *PROPERTIES])
        for sut in SUTS:
            row = {"SUT": sut}
            # Initialize all properties with no violations
            for prop in PROPERTIES:
                row[prop] = 0
            properties_path = args.base_folder / f"{sut}_results/done_RouteScenario_{route}/"
            if properties_path.exists():
                for file in properties_path.iterdir():
                    if file.name.endswith(".csv"):
                        name = file.name.split(".csv")[0]
                        df = pd.read_csv(file)
                        q = df[df['prop_eval'] == False]
                        # Check for violations
                        if len(q) > 0:
                            row[name] = 1
                            # TODO: add time
                            time = q.iloc[0]['ts']

            r = pd.DataFrame(columns=["SUT", *PROPERTIES], data=[row])
            n_violations += r.iloc[:, 1:].sum(axis=1)[0]
            results = pd.concat([results, r])

        results["Total"] = results.iloc[:, 1:].sum(axis=1)
        results.loc['Total', :] = results.sum(axis=0)
        results.to_csv(args.output_folder / f"RouteScenario_{route}.csv", index=False)
        if n_violations > route_with_most_violations[1]:
            route_with_most_violations = (route, n_violations)

        if len(summary) == 0:
            summary = results
        else:
            summary.iloc[:, 1:] += results.iloc[:, 1:]

    summary.to_csv(args.output_folder / "summary.csv", index=False)
    print(f"Route {route_with_most_violations[0]} has the most violations: {route_with_most_violations[1]}")
    print(summary.to_latex(index=False))


if __name__ == "__main__":
    main()
