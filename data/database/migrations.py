from data.database.controller import TickDataController
from data.feeder.feeder import Feeder
from data.database.settings import pair
def migration_1():
    ticks = Feeder().get_most(pair)
    controller = TickDataController()
    controller.add_ticks(ticks)