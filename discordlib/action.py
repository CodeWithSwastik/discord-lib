import re
import random

class Action:
    def __init__(self, action_config, namespace=None):
        self.action_config = action_config
        self.namespace = namespace
        self.setup()

    def setup(self):
        matcher = re.compile(r"(?:\{\{)([a-zA-Z0-9\.]+)(?:\}\})")
        replacer = "{0.\\1}"

        for config in self.action_config:
            config_data = self.action_config[config]
            if isinstance(config_data, str):
                config_data = matcher.sub(replacer, config_data).format(self.namespace)
            setattr(self, config, config_data)

    def execute(self):

        if self.type == "log":
            print(self.action_eval(self.value))
        elif self.type == "conditional":
            if eval(self.condition):
                return self.action_eval(self.true)
            else:
                return self.action_eval(self.false)
        elif self.type == "store":
            setattr(
                self.namespace, self.action_eval(self.name), self.action_eval(self.data)
            )
        elif self.type == "multi":
            for action_config in self.value:
                self.action_eval(action_config)
        elif self.type == "math":
            return eval(self.action_eval(self.value))
        elif self.type == "random":
            if hasattr(self,"choice"):
                return random.choice(self.choice)
            elif hasattr(self,"range"):
                return random.randint(int(self.range[0]), int(self.range[1]))



    def action_eval(self, f):
        if isinstance(f, dict):
            return Action(f, namespace=self.namespace).execute()
        else:
            return f
