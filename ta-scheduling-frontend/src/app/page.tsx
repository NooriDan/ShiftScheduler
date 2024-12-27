"use client";
import { TimetableProvider } from "@/context/app-context";
import { Timetable } from "@/models/domain";
import { useState } from "react";
import HomeContent from "./content";

export default function Home() {
  return (
    <TimetableProvider>
      <HomeContent />
    </TimetableProvider>
  );
}
