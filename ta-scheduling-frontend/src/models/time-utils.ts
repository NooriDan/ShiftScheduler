
export function convertEuropeanToAmericanTime(time: string) {
    const hour = parseInt(time.split(":")[0])
    const minute = parseInt(time.split(":")[1])

    return `${hour > 12 ? hour - 12 : hour}:${minute} ${hour >= 12 ? "PM" : "AM"}`
}