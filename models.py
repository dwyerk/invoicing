import yaml

class Company(yaml.YAMLObject):
    yaml_tag = '!company'
    def __init__(self, name, address, phone, rate):
        self.name = name
        self.address = address
        self.phone = phone
        self.rate = rate

class Payer(yaml.YAMLObject):
    yaml_tag = '!payer'
    def __init__(self, name, address, phone):
        self.name = name
        self.address = address
        self.phone = phone
