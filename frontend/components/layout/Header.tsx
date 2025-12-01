"use client";

import { useState } from "react";
import Link from "next/link";
import { useMediaQuery } from "@/hooks/use-media-query";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Menu } from "lucide-react";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export function Header() {
  const [open, setOpen] = useState(false);
  const isDesktop = useMediaQuery("(min-width: 768px)");

  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="text-xl font-bold">
          MemoryCard
        </Link>

        {isDesktop ? (
          <nav className="flex items-center gap-6">
            <Link href="/catalog" className="hover:text-primary">
              Catálogo
            </Link>
            <Link href="/cart" className="hover:text-primary">
              Carrito
            </Link>
            <Link href="/login" className="hover:text-primary">
              Login
            </Link>
            <ThemeToggle />
          </nav>
        ) : (
          // movil hamburger menu
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-6 w-6" />
                <span className="sr-only">Abrir menú</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right">
              <SheetHeader>
                <SheetTitle>Menú</SheetTitle>
                <SheetDescription>
                  Navega por las secciones de MemoryCard
                </SheetDescription>
              </SheetHeader>
              <nav className="mt-6 flex flex-col gap-4">
                <SheetClose asChild>
                  <Link href="/catalog" className="text-lg hover:text-primary">
                    Catálogo
                  </Link>
                </SheetClose>
                <SheetClose asChild>
                  <Link href="/cart" className="text-lg hover:text-primary">
                    Carrito
                  </Link>
                </SheetClose>
                <SheetClose asChild>
                  <Link href="/login" className="text-lg hover:text-primary">
                    Login
                  </Link>
                </SheetClose>
                <div className="flex items-center gap-2 pt-4 border-t">
                  <span className="text-sm text-muted-foreground">Tema:</span>
                  <ThemeToggle />
                </div>
              </nav>
            </SheetContent>
          </Sheet>
        )}
      </div>
    </header>
  );
}
