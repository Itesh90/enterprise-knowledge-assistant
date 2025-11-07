import React from 'react';
import clsx from 'clsx';

type Props = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, Props>(function Input({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={clsx(
        'h-10 w-full rounded-xl border-2 border-purple-200 bg-gradient-to-r from-white to-purple-50 px-4 py-2 text-sm text-black outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-300 shadow-md hover:shadow-lg',
        className,
      )}
      {...props}
    />
  );
});


