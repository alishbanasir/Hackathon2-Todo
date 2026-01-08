import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center rounded-md font-semibold tracking-tight transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none";

    const variantStyles = {
      primary:
        "bg-white text-black hover:bg-neutral-200 active:bg-neutral-300 shadow-sm",
      secondary:
        "bg-neutral-900 text-white border border-neutral-700 hover:bg-neutral-800 hover:border-neutral-600 active:bg-neutral-700",
      danger:
        "bg-red-600 text-white hover:bg-red-500 active:bg-red-700 shadow-sm",
      ghost:
        "bg-transparent text-neutral-300 hover:bg-neutral-900 hover:text-white active:bg-neutral-800 border border-transparent hover:border-neutral-800",
    };

    const sizeStyles = {
      sm: "px-3 py-1.5 text-sm h-8",
      md: "px-4 py-2 text-sm h-10",
      lg: "px-6 py-2.5 text-base h-12",
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
