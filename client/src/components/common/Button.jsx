import React from 'react';
import { cn } from '../../utils/cn';

export const Button = React.forwardRef(({
  children,
  className,
  variant = 'primary',
  size = 'md',
  disabled = false,
  isLoading = false,
  icon: Icon,
  iconPosition = 'left',
  ...props
}, ref) => {
  const baseStyles = "inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed select-none rounded-lg active:scale-[0.98]";

  const variants = {
    primary: "bg-scientific-600 text-white hover:bg-scientific-700 focus:ring-scientific-500 shadow-sm shadow-scientific-500/20",
    secondary: "bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 hover:border-slate-400 focus:ring-slate-300 shadow-sm",
    outline: "border border-scientific-600 text-scientific-600 hover:bg-scientific-50 focus:ring-scientific-400",
    ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus:ring-slate-200",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm",
    accent: "bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500 shadow-sm",
  };

  const sizes = {
    sm: "text-xs px-2.5 py-1.5 gap-1.5",
    md: "text-sm px-4 py-2 gap-2",
    lg: "text-base px-5 py-2.5 gap-2.5",
  };

  return (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1.5" />
      ) : Icon && iconPosition === 'left' ? (
        <Icon className={size === 'sm' ? "w-3.5 h-3.5" : "w-4 h-4"} />
      ) : null}
      {children}
      {!isLoading && Icon && iconPosition === 'right' && (
        <Icon className={size === 'sm' ? "w-3.5 h-3.5" : "w-4 h-4"} />
      )}
    </button>
  );
});

Button.displayName = 'Button';

