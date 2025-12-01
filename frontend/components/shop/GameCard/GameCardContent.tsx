"use client";

import { CardContent } from "@/components/ui";
import { ReactNode } from "react";

interface GameCardContentProps {
  children: ReactNode;
  className?: string;
}

export function GameCardContent({
  children,
  className = "",
}: GameCardContentProps) {
  return (
    <CardContent className={`p-3 space-y-1.5 ${className}`}>
      {children}
    </CardContent>
  );
}
