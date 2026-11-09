import logging

from colorama import Fore

log = logging.getLogger(__name__)


async def setup_custom_logging_format():
    formatter = logging.Formatter(
        f"{Fore.GREEN}[%(asctime)s] {Fore.BLUE}[%(levelname)s] {Fore.MAGENTA}%(name)s {Fore.RESET}- %(message)s",
        "%d-%m-%Y %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    log.info("Custom logging format set up.")
