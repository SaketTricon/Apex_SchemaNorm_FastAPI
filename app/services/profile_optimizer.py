
import json


def optimize_profile_json(profile_json):
    aliases = {
        "column_name": "cn",
        "inferred_data_type": "dt",
        "semantic_type": "sem",
        "nullable": "nb",
        "statistics": "st",
        "sample_values": "sv",
        "null_count": "nc",
        "null_percentage": "np",
        "distinct_count": "dc",
        "distinct_percentage": "dp",
        "key_analysis": "ka",
        "candidate_primary_key": "cpk",
        "patterns": "pt",
    }

    if isinstance(profile_json, str):
        profile_json = json.loads(profile_json)

    def optimize(obj):
        if isinstance(obj, dict):
            result = {}

            for key, value in obj.items():
                new_key = aliases.get(key, key)

                if new_key in result:
                    raise ValueError(f"Key collision: {new_key}")

                result[new_key] = optimize(value)

            return result

        if isinstance(obj, list):
            return [optimize(item) for item in obj]

        return obj

    return json.dumps(
        optimize(profile_json),
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
