from . import db


def list_items() -> None:
    rows = db.get_item_list()
    # print("\t".join(["ID", "Annotation Count", "File"]))
    for row in rows:
        # print(f"{ row['id'] }\t{ row['annotationCount'] }\t\"{ row['filename'] }\"")
        print(f"{ row['key'] }\t{ row['value'] }\t\"{ row['key'] }\"")
