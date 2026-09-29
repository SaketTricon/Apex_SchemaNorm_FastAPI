import csv
from random import Random
from typing import TextIO


class SampleFileError(ValueError):
    pass


def sample_csv_records(
    csv_file: TextIO,
    sample_size: int,
) -> list[dict[str, str | None]]:
    if sample_size < 1:
        raise ValueError("sample_size must be at least 1")

    random = Random()
    samples: list[tuple[int, dict[str, str | None]]] = []
    record_count = 0

    try:
        reader = csv.DictReader(csv_file, strict=True)
        headers = reader.fieldnames
        if not headers or any(not header.strip() for header in headers):
            raise SampleFileError("CSV must include non-empty column headers")
        if len(set(headers)) != len(headers):
            raise SampleFileError("CSV column headers must be unique")

        for row in reader:
            if None in row:
                raise SampleFileError("CSV row has more values than its header")

            sample = {header: row[header] for header in headers}
            if record_count < sample_size:
                samples.append((record_count, sample))
            else:
                replacement_index = random.randrange(record_count + 1)
                if replacement_index < sample_size:
                    samples[replacement_index] = (record_count, sample)
            record_count += 1
    except csv.Error as error:
        raise SampleFileError("CSV is malformed") from error

    if record_count == 0:
        raise SampleFileError("CSV must contain at least one data row")

    return [sample for _, sample in sorted(samples)]