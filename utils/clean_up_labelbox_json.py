from __future__ import division

import json
import argparse


def parse_args():
    """ Parse args passed on while calling the script. """

    args_parser = argparse.ArgumentParser()

    args_parser.add_argument('-f', '--json_file_path',
                             default=None,
                             dest='json_file_path',
                             type=str,
                             required=True,
                             help='Path to json file containing label data')

    return args_parser.parse_args()


def get_stats_from_json_file(json_file_path):
    with open(json_file_path, 'r') as json_file:
        correct_images = []
        data = json.load(json_file)

        correct = 0
        error = 0
        skipped = 0
        total = 0

        for image in data:
            correct_img = True
            labels = image['Label']
            total += 1
            if labels != 'Skip':
                for k, v in labels.iteritems():
                    if v[0]:
                        points = v[0]
                        if len(points) == 4:
                            correct += 1
                        else:
                            error += 1
                            correct_img = False
                    else:
                        error += 1
                        correct_img = False
                        # continue
            else:
                correct_img = False
                skipped += 1

            if correct_img == True:
                correct_images.append(image)

        correct_total = correct / total
        error_total = error / total
        skipped_total = skipped / total
        print('Correct:{}%'.format(correct_total))
        print('Error:{}'.format(error_total))
        print('Skipped:{}'.format(skipped_total))

        with open('correct.json', 'w') as json_file:
            json.dump(correct_images, json_file)

        with open('correct.json', 'r') as data_file:
            correct_data = json.load(data_file)

        import IPython
        IPython.embed()


if __name__ == '__main__':
    parsed_args = parse_args()
    get_stats_from_json_file(parsed_args.json_file_path)
