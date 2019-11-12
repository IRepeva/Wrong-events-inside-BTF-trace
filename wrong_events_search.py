import csv


def wrong_events_search(csv_reader, csv_writer):
    event_order_dict = {
        "activate": {"start"},
        "start": {"terminate", "preempt"},
        "preempt": {"resume"},
        "resume": {"terminate"},
        "terminate": {"activate"}
    }

    num_active_process = 0  # Number of active processes
    previous_event = {}
    for line in csv_reader:
        if not line or line[0].startswith("#"):
            continue

        timestamp, element, event = line[0], line[4], line[6]

        # Check if event is acceptable
        if event not in event_order_dict:
            csv_writer.writerow((timestamp, reader.line_num, 'Unknown event: "%s"' % event))
            continue

        previous_element_event = previous_event.get(element)

        # Check first element event
        if previous_element_event is None:
            if event != "activate":
                csv_writer.writerow((timestamp, reader.line_num, 'Wrong order of events. First action is not "activate"'))
            previous_event[element] = event
            continue

        # Calculate active process number
        if event == "terminate" or event == "preempt":
            num_active_process -= 1
        elif event == "start" or event == "resume":
            num_active_process += 1

        # Check a single process is active
        if num_active_process > 1:
            csv_writer.writerow((timestamp, reader.line_num, 'Parallel active tasks'))

        # Check correct order of events for current element
        if event not in event_order_dict[previous_element_event]:
            csv_writer.writerow((timestamp, reader.line_num, 'Wrong order of events'))

        previous_event[element] = event


if __name__ == '__main__':
    input_btf_file_path = "luxoft_btf_task/Demo_Exercise_Trace.btf"
    result_file_path = "result_file_funcs.csv"
    with open(input_btf_file_path) as src, open(result_file_path, "w") as dst:
        reader = csv.reader(src, delimiter=',')
        writer = csv.writer(dst, delimiter=',')
        writer.writerow(('# TimeStamp', 'Line number in BTF trace', 'Comment'))
        wrong_events_search(reader, writer)
