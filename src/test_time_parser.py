import unittest
from datetime import date, time
from utils.time_parser import parse_event_time, EventTime

class TestTimeParser(unittest.TestCase):

    def setUp(self):
        self.today = date(2023, 3, 9)

    def test_no_date_no_time(self):
        text = "Blah blah blah some event at some time"
        expected = EventTime(None, None, None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_single_time(self):
        text = "Starts at 2pm."
        expected = EventTime(None, time(14, 0), None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_time_range(self):
        text = "From 8am-4pm."
        expected = EventTime(None, time(8, 0), None, time(16, 0))
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_time_range_alternate(self):
        text = "From 1-4pm."
        expected = EventTime(None, time(13, 0), None, time(16, 0))
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_special_time(self):
        text = "Noon on 3/17."
        expected = EventTime(date(2023, 3, 17), time(12, 0), None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_single_date(self):
        text = "It's on March 17."
        expected = EventTime(date(2023, 3, 17), None, None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_date_and_single_time(self):
        text = "Swing by on 3/17 at 4pm."
        expected = EventTime(date(2023, 3, 17), time(16, 0), None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_date_and_time_range(self):
        text = "It's 8am-4pm on March 17."
        expected = EventTime(date(2023, 3, 17), time(8, 0), date(2023, 3, 17), time(16, 0))
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_date_and_special_time(self):
        text = "We'll start at noon, 17 Mar."
        expected = EventTime(date(2023, 3, 17), time(12, 0), None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

    def test_next_matching_date(self):
        text = "Be there on Jan 1."
        expected = EventTime(date(2024, 1, 1), None, None, None)
        actual = parse_event_time(text, today=self.today)
        self.assertEqual(expected.start_date, actual.start_date)
        self.assertEqual(expected.start_time, actual.start_time)
        self.assertEqual(expected.end_date, actual.end_date)
        self.assertEqual(expected.end_time, actual.end_time)

if __name__ == '__main__':
    unittest.main()