
import { TimetableProvider } from "@/context/app-context";
import HomeContent from "./content";

export default function Home() {
  return (
    <TimetableProvider>
      <HomeContent />
    </TimetableProvider>
  );
}
