import os
from functools import cached_property
from typing import Any, Dict

import yaml


class ConfigParserUtils:
    def __init__(
        self, path: str = os.path.join(os.path.dirname(__file__), "service_config.yaml")
    ):
        self._path, self._config = path, None

    def _init_config(self, path: str):
        with open(path, "r") as rf:
            self._config = yaml.safe_load(rf)
        return self._config

    @cached_property
    def config(self):
        self._init_config(self._path)
        return self._config

    def get_section(self, name) -> Dict:
        return self.config.get(name, {})

    def get_subsection(self, section_name: str, sub_section_name: str) -> Any:
        return self.get_section(section_name)[sub_section_name]


cp = ConfigParserUtils()
