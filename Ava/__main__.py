import logging

from Ava.ava import Ava as Ava_class


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    ava = Ava_class()
    ava.load_from_file()

    print(ava.dump())
    ava.run()


if  __name__ == "__main__":
    main()
