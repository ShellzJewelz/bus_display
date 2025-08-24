import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from defines import BUS_GOV_LANGUAGE_HEBREW, BUS_GOV_LANGUAGE_ENGLISH

CONFIG_FILE_NAME = "/etc/bus_display/busfilter.yaml"

def getBusFilterConfig() -> dict[int, list[str]]:
    busStopsConfig = None

    try:
        with open(CONFIG_FILE_NAME, "r") as f:
            busStopsConfig = yaml.load(f, Loader)
    except yaml.YAMLError as exc:
        print(f"Syntax error in {0} file: {exc}", CONFIG_FILE_NAME)

    config = []

    try:
        if busStopsConfig["Language"].upper() == "HEBREW":
            config.append(BUS_GOV_LANGUAGE_HEBREW)
        elif busStopsConfig["Language"].upper() == "ENGLISH":
            config.append(BUS_GOV_LANGUAGE_ENGLISH)
        else:
            print("Unsupported language")
            return None
    except (KeyError, AttributeError):
        print("No language specified")
        return None

    try:
        for busStop in busStopsConfig["BusStops"]:
            stopFilters = {}
            for filter_ in busStop["Filters"]:
                stopFilters[int(filter_["Operator"])] = str(filter_["Lines"]).replace(" ", "").split(",")
            config.append([int(busStop["StopCode"]), stopFilters])
    except KeyError as exc:
        print(f"YAML format error, expected {exc} but not found")
        return None

    return config
