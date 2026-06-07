import { useContext } from "react";
import { ConsumerSessionContext } from "../context/ConsumerSessionContext.jsx";

export default function useConsumerSession() {
  const ctx = useContext(ConsumerSessionContext);
  if (!ctx) throw new Error("useConsumerSession must be used within ConsumerSessionProvider");
  return ctx;
}
