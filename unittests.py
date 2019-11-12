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
        self.fake_reader_parallel_start = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T1", "392", "activate"),
            ("45", "Core1", "0", "T", "T1", "392", "start"),
        ])
        self.fake_reader_parallel_start_resume = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "preempt"),
            ("45", "Core1", "0", "T", "T2", "391", "resume"),
            ("46", "Core1", "0", "T", "T1", "392", "activate"),
            ("47", "Core1", "0", "T", "T1", "392", "start"),
        ])
        self.fake_reader_wrong_order1 = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "392", "activate")
        ])
        self.fake_reader_wrong_order2 = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            ("44", "Core1", "0", "T", "T2", "391", "preempt"),
            ("45", "Core1", "0", "T", "T2", "392", "terminate")
        ])
        self.fake_reader_first_event_start = FakeReader([
            ("43", "Core1", "0", "T", "T2", "391", "start")
        ])
        self.fake_reader_first_event_preempt = FakeReader([
            ("43", "Core1", "0", "T", "T2", "391", "preempt")
        ])
        self.fake_reader_special_lines_correct_data = FakeReader([
            ("42", "Core1", "0", "T", "T2", "391", "activate"),
            ("#"),
            ("43", "Core1", "0", "T", "T2", "391", "start"),
            (),
            ("44", "Core1", "0", "T", "T2", "391", "terminate")
        ])
        self.fake_reader_special_lines_incorrect_data = FakeReader([
            ("#"),
            ("43", "Core1", "0", "T", "T2", "391", "activate"),
            (),
            ("#"),
            ("44", "Core1", "0", "T", "T2", "391", "terminate")
        ])

    def test_simultaneous_start(self):
        wrong_events_search(self.fake_reader_parallel_start, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('45', 4, 'Parallel active tasks')])

    def test_simultaneous_start_resume(self):
        wrong_events_search(self.fake_reader_parallel_start_resume, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('47', 6, 'Parallel active tasks')])

    def test_wrong_order1(self):
        wrong_events_search(self.fake_reader_wrong_order1, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('44', 3, 'Wrong order of events')])

    def test_wrong_order2(self):
        wrong_events_search(self.fake_reader_wrong_order2, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('45', 4, 'Wrong order of events')])

    def test_first_start(self):
        wrong_events_search(self.fake_reader_first_event_start, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('43', 1, 'Wrong order of events. First action is not "activate"')])

    def test_first_preempt(self):
        wrong_events_search(self.fake_reader_first_event_preempt, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('43', 1, 'Wrong order of events. First action is not "activate"')])

    def test_empty_lines_and_comments_with_correct_data(self):
        res = wrong_events_search(self.fake_reader_special_lines_correct_data, self.fake_writer)
        self.assertIsNone(res)

    def test_empty_lines_and_comments_with_incorrect_data(self):
        wrong_events_search(self.fake_reader_special_lines_incorrect_data, self.fake_writer)
        self.assertEqual(self.fake_writer.result, [('44', 5, 'Wrong order of events')])


if __name__ == '__main__':
    main()
