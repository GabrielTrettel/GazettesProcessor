from gazette import Gazette


class GazetteProcessor():
    def __init__(self, config_path:str):
        self.config_path = config_path
        self.gazettes = None
        pass


    def parse_config(self):
        """parse_config
           Parses config file into class attrs
        """
        # TODO: parse config file
        pass


    def generate_gazettes(self):
        """ generate_gazettes
            returns a generator object of Gazette objects
        """
        # TODO: generate_gazettes
        pass


    def  dump_gazettes_as_csv(self):
       """ dump_gazettes_as_csv
       dump all Gazette fields in a csv file
       """
       # TODO: dump_gazettes_as_csv
       pass
