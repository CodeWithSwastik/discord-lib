class Action:
    def __init__(self, action_config, namespace = None):
        self.action_config = action_config
        self.setup()
        self.namespace = namespace

    def setup(self):
        for config in self.action_config:
            setattr(self, config, self.action_config[config])
    
    def execute(self):

        if self.type == "log": 
            print(self.action_eval(self.value))
        elif self.type == "conditional":
            if eval(self.condition):
                print("test")
                return self.action_eval(self.true)
            else:
                return self.action_eval(self.false)
        elif self.type == "store":
            setattr(self.namespace,self.action_eval(self.name),self.action_eval(self.data))
        elif self.type == "multi":
            for action_config in self.value:
                self.action_eval(action_config)

    def action_eval(self,f):
        if isinstance(f, dict):
            return Action(f, namespace=self.namespace).execute()
        else:
            return f