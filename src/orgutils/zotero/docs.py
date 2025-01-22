from . import db


def list_docs() -> None:
    rows = db.get_doc_list()
    print("\t".join(["ID", "Annotation Count", "File"]))
    for row in rows:
        print(f"{ row['id'] }\t{ row['annotationCount'] }\t\"{ row['filename'] }\"")
