import { CardFooter } from "@/components/ui";
import { ReactNode } from "react";

interface GameCardFooterProps {
  children: ReactNode;
  className?: string;
}

export function GameCardFooter({
  children,
  className = "",
}: GameCardFooterProps) {
  return (
    <CardFooter
      className={`px-3 py-2 flex items-center justify-between ${className}`}
    >
      {children}
    </CardFooter>
  );
}
