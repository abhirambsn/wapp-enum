import importlib
import inspect

class ScriptParser:
    def __init__(self, name, path, seq=None):
        self.name = name
        self.path = '.'.join(path.split('/'))
        self.module = importlib.import_module(self.path)
        self.function_signature = ','.join(inspect.signature(self.module.run).parameters.keys())
        self.arg_count = len(inspect.signature(self.module.run).parameters.keys())
        self.param_dict = {}
        self.sequence = seq

    def generate_function_params(self):
        for i in self.function_signature.split(','):
            self.param_dict[i] = None

    def run(self, **kwargs):
        self.generate_function_params() # Generating Function Parameter Dictionary
        for i in kwargs:
            if i in self.param_dict:
                self.param_dict[i] = kwargs[i]
        return self.module.run(**self.param_dict)
    
    def help(self):
        return help(self.module.run)
    
    def __repr__(self) -> str:
        return f"<ScriptParserObject name='{self.name}' path='{self.path}' run_sig='{self.function_signature}' arg_count={self.arg_count}>"