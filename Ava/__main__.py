import logging

from Ava import (
    config
)

from Ava.ava import Ava as Ava_class


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG if config.DEBUG else logging.INFO)

    ava = Ava_class()
    ava.load_from_file()

    logger.info("%s", ava)
    ava.run()

if  __name__ == "__main__":
    main()