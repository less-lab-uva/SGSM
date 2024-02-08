import SG_Primitives as P
from Property import Property
from functools import partial

# Set predicates
EGO = partial(P.filterByAttr, "G", "name", "ego")
EGO_LANES = partial(P.relSet, "Ego", "isIn")
EGO_ROADS = partial(P.relSet, EGO_LANES, "isIn")
EGO_JUNTIONS = partial(P.relSet, EGO_ROADS, "isIn")
OPPOSING_LANES = partial(P.relSet, EGO_LANES, "opposes")
ENTITIES_IN_EGO_LANE = partial(P.difference, partial(
    P.relSet, EGO_LANES, "isIn", edge_type="incoming"), EGO)
TRAFFIC_LIGHT_LANES_FOR_EGO = partial(
    P.intersection,
    partial(
        P.relSet, partial(P.filterByAttr, "G", "name", "traffic_light*"),
        "controlsTrafficOf"),
    EGO_LANES)
TRAFFIC_LIGHT_FOR_EGO = partial(
    P.relSet, TRAFFIC_LIGHT_LANES_FOR_EGO, "controlsTrafficOf",
    edge_type="incoming")
RED_TRAFFIC_LIGHT_FOR_EGO = partial(P.filterByAttr, TRAFFIC_LIGHT_FOR_EGO,
                                    "light_state", "Red")
STOP_SIGN_FOR_EGO = partial(P.intersection, partial(P.relSet, partial(
    P.filterByAttr, "G", "name", "stop_sign*"), "controlsTrafficOf"),
    EGO_LANES)

# Boolean predicates
IS_IN_JUNCTION = partial(partial(P.gt, partial(P.size, EGO_JUNTIONS), 0))
# IS_STOPPED = partial(P.eq, partial(P.size, partial(
#     P.filterByAttr, "Ego", "carla_speed", (lambda a: P.eq(a, b=0)))), 1)
IS_STOPPED = partial(P.eq, partial(P.size, partial(
    # P.filterByAttr, "Ego", "carla_speed", (lambda a: P.le(a, b=1e-4)))), 1)
    P.filterByAttr, "Ego", "carla_speed", (lambda a: P.le(a, b=0)))), 1)
ARE_RED_TRAFFIC_LIGHT_FOR_EGO = partial(
    P.gt, partial(P.size, RED_TRAFFIC_LIGHT_FOR_EGO), 0)
ARE_STOP_SIGNS_FOR_EGO = partial(
    P.gt, partial(P.size, STOP_SIGN_FOR_EGO), 0)

##################
### Properties ###
##################

# Property 1

EGO_IS_IN_OPPOSING_LANE = partial(P.gt, partial(
    P.size, partial(P.intersection, EGO_LANES, OPPOSING_LANES)), 0)
phi1 = Property("Phi1", "G(~ego_is_in_opposing_lane)",
                [("ego_is_in_opposing_lane", EGO_IS_IN_OPPOSING_LANE)])

# Property 2

EGO_IS_OUT_OF_ROAD = partial(P.gt, partial(P.size, partial(
    P.filterByAttr, EGO_LANES, "name", "Off Road")), 0)
phi2 = Property(
    "Phi2", "G(~ego_is_out_of_road)",
    [("ego_is_out_of_road", EGO_IS_OUT_OF_ROAD)])

# Property 3

IS_IN_RIGHT_MOST_LANE = partial(P.eq, partial(
    P.size, partial(P.relSet, EGO_LANES, 'toRightOf', edge_type="incoming")), 0)
IS_NOT_STEERING_RIGHT = partial(
    P.eq,
    partial(
        P.size,
        partial(
            P.filterByAttr, "Ego", "ego_control_carla_steer",
            (lambda a: P.lt(a, b=0)))),
    1)
phi3 = Property(
    "Phi3",
    "G(is_in_right_most_lane & ~is_in_junction -> is_not_steering_right)",
    [("is_in_right_most_lane", IS_IN_RIGHT_MOST_LANE),
     ("is_in_junction", IS_IN_JUNCTION),
     ("is_not_steering_right", IS_NOT_STEERING_RIGHT)])

