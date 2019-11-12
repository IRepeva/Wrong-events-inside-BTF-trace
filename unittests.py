from wrong_events_search import wrong_events_search


class FakeReader(object):

    def __init__(self, data):
        self.data = data
        self.line_num = 0

    def __iter__(self):
        for i, item in enumerate(self.data, 1):
            self.line_num = i
            yield item


class FakeWriter(object):

    def __init__(self):
        self.result = []

    def writerow(self, row):
        self.result.append(row)


fake_reader = FakeReader([
    ("396712855", "Core1", "0", "T", "T1", "390", "activate"),
    ("396712855", "Core1", "0", "T", "T1", "390", "start"),
    ("398630825", "Core1", "0", "T", "T1", "390", "terminate"),
    ("399988816", "Core1", "0", "T", "T2", "391", "activate"),
    ("399988816", "Core1", "0", "T", "T2", "391", "start"),
    ("401712855", "Core1", "0", "T", "T1", "392", "activate"),
    ("401712855", "Core1", "0", "T", "T1", "392", "start"),
])

fake_writer = FakeWriter()

wrong_events_search(fake_reader, fake_writer)
print(fake_writer.result)
