import logging
from logging.handlers import RotatingFileHandler
from time import sleep

import uvicorn
import threading
import colorlog

import os

from fast_api.git_version import __git_version__
from langchain_core.globals import set_verbose, set_debug
from langchain_core.tracers.stdout import ConsoleCallbackHandler

from llm.common import get_current_llm, LLMInitializationError

from fast_api.api_server import api_server
from config.config_ui import config_ui_app
from config.config_ui import config
from skillberry_agent_lib.skillberry_store import skillberry_store

# Initialize logger
logger = logging.getLogger(__name__)


# MCP tools implementation loaded directly in api_server
logger.info("Using MCP tools implementation")


debug = config.get("advanced__debug")
otel_logging = config.get("advanced__otel_logging")
invoke_config = None

log_level = logging.INFO
if debug is True:
    log_level = logging.DEBUG
    set_debug(True)
    set_verbose(True)
    invoke_config = {'callbacks': [ConsoleCallbackHandler()]}

    if otel_logging is True:
        # Initialize logging with agent_analytics_sdk
        from agent_analytics.instrumentation import agent_analytics_sdk
        from agent_analytics.instrumentation.configs import OTLPCollectorConfig

        print("otel_logging mode enabled")
        agent_analytics_sdk.initialize_logging(
            tracer_type=agent_analytics_sdk.SUPPORTED_TRACER_TYPES.REMOTE,
            config=OTLPCollectorConfig(endpoint="http://localhost:4318/v1/traces"),
            # logs_dir_path="/tmp/",
            # log_filename="tools-agent",
        )

    print("Debug mode enabled")
else:
    set_debug(False)
    set_verbose(False)
    invoke_config = None

log_file = config.get("advanced__log_file")


# Define log format for colors (Console)
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
)

# Define log format for file (No colors)
file_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d] %(message)s"
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10)
file_handler.setFormatter(file_formatter)

# Configure logger
logging.basicConfig(level=log_level, handlers=[console_handler, file_handler])


def run_config_ui():
    config_ui_app.run(debug=True, use_reloader=False, host="0.0.0.0", port=7001)


def _stay_in_config_only_mode(reason: str):
    logger.error(reason)
    logger.error("Configuration UI is available.")
    logger.error("Update the configuration, then restart the agent.")
    while True:
        sleep(100000)


def main():

    # Run the configuration UI
    config_ui_thread = threading.Thread(target=run_config_ui, daemon=True)
    config_ui_thread.start()

    logger.info("Configuration UI is available.")

    # make sure we can communicate with the LLM
    try:
        current_llm = get_current_llm(refresh=True)
        current_llm.check_llm_communication()
    except LLMInitializationError as e:
        _stay_in_config_only_mode(e.user_message)
    except Exception:
        _stay_in_config_only_mode(
            "Can't communicate with the LLM. Please check model/provider configuration, network, VPN, and access keys."
        )

    # make sure we can communicate with the Skillberry API
    try:
        skillberry_store_communication = skillberry_store.check_communication()
    except Exception:
        skillberry_store_communication = False

    if not skillberry_store_communication:
        _stay_in_config_only_mode(
            "Can't communicate with the Skillberry Store service. Please check network, VPN, access keys, and service availability."
        )

    # emit the git version
    logging.info(f"skillberry-tools-agent version {__git_version__} is running.")

    # Run the API server
    uvicorn.run(api_server, host="0.0.0.0", port=7000)


if __name__ == "__main__":
    main()
