import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { CartDrawer } from "@/components/shop/CartDrawer";

export default function TestComponentsPage() {
  return (
    <div className="container mx-auto p-8">
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Card Component</CardTitle>
            <CardDescription>Descripción del card</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Contenido del card con componentes de shadcn/ui</p>
          </CardContent>
          <CardFooter>
            <Button>Acción</Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Inputs y Badges</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Email" />
            <div className="flex gap-2">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="destructive">Destructive</Badge>
            </div>
          </CardContent>
        </Card>
        <CartDrawer />
      </div>
    </div>
  );
}
