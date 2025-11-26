"use client";

import { useState } from "react";
import { useMediaQuery } from "@/hooks/use-media-query";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { ShoppingCart } from "lucide-react";

export function CartDrawer() {
  const [open, setOpen] = useState(false);
  const isDesktop = useMediaQuery("(min-width: 768px)");

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button variant="outline">
            <ShoppingCart className="mr-2 h-4 w-4" />
            Carrito (0)
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Carrito de Compras</DialogTitle>
            <DialogDescription>
              Revisa los productos antes de proceder al pago
            </DialogDescription>
          </DialogHeader>
          <CartContent />
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cerrar</Button>
            </DialogClose>
            <Button>Proceder al Pago</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerTrigger asChild>
        <Button variant="outline" size="icon">
          <ShoppingCart className="h-4 w-4" />
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <div className="mx-auto w-full max-w-sm">
          <DrawerHeader>
            <DrawerTitle>Carrito de Compras</DrawerTitle>
            <DrawerDescription>
              Revisa los productos antes de proceder al pago
            </DrawerDescription>
          </DrawerHeader>
          <CartContent className="p-4 pb-0" />
          <DrawerFooter>
            <Button>Proceder al Pago</Button>
            <DrawerClose asChild>
              <Button variant="outline">Cerrar</Button>
            </DrawerClose>
          </DrawerFooter>
        </div>
      </DrawerContent>
    </Drawer>
  );
}

function CartContent({ className }: { className?: string }) {
  return (
    <div className={className}>
      {/* Lista de productos del carrito */}
      <p className="text-muted-foreground">Tu carrito está vacío</p>
    </div>
  );
}
