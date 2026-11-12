import { useCallback, useEffect, useState } from "react";

// Loads data when the page opens or when `deps` change.
// Returns { data, loading, error, reload }. Old data stays visible while reloading.
export function useFetch(fetcher, deps = []) {
  const [tick, setTick] = useState(0);
  const [result, setResult] = useState({ key: null, data: null, error: "" });
  const key = `${JSON.stringify(deps)}:${tick}`;

  useEffect(() => {
    let cancelled = false;
    fetcher()
      .then((data) => !cancelled && setResult({ key, data, error: "" }))
      .catch((err) => !cancelled && setResult({ key, data: null, error: err.message }));
    return () => {
      cancelled = true; // ignore answers that arrive after the page changed
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  const loading = result.key !== key;
  return { data: result.data, loading, error: loading ? "" : result.error, reload };
}