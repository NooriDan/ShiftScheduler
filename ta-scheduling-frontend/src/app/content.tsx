import SchedulerGrid from "@/components/scheduler-grid";
import { useTimetableContext } from "@/context/app-context";
import { Shift, TA } from "@/models/domain";

function ShiftDisplay({ shift }: { shift: Shift }) {
    return <div>{shift.id}</div>
}

function TADisplay({ ta }: { ta: TA }) {
    return <div>{ta.id}</div>
}

export default function HomeContent() {
    //const { timetable, setTimetable } = useTimetableContext()

    return (<div className="flex flex-1 flex-col p-4">
        <div className="">
            <div className="text-xl font-bold">TA Management</div>
            <div>
                {/*
                <div>Shifts</div>
                <div>
                    {timetable.shifts.map(shift => <ShiftDisplay key={shift.id} shift={shift} />)}
                </div>
                <div>TAs</div>
                <div>
                    {timetable.tas.map(ta => <TADisplay key={ta.id} ta={ta} />)}
                </div>*/}
            </div>
            <div>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400">Add Shift</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400">Add TAs</button>
                <button className="p-2 m-2 bg-blue-300 rounded-xl hover:bg-blue-400">Generate Schedule</button>
            </div>

        </div>
        <SchedulerGrid />
    </div>)
}