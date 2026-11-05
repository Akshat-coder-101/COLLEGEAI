import React from 'react';
import { cn } from '../../utils/cn';

export const Card = ({
  children,
  className,
  hoverable = false,
  highlight = false,
  ...props
}) => {
  return (
    <div
      className={cn(
        "bg-white border rounded-xl shadow-sm transition-all duration-200",
        highlight ? "border-scientific-300 ring-1 ring-scientific-100" : "border-slate-200/90",
        hoverable && "hover:border-slate-300 hover:shadow-md cursor-pointer",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className, ...props }) => (
  <div className={cn("px-6 py-4 border-b border-slate-100 flex items-center justify-between", className)} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ children, className, ...props }) => (
  <h3 className={cn("text-base font-semibold text-slate-900 tracking-tight", className)} {...props}>
    {children}
  </h3>
);

export const CardDescription = ({ children, className, ...props }) => (
  <p className={cn("text-xs text-slate-500 mt-0.5", className)} {...props}>
    {children}
  </p>
);

export const CardContent = ({ children, className, ...props }) => (
  <div className={cn("p-6", className)} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ children, className, ...props }) => (
  <div className={cn("px-6 py-3.5 bg-slate-50/50 border-t border-slate-100 rounded-b-xl flex items-center justify-between", className)} {...props}>
    {children}
  </div>
);

