import React from "react";

const variants = {
  default:
    "border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-500",
  primary:
    "border-blue-200 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-500",
  success:
    "border-emerald-200 dark:border-emerald-700 hover:border-emerald-400 dark:hover:border-emerald-500",
  warning:
    "border-amber-200 dark:border-amber-700 hover:border-amber-400 dark:hover:border-amber-500",
  danger:
    "border-red-200 dark:border-red-700 hover:border-red-400 dark:hover:border-red-500",
  info:
    "border-sky-200 dark:border-sky-700 hover:border-sky-400 dark:hover:border-sky-500",
};

const iconColors = {
  default: "text-blue-600 dark:text-blue-400",
  primary: "text-blue-600 dark:text-blue-400",
  success: "text-emerald-600 dark:text-emerald-400",
  warning: "text-amber-600 dark:text-amber-400",
  danger: "text-red-600 dark:text-red-400",
  info: "text-sky-600 dark:text-sky-400",
};

const paddings = {
  none: "p-0",
  sm: "p-4",
  md: "p-6",
  lg: "p-8",
};

const shadows = {
  none: "",
  sm: "shadow-sm",
  md: "shadow-lg",
  lg: "shadow-2xl",
};

const radius = {
  md: "rounded-md",
  lg: "rounded-lg",
  xl: "rounded-xl",
  "2xl": "rounded-2xl",
};

const Card = ({
  title,
  subtitle,
  children,
  icon: Icon,
  headerAction,
  footer,
  variant = "default",
  padding = "md",
  hoverable = true,
  bordered = true,
  shadow = "md",
  rounded = "2xl",
  className = "",
}) => {
  const hasHeader = title || subtitle || Icon || headerAction;

  return (
    <article
      className={[
        "overflow-hidden bg-white/90 backdrop-blur-md dark:bg-slate-900/90 transition-all duration-300",
        bordered ? `border ${variants[variant] || variants.default}` : "",
        shadows[shadow] || shadows.md,
        radius[rounded] || radius["2xl"],
        hoverable
          ? "hover:-translate-y-1 hover:shadow-2xl"
          : "",
        className,
      ].join(" ")}
    >
      {hasHeader && (
        <>
          <header className="flex items-start justify-between gap-4 p-6">
            <div className="flex items-start gap-4 min-w-0">
              {Icon && (
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 ${
                    iconColors[variant] || iconColors.default
                  }`}
                >
                  <Icon className="text-xl" />
                </div>
              )}

              <div className="min-w-0">
                {title && (
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                    {title}
                  </h3>
                )}

                {subtitle && (
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>

            {headerAction && (
              <div className="shrink-0">{headerAction}</div>
            )}
          </header>

          <div className="border-t border-slate-200 dark:border-slate-700" />
        </>
      )}

      <section
        className={`${paddings[padding] || paddings.md} text-slate-700 dark:text-slate-300`}
      >
        {children}
      </section>

      {footer && (
        <>
          <div className="border-t border-slate-200 dark:border-slate-700" />
          <footer className="p-6">{footer}</footer>
        </>
      )}
    </article>
  );
};

export default Card;