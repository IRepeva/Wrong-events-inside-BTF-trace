from wrong_events_search import wrong_events_search
from unittest import TestCase, main


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


class WrongEventsTesting(TestCase):
    def setUp(self):
        self.fake_writer = FakeWriter()

    def test_simultaneous_start(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T1", "392", "activate"),
            ("45", "Core1", "0", "T", "T1", "392", "start"),
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('45', 4, 'Parallel active tasks')])

    def test_simultaneous_start_resume(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "preempt"),
            ("45", "Core1", "0", "T", "T2", "391", "resume"),
            ("46", "Core1", "0", "T", "T1", "392", "activate"),
            ("47", "Core1", "0", "T", "T1", "392", "start"),
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('47', 6, 'Parallel active tasks')])

    def test_wrong_order1(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "392", "activate")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('44', 3, 'Wrong order of events')])

    def test_wrong_order2(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "preempt"),
            ("45", "Core1", "0", "T", "T2", "392", "terminate")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('45', 4, 'Wrong order of events')])

    def test_first_preempt(self):
        fake_reader = FakeReader([
            ("43", "Core1", "0", "T", "T2", "391", "preempt")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('43', 1, 'Wrong order of events. First action is not "activate"')])

    def test_empty_lines_and_comments_with_correct_data(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("#"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            (),
            ("44", "Core1", "0", "T", "T2", "391", "terminate")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertFalse(self.fake_writer.result)

    def test_empty_lines_and_comments_with_incorrect_data(self):
        fake_reader = FakeReader([
            ("#"),
            ("43", "Core1", "0", "T", "T2", "391", "activate"),
            (),
            ("#"),
            ("44", "Core1", "0", "T", "T2", "391", "terminate")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('44', 5, 'Wrong order of events')])

    def test_process_termination(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "terminate"),
            ("45", "Core1", "0", "T", "T2", "381", "activate"),
            ("46", "Core1", "0", "T", "T2", "381", "start")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertFalse(self.fake_writer.result)

    def test_process_preempt(self):
        fake_reader = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "preempt"),
            ("45", "Core1", "0", "T", "T1", "381", "activate"),
            ("46", "Core1", "0", "T", "T1", "381", "start")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertFalse(self.fake_writer.result)

    def test_incorrect_event(self):
        fake_reader = FakeReader([
            ("48", "Core1", "0", "T", "T2", "391", "active")
        ])
        wrong_events_search(fake_reader, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('48', 1, 'Unknown event: "active"')])

if __name__ == '__main__':
    main()
