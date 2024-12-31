
export function convertEuropeanToAmericanTime(time: string) {
    const hour = parseInt(time.split(":")[0])
    const minute = parseInt(time.split(":")[1])

    return `${hour > 12 ? hour - 12 : hour}:${minute} ${hour >= 12 ? "PM" : "AM"}`
}

export function compareTimes(time1: string, time2: string) {
    const hour1 = parseInt(time1.split(":")[0])
    const minute1 = parseInt(time1.split(":")[1])

    const hour2 = parseInt(time2.split(":")[0])
    const minute2 = parseInt(time2.split(":")[1])

    if (hour1 > hour2) {
        return 1
    } else if (hour1 < hour2) {
        return -1
    } else {
        if (minute1 > minute2) {
            return 1
        } else if (minute1 < minute2) {
            return -1
        } else {
            return 0
        }
    }
}