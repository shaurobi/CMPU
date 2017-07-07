from CTPU import app, createWebook, setHeaders

if __name__ == '__main__':
    header = setHeaders()
    createWebook(header)
    app.run()
