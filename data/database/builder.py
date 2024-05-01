def main():
    from schema import Base, engine
    Base.metadata.create_all(bind=engine)

if __name__== '__main__':
    main()