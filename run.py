from CTPU import app, setHeaders, createWebook

if __name__ == '__main__':
    header = setHeaders()
    webhook = createWebook(header)
    app.run()
