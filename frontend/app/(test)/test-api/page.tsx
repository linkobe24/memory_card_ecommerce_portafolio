"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";

export default function TestAPIPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["backend-health"],
    queryFn: () => apiClient.get("/"),
    enabled: false, // no ejectua automaticamente
  });

  return (
    <>
      <Button onClick={() => refetch()}>test</Button>
      {isLoading && <p>loading...</p>}
      {error && <p>Error: {(error as Error).message}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </>
  );
}
