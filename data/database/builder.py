

def main():
    from data.database.schema import Base, engine
    from data.database.migrations import migration_1
    Base.metadata.create_all(bind=engine)
    migration_1()


if __name__== '__main__':
    main()