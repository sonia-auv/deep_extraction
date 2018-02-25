import argparse
import json
import os

class Main():
    """ Main application class. """

    def parse_args(self):
        """ Parse args passed on while calling the script. """

        args_parser = argparse.ArgumentParser()

        args_parser.add_argument('-f', '--json_file_path',
                                default=None,
                                required=True, 
                                help='Path to json file containing label data')

        args_parser.add_argument('-o', '--output_image_path',
                                default=None,
                                required=True, 
                                help='Path to destination directory where masked images are created')
        
        

        
        
        def main(self):
            """ Application main method. """
            self.parse_args()   

            
            
if __name__ == '__main__':
    main = Main()
    import IPython;IPython.embed()