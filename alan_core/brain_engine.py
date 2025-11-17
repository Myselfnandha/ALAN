class AlanBrain:
    def __init__(self):
        self.layers = []
        self.memory = {}

    def add_layer(self, name, details):
        self.layers.append({ "name": name, "details": details })

    def get_layers(self):
        return self.layers
