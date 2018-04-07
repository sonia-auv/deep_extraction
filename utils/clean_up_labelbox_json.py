from __future__ import division

import json
import argparse


def parse_args():
    """ Parse args passed on while calling the script. """

    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('-i', '--input_json_file',
                             default=None,
                             dest='input_json_file',
                             type=str,
                             required=True,
                             help='Path to json file containing raw label data')

    args_parser.add_argument('-o', '--output_json_file',
                             default=None,
                             dest='output_json_file',
                             type=str,
                             required=True,
                             help='Path to output json file containing screened label data')

    return args_parser.parse_args()


def get_stats_from_json_file(input_json_file, output_json_file):
    with open(input_json_file, 'r') as json_file:
        parsed_json = []
        json_data = json.load(json_file)

        for entry in json_data:
            labels = entry['Label']
            if labels != 'Skip':
                for label_name, points in labels.iteritems():
                    points = points[0]
                    xy_coords = []
                    remove_label = []
                    for point in points:
                        xy_coords.extend([point['x'], point['y']])

                    if len(xy_coords) < 8 or len(xy_coords) > 8:
                        remove_label.append(label_name)
                    else:

                        top_left_x = xy_coords[0]
                        top_left_y = xy_coords[1]

                        bottom_left_x = xy_coords[2]
                        bottom_left_y = xy_coords[3]

                        bottom_right_x = xy_coords[4]
                        bottom_right_y = xy_coords[5]

                        top_right_x = xy_coords[6]
                        top_right_y = xy_coords[7]

                        left_x = top_left_x == bottom_left_x
                        right_x = top_right_x == bottom_right_x
                        top_y = top_left_y == top_right_y
                        bottom_y = bottom_left_y == bottom_right_y

                        print(left_x, right_x, top_y, bottom_y)
                        if not all([left_x, right_x, top_y, bottom_y]):
                            remove_label.append(label_name)

                for label in remove_label:
                    entry['Label'].pop(label)

                parsed_json.append(entry)

        with open(output_json_file, 'w') as new_json_file:
            json.dump(parsed_json, new_json_file)


if __name__ == '__main__':
    parsed_args = parse_args()
    input_json_file = parsed_args.input_json_file
    output_json_file = parsed_args.output_json_file
    get_stats_from_json_file(input_json_file, output_json_file)
