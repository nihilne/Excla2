import logging

from colorama import Fore

log = logging.getLogger(__name__)


async def setup_custom_format():
    formatter = logging.Formatter(
        "{0}[%(asctime)s] {1}[%(levelname)s] {2}%(name)s {3}- %(message)s".format(
            Fore.GREEN,
            Fore.BLUE,
            Fore.MAGENTA,
            Fore.RESET,
        ),
        "%d-%m-%Y %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    log.info("Custom logging format set up.")
