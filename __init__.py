"""
app/uploads/__init__.py

Package initializer for CivicLens AI's file-upload module.

This package encapsulates everything related to handling user-submitted
files (e.g. issue-report photos, AI-detection images): validation, storage,
naming, and error handling. Submodules are assumed to already exist and be
production-ready:

    app/uploads/exceptions.py   -> Upload-specific exception classes
    app/uploads/validators.py   -> File type/size/content validation
    app/uploads/storage.py      -> Persisting files to disk/object storage
    app/uploads/utils.py        -> Filename generation, path helpers

Re-exporting the public API here allows the rest of the codebase to import
concisely:

    from app.uploads import save_upload_file, validate_image_file, UploadError

instead of reaching into each submodule individually. Submodules remain
directly importable as well (e.g. `app.uploads.storage`).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #
from app.uploads.exceptions import (  # noqa: F401
    FileTooLargeError,
    InvalidFileTypeError,
    UploadError,
)

# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
from app.uploads.validators import (  # noqa: F401
    ALLOWED_IMAGE_CONTENT_TYPES,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES,
    validate_image_file,
    validate_upload_file,
)

# --------------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------------- #
from app.uploads.storage import (  # noqa: F401
    delete_upload_file,
    get_upload_file_url,
    save_upload_file,
)

# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #
from app.uploads.utils import (  # noqa: F401
    build_upload_path,
    generate_unique_filename,
    get_file_extension,
)

__all__ = [
    # exceptions
    "UploadError",
    "InvalidFileTypeError",
    "FileTooLargeError",
    # validators
    "validate_upload_file",
    "validate_image_file",
    "ALLOWED_IMAGE_EXTENSIONS",
    "ALLOWED_IMAGE_CONTENT_TYPES",
    "MAX_UPLOAD_SIZE_BYTES",
    # storage
    "save_upload_file",
    "delete_upload_file",
    "get_upload_file_url",
    # utils
    "generate_unique_filename",
    "get_file_extension",
    "build_upload_path",
]