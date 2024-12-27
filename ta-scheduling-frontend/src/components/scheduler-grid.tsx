

const times: number[] = []

// Edit this for when to start and when to end
for (let i = 8; i <= 20; i++) {
    times.push(i)
}

export const time_strings = times.map((time) => `${time == 12 ? 12 : time % 12}:30 ${time / 12 < 1 ? "AM" : "PM"}`)

function BlockDivider({ row, time }: { row: number, time: number }) {
    return (
        <>
            <div className={`col-start-1 row-start-${row} flex flex-row`}>
                <div>
                    {time == 12 ? 12 : time % 12}:30 {time / 12 < 1 ? "AM" : "PM"}
                </div>
                <hr />
            </div>
            <div className={`col-start-2 col-span-5 row-start-${row} flex flex-col`}>
                <div className="flex-1"></div>
                <hr className="bg-black h-1" />
                <div className="flex-1"></div>
            </div>
        </>
    )
}

function Block({ row, col }: { row: number, col: number }) {
    return (
        <div className={`col-start-${col} col-span-1 row-start-${row} h-10`}>
        </div>
    )
}

function Header() {
    return (
        <>
            <div className="col-start-1 row-start-1">Time</div>
            <div className="col-start-2 row-start-1">Monday</div>
            <div className="col-start-3 row-start-1">Tuesday</div>
            <div className="col-start-4 row-start-1">Wednesday</div>
            <div className="col-start-5 row-start-1">Thursday</div>
            <div className="col-start-6 row-start-1">Friday</div></>
    )
}

function BlockRow({ index, time }: { index: number, time: number }) {
    return (
        <>
            <BlockDivider row={2 * index + 2} time={time} />
            {
                index < times.length - 1 &&
                <>
                    <Block row={2 * index + 3} col={2} />
                    <Block row={2 * index + 3} col={3} />
                    <Block row={2 * index + 3} col={4} />
                    <Block row={2 * index + 3} col={5} />
                    <Block row={2 * index + 3} col={6} />
                </>
            }</>
    )
}

export default function SchedulerGrid() {
    return (<div className="grid grid-cols-6 bg-gray-300">
        <Header />
        {
            times.map((time, index, arr) => <BlockRow key={index} index={index} time={time} />)
        }
    </div>)
}