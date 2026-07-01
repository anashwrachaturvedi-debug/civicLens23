import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { HiOutlineCloudUpload, HiOutlineX, HiOutlineExclamationCircle } from "react-icons/hi";

const MAX_SIZE = 5 * 1024 * 1024;

export default function ImageUploader({ image, setImage, onImageChange }) {
  const [error, setError] = useState("");

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      setError("");

      if (rejectedFiles?.length) {
        const reason = rejectedFiles[0].errors[0]?.code;
        if (reason === "file-too-large") {
          setError("File size must be under 5MB.");
        } else if (reason === "file-invalid-type") {
          setError("Only JPG, JPEG, and PNG files are allowed.");
        } else {
          setError("This file could not be uploaded.");
        }
        return;
      }

      const file = acceptedFiles[0];
      if (!file) return;

      const preview = URL.createObjectURL(file);
      setImage({ file, preview });
      onImageChange?.(file);
    },
    [setImage, onImageChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/jpeg": [], "image/jpg": [], "image/png": [] },
    maxSize: MAX_SIZE,
    multiple: false,
  });

  function handleRemove(event) {
    event.stopPropagation();
    if (image?.preview) URL.revokeObjectURL(image.preview);
    setImage(null);
    setError("");
  }

  return (
    <div className="flex flex-col gap-3">
      <div
        {...getRootProps()}
        role="button"
        tabIndex={0}
        aria-label="Upload an image"
        className={`relative flex min-h-[180px] cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-8 text-center transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          isDragActive
            ? "border-blue-400 bg-blue-50/50 dark:bg-blue-500/10"
            : "border-slate-300 bg-slate-50/50 hover:border-blue-400 dark:border-slate-700 dark:bg-slate-900/40"
        }`}
      >
        <input {...getInputProps()} />
        {image ? (
          <div className="relative w-full">
            <img
              src={image.preview}
              alt="Selected upload preview"
              className="mx-auto max-h-48 rounded-lg object-cover shadow-sm"
            />
            <button
              type="button"
              onClick={handleRemove}
              aria-label="Remove image"
              className="absolute right-2 top-2 rounded-full bg-slate-900/70 p-1.5 text-white hover:bg-slate-900"
            >
              <HiOutlineX size={16} />
            </button>
          </div>
        ) : (
          <>
            <HiOutlineCloudUpload size={36} className="text-blue-500" />
            <span className="text-sm font-medium">Drag & drop a photo, or click to browse</span>
            <span className="text-xs text-slate-400">JPG, JPEG, or PNG, up to 5MB</span>
          </>
        )}
      </div>
      {error && (
        <p className="flex items-center gap-2 text-sm text-red-500" role="alert">
          <HiOutlineExclamationCircle /> {error}
        </p>
      )}
    </div>
  );
}