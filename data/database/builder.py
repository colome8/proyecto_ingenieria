

def main():
    from schema import Base, engine
    Base.metadata.create_all(bind=engine)
    from data.feeder.feeder import Feeder
    from data.database.settings import pair
    f=Feeder()
    f.fast_feed_ticks_range(pair)

if __name__== '__main__':
    main()