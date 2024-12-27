
export function to_time_string(date: Date) {
    return `${date.getHours() == 12 ? 12: date.getHours()}:${date.getMinutes()} ${date.getHours() < 12 ? "AM" : "PM"}`
}