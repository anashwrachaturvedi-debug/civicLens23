import { useEffect, useRef } from "react";
import { FaTimes } from "react-icons/fa";

const sizes = {
  sm: "max-w-sm",
  md: "max-w-lg",
  lg: "max-w-3xl",
  xl: "max-w-5xl",
};

const FOCUSABLE =
  'button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  showCloseButton = true,
  showFooter = false,
  footer,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  className = "",
}) => {
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    document.body.style.overflow = "hidden";
    closeButtonRef.current?.focus();

    const handleKeyDown = (e) => {
      if (e.key === "Escape" && closeOnEscape) {
        onClose?.();
        return;
      }

      if (e.key !== "Tab") return;

      const elements = modalRef.current?.querySelectorAll(FOCUSABLE);
      if (!elements?.length) return;

      const first = elements[0];
      const last = elements[elements.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else if (document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, closeOnEscape, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={closeOnOverlayClick ? onClose : undefined}
    >
      <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity duration-300" />

      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
        className={`relative w-full ${
          sizes[size] || sizes.md
        } max-h-[90vh] overflow-hidden rounded-2xl border border-white/20 bg-white/80 shadow-2xl backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/90 animate-in zoom-in-95 fade-in duration-300 ${className}`}
      >
        <header className="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h2
            id="modal-title"
            className="text-xl font-semibold text-slate-900 dark:text-white"
          >
            {title}
          </h2>

          {showCloseButton && (
            <button
              ref={closeButtonRef}
              type="button"
              onClick={onClose}
              aria-label="Close modal"
              className="rounded-lg p-2 text-slate-500 transition-all duration-200 hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
            >
              <FaTimes />
            </button>
          )}
        </header>

        <main className="max-h-[calc(90vh-140px)] overflow-y-auto px-6 py-5 text-slate-700 dark:text-slate-300">
          {children}
        </main>

        {showFooter && (
          <footer className="border-t border-slate-200 px-6 py-4 dark:border-slate-700">
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
};

export default Modal;