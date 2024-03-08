import click

from src.prime.sequential import SequentialManager
from src.prime.parallel import ParallelManager
from src.util.logger import Logger


logger = Logger.get_logger(__name__)


@click.command()
@click.option('--mode',
              type=click.Choice(['sequential', 'parallel']),
              required=True,
              help='Mode to run')
@click.option('--until-number',
              type=click.INT,
              required=True,
              help='Until which number calculate the quantity of prime numbers')
@click.option('--workers',
              type=click.INT,
              default=1,
              help='How many workers to use on parallel mode')


def run(mode: str, until_number: int, workers: int) -> None:
    logger.info(f'Searching quantity of prime numbers until {until_number}')
    logger.info(f'Starting in {mode =}')
    if mode == 'sequential':
        SequentialManager.run(until_number)
        return
    ParallelManager.run(until_number, workers)


if __name__ == '__main__':
    run()