def truncate_patch_id(patch_id: str) -> str:
    parts = patch_id.split(".")
    return f"{parts[0]}.{parts[1]}"
