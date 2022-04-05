import logging
import os
import sys
from sleeputils import Defaults

logger = logging.getLogger(__name__)


class _Defaults(Defaults):
    """
    Stores and potentially updates default values for sleep stages etc.
    """
    # Default hyperparameters path (relative to project dir)
    HPARAMS_DIR = 'hyperparameters'
    HPARAMS_NAME = 'hparams.yaml'
    PRE_PROCESSED_HPARAMS_NAME = 'pre_proc_hparams.yaml'
    DATASET_CONF_DIR = "dataset_configurations"
    PRE_PROCESSED_DATA_CONF_DIR = "preprocessed"

    # Global RNG seed
    GLOBAL_SEED = None

    # Log dir usually set on run time by utime.bin.ut entry script
    PACKAGE_NAME = __name__.split(".")[0]
    PACKAGE_LEVEL_LOGGERS = []  # Populated in init_package_level_loggers
    LOG_DIR = None

    @classmethod
    def get_logging_path(cls, log_file_name=None, log_dir=None):
        if log_dir and cls.LOG_DIR is None:
            return None
        else:
            return os.path.join(log_dir or cls.LOG_DIR, log_file_name or "")

    @classmethod
    def init_package_level_loggers(cls,
                                   level,
                                   package_names=None,
                                   format='%(levelname)s | %(asctime)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
                                   datefmt="%Y/%m/%d %H:%M:%S",
                                   stream=sys.stdout):
        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter(format, datefmt=datefmt)
        handler.setFormatter(formatter)
        # Set handler and log level on all passed package-level loggers or on the utime packe logger only by default
        cls.PACKAGE_LEVEL_LOGGERS = []
        for package_logger in map(logging.getLogger, package_names or [cls.PACKAGE_NAME]):
            package_logger.setLevel(level)
            package_logger.addHandler(handler)
            cls.PACKAGE_LEVEL_LOGGERS.append(package_logger)

    @classmethod
    def set_logging_file_handler(cls, file_name, loggers=None, mode="w", log_dir=None, overwrite_existing=False):
        if loggers is None:
            loggers = cls.PACKAGE_LEVEL_LOGGERS or [logging.getLogger(cls.PACKAGE_NAME)]
        path = cls.get_logging_path(file_name, log_dir)
        if os.path.exists(path):
            if overwrite_existing:
                os.remove(path)
            elif "a" not in mode:
                raise OSError(f"Logging path {path} already exists and 'overwrite_existing' argument is set False. "
                              f"If using the utime scripts, set the --overwrite flag to overwrite.")
        if path is None:
            raise ValueError("Attribute 'LOG_DIR' on Defaults object has not yet been set.")
        folder = os.path.split(path)[0]
        if not os.path.exists(folder):
            global logger
            logger.info(f"Creating logging directory at path: {folder}")
            os.makedirs(folder)
        top_level_logger = logging.getLogger(cls.PACKAGE_NAME)
        file_handler = logging.FileHandler(path, mode=mode)
        file_handler.setLevel(top_level_logger.level)
        file_handler.setFormatter(top_level_logger.handlers[0].formatter)
        for passed_logger in loggers:
            passed_logger.addHandler(file_handler)

    @classmethod
    def set_global_seed(cls, seed):
        import tensorflow as tf
        import numpy as np
        import random
        cls.GLOBAL_SEED = int(seed)
        logger.info(f"Seeding TensorFlow, numpy and random modules with seed: {cls.GLOBAL_SEED}")
        tf.random.set_seed(cls.GLOBAL_SEED)
        np.random.seed(cls.GLOBAL_SEED)
        random.seed(cls.GLOBAL_SEED)

    @classmethod
    def get_hparams_dir(cls, project_dir):
        return os.path.join(project_dir, cls.HPARAMS_DIR)

    @classmethod
    def get_hparams_path(cls, project_dir):
        return os.path.join(project_dir, cls.HPARAMS_DIR, cls.HPARAMS_NAME)

    @classmethod
    def get_pre_processed_hparams_path(cls, project_dir):
        return os.path.join(project_dir, cls.HPARAMS_DIR,
                            cls.PRE_PROCESSED_HPARAMS_NAME)

    @classmethod
    def get_dataset_configurations_dir(cls, project_dir):
        return os.path.join(cls.get_hparams_dir(project_dir),
                            cls.DATASET_CONF_DIR)

    @classmethod
    def get_pre_processed_data_configurations_dir(cls, project_dir):
        return os.path.join(cls.get_dataset_configurations_dir(project_dir),
                            cls.PRE_PROCESSED_DATA_CONF_DIR)
