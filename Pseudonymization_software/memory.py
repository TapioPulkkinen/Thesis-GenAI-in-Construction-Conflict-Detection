

class RunTimeMemory:
    needs_ocr = []
    org_file_paths = []
    log_file_errors = {}  # {path: error_message}
    pseudo_file_paths = []
    file_data = {}  # {path: [data]}
    found_entities = []  # [{'UID': text+entity_type, 'word': text, 'entity_type': entity_type, 'ner_method': ner_method, 'score':score, 'replacement': replacement}]


    def get_memory_values(self, name_of_variable):
        if not name_of_variable or not isinstance(name_of_variable, str):
            raise ValueError("Not name for variable or variable wasn't string!")
        try:
            value = getattr(self, name_of_variable)
            return value
        except AttributeError:
            raise ValueError(f"Variable named '{name_of_variable}' does not exist in the class")

    def clear_memory(self):
        self.needs_ocr = []
        self.org_file_paths = []
        self.pseudo_file_paths = []

        self.log_file_errors = {}
        self.file_data = {}
