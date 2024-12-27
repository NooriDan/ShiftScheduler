import SchedulerGrid from "@/components/scheduler-grid";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col p-4">
      <div className="">
        <div className="text-xl font-bold">TA Management</div>
        <div>Add Shift</div>
        <div>Add TAs</div>


      </div>
      <SchedulerGrid />
    </div>
  );
}