# Property 4 - S=5

S = 5  # PARAMETER S
ARE_ENTITIES_NEAR_COLL = partial(P.gt, partial(
    P.size, partial(P.relSet, ENTITIES_IN_EGO_LANE, "near_coll")), 0)
EGO_IS_FASTER_THAN_S = partial(P.eq, partial(P.size, partial(
    P.filterByAttr, "Ego", "carla_speed", (lambda a: P.gt(a, b=S)))), 1)
phi4_S_5 = Property(
    "Phi4_S_5", "G(are_entities_near_coll -> ~ego_is_faster_than_s)",
    [("are_entities_near_coll", ARE_ENTITIES_NEAR_COLL),
     ("ego_is_faster_than_s", EGO_IS_FASTER_THAN_S)])

# Property 4 - S=10

S = 10  # PARAMETER S
ARE_ENTITIES_NEAR_COLL = partial(P.gt, partial(
    P.size, partial(P.relSet, ENTITIES_IN_EGO_LANE, "near_coll")), 0)
EGO_IS_FASTER_THAN_S = partial(P.eq, partial(P.size, partial(
    P.filterByAttr, "Ego", "carla_speed", (lambda a: P.gt(a, b=S)))), 1)
phi4_S_10 = Property(
    "Phi4_S_10", "G(are_entities_near_coll -> ~ego_is_faster_than_s)",
    [("are_entities_near_coll", ARE_ENTITIES_NEAR_COLL),
     ("ego_is_faster_than_s", EGO_IS_FASTER_THAN_S)])

# Property 4 - S=15

S = 15  # PARAMETER S
ARE_ENTITIES_NEAR_COLL = partial(P.gt, partial(
    P.size, partial(P.relSet, ENTITIES_IN_EGO_LANE, "near_coll")), 0)
EGO_IS_FASTER_THAN_S = partial(P.eq, partial(P.size, partial(
    P.filterByAttr, "Ego", "carla_speed", (lambda a: P.gt(a, b=S)))), 1)
phi4_S_15 = Property(
    "Phi4_S_15", "G(are_entities_near_coll -> ~ego_is_faster_than_s)",
    [("are_entities_near_coll", ARE_ENTITIES_NEAR_COLL),
     ("ego_is_faster_than_s", EGO_IS_FASTER_THAN_S)])

# Property 5

ARE_ENTITIES_SUPER_NEAR = partial(P.gt, partial(
    P.size, partial(P.relSet, ENTITIES_IN_EGO_LANE, "super_near")), 0)
IS_THROTTLE_NOT_POSITIVE = partial(
    P.eq,
    partial(
        P.size,
        partial(
            P.filterByAttr, "Ego", "ego_control_carla_throttle",
            (lambda a: P.le(a, b=0.05)))),  # instead of checking exactly ~positive, we check <= a small value
    1)
phi5 = Property(
    "Phi5",
    "G(are_entities_super_near & ~are_entities_near_coll & X are_entities_near_coll -> X is_throttle_not_positive)",
    [("are_entities_super_near", ARE_ENTITIES_SUPER_NEAR),
     ("are_entities_near_coll", ARE_ENTITIES_NEAR_COLL),
     ("is_throttle_not_positive", IS_THROTTLE_NOT_POSITIVE)])

# Property 6

ARE_ENTITIES_WITHIN_7M = partial(
    P.logic_or, ARE_ENTITIES_NEAR_COLL, ARE_ENTITIES_SUPER_NEAR)
phi6 = Property(
    "Phi6",
    # "G(~are_entities_within_7m & ~are_red_traffic_lights_for_ego & ~are_stop_signs_for_ego -> ~is_stopped)",
    "G(~is_stopped & ~are_entities_within_7m & ~are_red_traffic_lights_for_ego & ~are_stop_signs_for_ego & X(~are_entities_within_7m & ~are_red_traffic_lights_for_ego & ~are_stop_signs_for_ego) -> X ~is_stopped)",
    [("are_entities_within_7m", ARE_ENTITIES_WITHIN_7M),
     ("are_red_traffic_lights_for_ego", ARE_RED_TRAFFIC_LIGHT_FOR_EGO),
     ("are_stop_signs_for_ego", ARE_STOP_SIGNS_FOR_EGO),
     ("is_stopped", IS_STOPPED)])

