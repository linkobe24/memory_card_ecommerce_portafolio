import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ShoppingCart } from "lucide-react";

export default function CatalogPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-8 text-3xl font-bold md:text-4xl">
        Catálogo de Juegos
      </h1>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Card key={i} className="flex flex-col">
            <CardHeader>
              <div className="aspect-video w-full rounded-md bg-muted" />
              <CardTitle className="mt-4">The Witcher 3</CardTitle>
              <CardDescription>
                RPG de mundo abierto con historia epica
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <div className="flex gap-2">
                <Badge variant="secondary">RPG</Badge>
                <Badge variant="secondary">PS4</Badge>
              </div>
            </CardContent>
            <CardFooter className="flex items-center justify-between">
              <span className="text-lg font-bold">$59.99</span>
              <Button className="md:min-w-[120px]">
                <ShoppingCart className="mr-2 h-4 w-4 md:mr-0" />
                <span className="hidden md:inline">Agregar</span>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
