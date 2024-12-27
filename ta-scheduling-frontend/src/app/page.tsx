import Image from "next/image";

export default function Home() {
  const times = []

  for (let i = 8; i <= 20; i++) {
    times.push(i)
  }


  return (
    <div className="flex flex-1 flex-col p-4">
      <div className="">
        <div className="text-xl font-bold">TA Management</div>
        <div>Add Shift</div>
        <div>Add TAs</div>


      </div>
      <div className="grid grid-cols-6">
        <div className="col-start-2 row-start-1">Monday</div>
        <div className="col-start-3 row-start-1">Tuesday</div>
        <div className="col-start-4 row-start-1">Wednesday</div>
        <div className="col-start-5 row-start-1">Thursday</div>
        <div className="col-start-6 row-start-1">Friday</div>
        {
          times.map((time, index, arr) =>
            <>
              <div className={`col-start-1 row-start-${2 * index + 2}`}>{time == 12 ? 12 : time % 12}:30 {time / 12 < 1 ? "AM" : "PM"}</div>
              <div className={`col-start-2 col-span-5 row-start-${2 * index + 2} flex flex-col`}>
                <div className="flex-1"></div>
                <hr className="bg-black h-1" />
                <div className="flex-1"></div>
              </div>
              {
                index < arr.length - 1 &&
                <>
                  <div className={`col-start-1 row-start-${2 * index + 3}`}>-</div>
                  <div className={`col-start-2 row-start-${2 * index + 3}`}>-</div>
                  <div className={`col-start-3 row-start-${2 * index + 3}`}>-</div>
                  <div className={`col-start-4 row-start-${2 * index + 3}`}>-</div>
                  <div className={`col-start-5 row-start-${2 * index + 3}`}>-</div>
                </>}
            </>
          )
        }
      </div>
    </div>
  );
}
