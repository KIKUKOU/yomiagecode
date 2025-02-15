#!/usr/bin/env python3
"""
The functions for get and set configs.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(config_file_name: str = './data/config.yaml') -> dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_file_name (str): The name of the configuration file. Defaults to './data/config.yaml'.

    Returns:
        dict[str, Any]: A dictionary containing the configuration.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with Path(config_file_name).open('r', encoding='utf-8') as f:
            configs = yaml.safe_load(f)
    except FileNotFoundError:
        logging.exception('Configuration file "%s" not found.', config_file_name)
        raise
    except yaml.YAMLError:
        logging.exception('Error parsing YAML file "%s"', config_file_name)
        raise

    return configs


def save_config(configs: dict[str, Any], config_file_name: str = './data/config.yaml') -> None:
    """
    Load configuration from a YAML file.

    Args:
        configs (dict): config辞書
        config_file_name (str): The name of the configuration file. Defaults to './data/config.yaml'.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with Path(config_file_name).open('r', encoding='utf-8') as f:
            yaml.safe_dump(configs, f)
    except FileNotFoundError:
        logging.exception('Configuration file "%s" not found.', config_file_name)
        raise
    except yaml.YAMLError:
        logging.exception('Error parsing YAML file "%s"', config_file_name)
        raise


def set_config_value(configs: dict[str, Any], update_key: str, update_value: Any) -> dict[str, Any]:  # noqa: ANN401
    # NOTE: configごとに格納する値の型が違うのでAnyを許容する.
    """
    configファイルに値を書込む.

    Args:
        configs (dict): config辞書
        update_key (str): 更新するconfigの要素
        update_value (Any): 更新するconfigの値

    Returns:
        dict[str, Any]: 更新されたconfig辞書
    """
    configs.update(zip(update_key, update_value, strict=True))
    return configs