# Property 7 - T=5

T = 10  # PARAMETER T at 2Hz
IS_IN_MULTIPLE_LANES = partial(P.gt, partial(P.size, partial(EGO_LANES)), 1)
phi7_T_5 = Property(
    "Phi7_T_5",
    f"~ $[{T}][is_in_multiple_lanes & ~is_in_juntion]",
    [("is_in_multiple_lanes", IS_IN_MULTIPLE_LANES),
     ("is_in_juntion", IS_IN_JUNCTION)])

# Property 7 - T=10

T = 20  # PARAMETER T at 2Hz
IS_IN_MULTIPLE_LANES = partial(P.gt, partial(P.size, partial(EGO_LANES)), 1)
phi7_T_10 = Property(
    "Phi7_T_10",
    f"~ $[{T}][is_in_multiple_lanes & ~is_in_juntion]",
    [("is_in_multiple_lanes", IS_IN_MULTIPLE_LANES),
     ("is_in_juntion", IS_IN_JUNCTION)])

# Property 7 - T=15

T = 30  # PARAMETER T at 2Hz
IS_IN_MULTIPLE_LANES = partial(P.gt, partial(P.size, partial(EGO_LANES)), 1)
phi7_T_15 = Property(
    "Phi7_T_15",
    f"~ $[{T}][is_in_multiple_lanes & ~is_in_juntion]",
    [("is_in_multiple_lanes", IS_IN_MULTIPLE_LANES),
     ("is_in_juntion", IS_IN_JUNCTION)])

# Property 8 - T=5

T = 10  # PARAMETER T at 2Hz
IS_ONLY_IN_JUNCTION = partial(P.eq, partial(P.size, partial(
    P.difference, EGO_ROADS, partial(
        P.relSet, EGO_JUNTIONS, "isIn", edge_type="incoming"))), 0)
phi8_T_5 = Property(
    "Phi8_T_5",
    f"~ $[{T}][is_only_in_junction]",
    [("is_only_in_junction", IS_ONLY_IN_JUNCTION)])

# Property 8 - T=10

T = 20  # PARAMETER T at 2Hz
IS_ONLY_IN_JUNCTION = partial(P.eq, partial(P.size, partial(
    P.difference, EGO_ROADS, partial(
        P.relSet, EGO_JUNTIONS, "isIn", edge_type="incoming"))), 0)
phi8_T_10 = Property(
    "Phi8_T_10",
    f"~ $[{T}][is_only_in_junction]",
    [("is_only_in_junction", IS_ONLY_IN_JUNCTION)])

# Property 8 - T=15

T = 30  # PARAMETER T at 2Hz
IS_ONLY_IN_JUNCTION = partial(P.eq, partial(P.size, partial(
    P.difference, EGO_ROADS, partial(
        P.relSet, EGO_JUNTIONS, "isIn", edge_type="incoming"))), 0)
phi8_T_15 = Property(
    "Phi8_T_15",
    f"~ $[{T}][is_only_in_junction]",
    [("is_only_in_junction", IS_ONLY_IN_JUNCTION)])

# Property 9

phi9 = Property(
    "Phi9",
    # "G(are_stop_signs_for_ego -> (!(~are_stop_signs_for_ego) U ((is_stopped & !(~are_stop_signs_for_ego)) | G(!(~are_stop_signs_for_ego)))))",
    "G((~are_stop_signs_for_ego & X are_stop_signs_for_ego) -> (X(are_stop_signs_for_ego U (is_stopped | G(are_stop_signs_for_ego)))))",
    [("are_stop_signs_for_ego", ARE_STOP_SIGNS_FOR_EGO),
     ("is_stopped", IS_STOPPED)])


all_properties = [phi1, phi2, phi3, phi4_S_5, phi4_S_10, phi4_S_15, phi5, phi6, phi7_T_5, phi7_T_10, phi7_T_15,
                  phi8_T_5, phi8_T_10, phi8_T_15, phi9]
